from telebot import TeleBot
from auth_token import token
import telebot
import telebot
from auth_token import token
from comands import telegram_bot


if __name__ == '__main__':
    bot = telegram_bot(token)

bot.polling()