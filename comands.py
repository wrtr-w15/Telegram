import telebot
import requests
import yfinance as yf
import matplotlib.pyplot as plt
import io
import schedule
import time
import sqlite3
import time
from telebot import types
from datetime import datetime
from auth_token import token
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from menu_options import menu_options, coin_options, dailyalert_options , time_options , back_options

def telegram_bot(token):
    bot = telebot.TeleBot(token)


    @bot.message_handler(commands=["start"])
    def handle_start(message):
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)  # Set row_width to 2

        # Create two rows of buttons
        row1_buttons = [telebot.types.InlineKeyboardButton(option, callback_data=option) for option in menu_options[:2]]
        row2_buttons = [telebot.types.InlineKeyboardButton(option, callback_data=option) for option in menu_options[2:]]

        markup.add(*row1_buttons)  # Add buttons from the first row
        markup.add(*row2_buttons)  # Add buttons from the second row

        bot.send_message(message.chat.id, "Welcome to Trading Alarm bot - a useful tool for every trader. Choose from the following commands:", reply_markup=markup)


    @bot.callback_query_handler(func=lambda call: call.data in menu_options)
    def handle_button_click(call):
        option = call.data
        if option == "Sell Price":
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)

            for coin_option in coin_options:
                button = telebot.types.InlineKeyboardButton(coin_option, callback_data=coin_option)
                markup.add(button)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Choose a coin:", reply_markup=markup)

        elif option == "Daily Alert":
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)

            for daily_alert_option in dailyalert_options:
                button = telebot.types.InlineKeyboardButton(daily_alert_option, callback_data=daily_alert_option)
                markup.add(button)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Choose a coin:", reply_markup=markup)
            pass

    def send_scheduled_message(time_option, chat_id, daily_alert_option):
        message = f"At {time_option}, you will receive a {daily_alert_option} notification from your bot!"
        bot.send_message(chat_id, message)

# Обработчик выбора варианта "Daily Alert"
    @bot.callback_query_handler(func=lambda call: call.data in dailyalert_options)
    def handle_daily_alert_option_click(call):
        daily_alert_option = call.data
        chat_id = call.message.chat.id

        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        row_buttons = [telebot.types.InlineKeyboardButton(time_option, callback_data=f"{daily_alert_option}:{time_option}") for time_option in time_options]

        for i in range(0, len(row_buttons), 2):
            markup.add(row_buttons[i], row_buttons[i+1] if i+1 < len(row_buttons) else None)

        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Choose a Time:", reply_markup=markup)

# Обработчик выбора времени
    @bot.callback_query_handler(func=lambda call: call.data in [f"{option}:{time_option}" for option in dailyalert_options for time_option in time_options])
    def handle_time_option_click(call):
        full_data = call.data.split(":")
        daily_alert_option = full_data[0]
        time_option = full_data[1]
        chat_id = call.message.chat.id
    
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        back_button = telebot.types.InlineKeyboardButton("Back", callback_data="Back")
        markup.add(back_button)
    
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"You selected: {daily_alert_option}, {time_option}\n\nChoose an option:", reply_markup=markup)



# Обработчик нажатия кнопки "Back"
    @bot.callback_query_handler(func=lambda call: call.data == "Back")
    def handle_button_click(call):
        if call.data == "Back":
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            handle_start(call.message)


    @bot.callback_query_handler(func=lambda call: call.data in coin_options)
    def handle_coin_option_click(call):
        coin_option = call.data
        if coin_option == "BTC Price":
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)
            time_frames = ["1 D", "5 D", "1 M", "3 M", "6 M", "1 Y"]

            for frame_option in time_frames:
                button = telebot.types.InlineKeyboardButton(frame_option, callback_data=frame_option)
                markup.add(button)

            try:
                req = requests.get("https://yobit.net/api/3/ticker/btc_usd")
                response = req.json()
                sell_price = response.get("btc_usd", {}).get("sell")

                if sell_price is not None:
                    message_text = f"Choose TimeFrame"
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text, reply_markup=markup)
                else:
                    bot.send_message(call.from_user.id, "BTC price data not available.")
            except Exception as ex:
                print(f"Error fetching BTC Price: {ex}")
                bot.send_message(call.from_user.id, "Error fetching BTC Price, please try again later")

    @bot.callback_query_handler(func=lambda call: call.data in ["1 D", "5 D", "1 M", "3 M", "6 M", "1 Y"])
    def handle_time_frame_click(call):
        time_frame = call.data
        try:
            # Retrieve historical price data for BTC using yfinance
            btc_data = yf.download("BTC-USD", period=time_frame, interval="1h")

            # Create a plot
            plt.figure(figsize=(10, 6))
            plt.plot(btc_data.index, btc_data["Close"], label="BTC Price")
            plt.xlabel("Date")
            plt.ylabel("Price (USD)")
            plt.title(f"Bitcoin (BTC) Price Chart ({time_frame} timeframe)")
            plt.legend()

            # Calculate price change
            price_change = btc_data["Close"][-1] - btc_data["Close"][0]

            # Convert the plot to an image
            image_stream = io.BytesIO()
            plt.savefig(image_stream, format="png")
            image_stream.seek(0)

            # Construct the table-like message
            message_text = (
                f"BTC Price: {btc_data['Close'][-1]:.2f}\n"
                f"Price Change: {price_change:.2f}\n\n"
                "```\n"
                "| Symbol |   Price   | Change |\n"
                "|--------|-----------|--------|\n"
                f"| BTC    | {btc_data['Close'][-1]:.2f}  | {price_change:.2f} |\n"
                "```"
            )

            # Send the image with the message to the user
            bot.send_photo(call.from_user.id, photo=image_stream, caption=message_text, parse_mode="Markdown")

            # Close the plot
            plt.close()
        except Exception as ex:
            print(f"Error creating BTC price chart: {ex}")
            bot.send_message(call.from_user.id, f"Error creating BTC price chart ({time_frame} timeframe), please try again later")

    bot.polling()

telegram_bot(token)
