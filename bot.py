import requests
from datetime import datetime
import telebot
from auth_token1 import token
from comands import telegram_bot

#BTC
def get_data():
    req = requests.get("https://yobit.net/api/3/ticker/btc_usd")
    response = req.json()
    sell_price = response["btc_usd"]["sell"]
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%H')}\nSell BTC price: {sell_price}")

#ETH
def get_data():
    req = requests.get("https://yobit.net/api/3/ticker/eth_usd")
    response = req.json()
    sell_price = response["eth_usd"]["sell"]
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%H')}\nSell ETH price: {sell_price}")
    

if __name__ == '__main__':
    telegram_bot(token)