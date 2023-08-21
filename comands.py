import telebot
import requests
from datetime import datetime
from auth_token import token

def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id,"Добро пожаловать ! Это Украинский телеграм бот крипто оповещений 223 ")

    
    @bot.message_handler(commands=["help"])
    def start_message(message):
        bot.send_message(message.chat.id,"Help with your problem")

    @bot.message_handler(content_types=["text"])
    def send_text(message):
        if message.text.lower() == "price":
            try:
                req = requests.get("https://yobit.net/api/3/ticker/btc_usd")
                response = req.json()
                sell_price = response["btc_usd"]["sell"]
                bot.send_message(message.chat.id,f"{datetime.now().strftime('%Y-%m-%d %H:%H')}\nSell BTC price: {sell_price}")
         
            except Exception as ex:
                print(ex)
                bot.send_message(message.chat.id,"Damn.....")

        else:
            bot.send_message(message.chat.id, "wrong comand")
    
    
    bot.polling()
