import telebot
import requests
import yfinance as yf
import matplotlib.pyplot as plt
import io
from datetime import datetime
from auth_token import token
from menu_options import menu_options, coin_options

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

    @bot.callback_query_handler(func=lambda call: call.data in coin_options)
    def handle_coin_option_click(call):
        coin_option = call.data
        if coin_option == "BTC Price":
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)
            time_frames = ["1d", "5d", "1mo", "3mo", "6mo", "1y"]

            for frame_option in time_frames:
                button = telebot.types.InlineKeyboardButton(frame_option, callback_data=frame_option)
                markup.add(button)

            try:
                req = requests.get("https://yobit.net/api/3/ticker/btc_usd")
                response = req.json()
                sell_price = response.get("btc_usd", {}).get("sell")

                if sell_price is not None:
                    message_text = f"BTC Price: {sell_price}"
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text, reply_markup=markup)
                else:
                    bot.send_message(call.from_user.id, "BTC price data not available.")
            except Exception as ex:
                print(f"Error fetching BTC Price: {ex}")
                bot.send_message(call.from_user.id, "Error fetching BTC Price, please try again later")

    @bot.callback_query_handler(func=lambda call: call.data in ["1d", "5d", "1mo", "3mo", "6mo", "1y"])
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
                "| Symbol | Price | Change |\n"
                "|--------|-------|--------|\n"
                f"| BTC    | {btc_data['Close'][-1]:.2f} | {price_change:.2f} |\n"
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
