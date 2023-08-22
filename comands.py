import telebot
import requests
from datetime import datetime
from auth_token import token

menu_options = [
    "ETH Price",
    "BTC Price",
    "Option 3"
]

def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def handle_start(message):
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)

        for option in menu_options:
            button = telebot.types.InlineKeyboardButton(option, callback_data=option)
            markup.add(button)

        bot.send_message(message.from_user.id, "Welcome to Trading Alarm bot - useful tool for every trader. Choose from the followign comands:", reply_markup=markup)
        
    #запрос ETH
    @bot.callback_query_handler(func=lambda call: True)
    def handle_button_click(call):
        option = call.data
        
        if option == "ETH Price":
            try:
                req = requests.get("https://yobit.net/api/3/ticker/eth_usd")
                response = req.json()
                sell_price = response["eth_usd"]["sell"]
                bot.send_message(call.from_user.id,f"{datetime.now().strftime('%Y-%m-%d %H:%H')}\nSell ETH price: {sell_price}")
         
            except Exception as ex:
                print(ex)
                bot.send_message(call.message.chat.id,"Can not collect information, try again later")

     
    

            
        if option == "BTC Price":
            try:
                req = requests.get("https://yobit.net/api/3/ticker/btc_usd")
                response = req.json()
                sell_price = response["btc_usd"]["sell"]
                bot.send_message(call.from_user.id,f"{datetime.now().strftime('%Y-%m-%d %H:%H')}\nSell BTC price: {sell_price}")
         
            except Exception as ex:
                print(ex)
                bot.send_message(call.from_user.id,"Can not collect information, try again later")

        #elif(option != "ETC Price"):
            #bot.send_message(call.message.chat.id, "wrong comand")

       
    

    #начало других команд

    #@bot.message_handler(content_types=["text"])
    #def send_text(message):
        #if message.text.lower() == "price":
            #try:
                #req = requests.get("https://yobit.net/api/3/ticker/btc_usd")
                #response = req.json()
                #sell_price = response["btc_usd"]["sell"]
               # bot.send_message(message.chat.id,f"{datetime.now().strftime('%Y-%m-%d %H:%H')}\nSell BTC price: {sell_price}")
         
           # except Exception as ex:
                #print(ex)
              #  bot.send_message(message.chat.id,"Can not collect information, try again later")

       # else:
            #bot.send_message(message.chat.id, "wrong comand")


        @bot.message_handler(commands=["help"])
        def start_message(message):
            bot.send_message(message.chat.id,"Help with your problem")
    
    
    bot.polling()