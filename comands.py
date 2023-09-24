import telebot
import requests
import yfinance as yf
import matplotlib.pyplot as plt
import io
import datetime
from threading import Thread
from telebot import types
from datetime import datetime
from auth_token import token
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Updater, CommandHandler
from menu_options import menu_options, coin_options, back_options

def telegram_bot(token):
    bot = telebot.TeleBot(token)


    # Start 
    @bot.message_handler(commands=["start"])
    def handle_start(message):
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)  # Set row_width to 2

        # Create two rows of buttons
        row1_buttons = [telebot.types.InlineKeyboardButton(option, callback_data=option) for option in menu_options[:2]]
        row2_buttons = [telebot.types.InlineKeyboardButton(option, callback_data=option) for option in menu_options[2:]]

        markup.add(*row1_buttons)  # Add buttons from the first row
        markup.add(*row2_buttons)  # Add buttons from the second row

        bot.send_message(message.chat.id, "Привет👋\n\n\nЯ, Treiding Alarm - бот, который поможет тебе отслеживать курс криптовалют, просматривать график цены и устанавливать оповещения при достижении монетой желаемой цены. \n\n\nДавай посмотрим, что там👇", reply_markup=markup)



    # Обработчик Главного Меню 
    @bot.callback_query_handler(func=lambda call: call.data in menu_options)
    def handle_button_click(call):
        option = call.data
        if option == "Sell Price":
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)

            for coin_option in coin_options:
                button = telebot.types.InlineKeyboardButton(coin_option, callback_data=coin_option)
                markup.add(button)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Choose a coin :", reply_markup=markup)
    
            pass


    # Обработчик нажатия кнопки "Back"
    @bot.callback_query_handler(func=lambda call: call.data == "Back")
    def handle_button_click(call):
        if call.data == "Back":
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            handle_start(call.message)
        


    #Coin price and graph
    @bot.callback_query_handler(func=lambda call: call.data in coin_options)
    def handle_coin_option_click(call):
        coin_option = call.data
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        time_frames = {"1 day": "1d", "5 days": "5d", "1 month": "1mo", "3 month": "3mo", "6 month": "6mo", "1 year": "1y"}

        for frame_option, frame_period in time_frames.items():
            button = telebot.types.InlineKeyboardButton(frame_option, callback_data=f"{coin_option}|{frame_period}")
            markup.add(button)

        try:
            message_text = f"Choose TimeFrame for {coin_option}"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text, reply_markup=markup)
        except Exception as ex:
            print(f"Error updating message: {ex}")
            bot.send_message(call.from_user.id, "Error updating message, please try again later")

    @bot.callback_query_handler(func=lambda call: "|" in call.data)
    def handle_time_frame_click(call):
        coin_option, frame_period = call.data.split("|")
        try:
            coin_data = yf.download(coin_option, period=frame_period, interval="1h")

            # Create a plot
            plt.figure(figsize=(10, 6))
            plt.plot(coin_data.index, coin_data["Close"], label=f"{coin_option} Price")
            plt.xlabel("Date")
            plt.ylabel("Price (USD)")
            plt.title(f"{coin_option} Price Chart ({frame_period} timeframe)")
            plt.legend()

            # Calculate price change
            price_change = coin_data["Close"][-1] - coin_data["Close"][0]

            # Convert the plot to an image
            image_stream = io.BytesIO()
            plt.savefig(image_stream, format="png")
            image_stream.seek(0)

            # Construct the table-like message
            message_text = (
                f"{coin_option} Price: {coin_data['Close'][-1]:.2f}\n"
                f"Price Change: {price_change:.2f}\n\n"
                "```\n"
                "| Symbol |   Price   | Change |\n"
                "|--------|-----------|--------|\n"
                f"| {coin_option} | {coin_data['Close'][-1]:.2f} | {price_change:.2f} |\n"
                "```"
            )

            # Send the image with the message to the user
            bot.send_photo(call.from_user.id, photo=image_stream, caption=message_text, parse_mode="Markdown")

            # Close the plot
            plt.close()
        except Exception as ex:
            print(f"Error creating {coin_option} price chart: {ex}")
            bot.send_message(call.from_user.id, f"Error creating {coin_option} price chart ({frame_period} timeframe), please try again later")

    bot.polling()

telegram_bot(token)
