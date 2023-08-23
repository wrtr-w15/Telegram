import requests
from datetime import datetime
import telebot
from auth_token import token
from comands import telegram_bot


if __name__ == '__main__':
    telegram_bot(token)