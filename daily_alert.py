import telebot
import requests
import yfinance as yf
import matplotlib.pyplot as plt
import io
import schedule
import time
import sqlite3
from telebot import types
from datetime import datetime
from auth_token import token
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from menu_options import menu_options, coin_options, dailyalert_options , time_options , back_options

def telegram_alert(token):
    bot = telebot.TeleBot(token)

    @bot.callback_query_handler(func=lambda call: call.data in dailyalert_options)
    def handle_daily_alert_option_click(call):
             daily_alert_option = call.data
             time_option = call.data
             if daily_alert_option == "BTC":
              markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        
              row_buttons = [telebot.types.InlineKeyboardButton(time_option, callback_data=time_option) for time_option in time_options]

              for i in range(0, len(row_buttons), 2):
                      markup.add(row_buttons[i], row_buttons[i+1] if i+1 < len(row_buttons) else None)

                      bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Choose a Time:", reply_markup=markup)
              time.sleep(1)
              now = datetime.now() 
              current_time = now.strftime("%H:%M")
              bot.callback_query_handler(func=lambda call: call.data in coin_options)
           
              
             if current_time == time_option:
              print('pass')
              bot.send_message(call.from_user.id, "Error fetching BTC Price, please try again later")
             else : 
                 pass