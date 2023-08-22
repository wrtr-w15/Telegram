import telebot
import requests
from datetime import datetime
from auth_token import token

menu_options = [
    "Sell Price",
    "Coin Alert",
    "Daily Alert"
]

coin_options = [
    "BTC Price",
    "ETH Price"
]

def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def handle_start(message):
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)

        for option in menu_options:
            button = telebot.types.InlineKeyboardButton(option, callback_data=option)
            markup.add(button)

        bot.send_message(message.from_user.id, "Welcome to Trading Alarm bot - a useful tool for every trader. Choose from the following commands:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data in menu_options)
    def handle_button_click(call):
        option = call.data
        if option == "Sell Price":
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)

            for coin_option in coin_options:
                button = telebot.types.InlineKeyboardButton(coin_option, callback_data=coin_option)
                markup.add(button)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Choose a coin:", reply_markup=markup)
        elif option == "Coin Alert":
            # Logic for Coin Alert
            pass
        elif option == "Daily Alert":
            # Logic for Daily Alert
            pass

    @bot.callback_query_handler(func=lambda call: call.data in coin_options)
    def handle_coin_option_click(call):
        coin_option = call.data
        if coin_option == "BTC Price":
            try:
                req = requests.get("https://yobit.net/api/3/ticker/btc_usd")
                response = req.json()
                sell_price = response.get("btc_usd", {}).get("sell")
                if sell_price is not None:
                    bot.send_message(call.from_user.id, f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\nSell BTC price: {sell_price}")
                else:
                    bot.send_message(call.from_user.id, "BTC price data not available.")
            except Exception as ex:
                print(f"Error fetching BTC Price: {ex}")
                bot.send_message(call.from_user.id, "Error fetching BTC Price, please try again later")
        elif coin_option == "ETH Price":
            try:
                req = requests.get("https://yobit.net/api/3/ticker/eth_usd")
                response = req.json()
                sell_price = response.get("eth_usd", {}).get("sell")
                if sell_price is not None:
                    bot.send_message(call.from_user.id, f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\nSell ETH price: {sell_price}")
                else:
                    bot.send_message(call.from_user.id, "ETH price data not available.")
            except Exception as ex:
                print(f"Error fetching ETH Price: {ex}")
                bot.send_message(call.from_user.id, "Error fetching ETH Price, please try again later")

    @bot.message_handler(commands=["help"])
    def start_message(message):
        bot.send_message(message.chat.id, "Help with your problem")

    bot.polling()

telegram_bot(token)