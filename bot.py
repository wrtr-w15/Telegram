import requests
from datetime import datetime
import telebot
from auth_token import token

def get_data():
    req = requests.get("https://yobit.net/api/3/ticker/btc_usd")
    response = req.json()
    sell_price = response["btc_usd"]["sell"]
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%H')}\nSell BTC price: {sell_price}")

def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id,"Добро пожаловать ! Это Украинский телеграм бот крипто оповещений!")
    
    bot.polling()
    


if __name__ == '__main__':
    telegram_bot(token)