import telebot
import requests
import yfinance as yf
import matplotlib.pyplot as plt
import io
import datetime
import time
import threading
from threading import Thread
from telebot import types
from datetime import datetime
from auth_token import token
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Updater, CommandHandler
from menu_options import menu_options, coin_options, dailyalert_options , time_options , back_options, coin_alert_options, alert_options


def telegram_bot(token):
    bot = telebot.TeleBot(token)
    coin_manual_alert = None

    # Запуск планировщика,+ в отдельном потоке (нужно для daily alert)
    scheduler = BackgroundScheduler()
    def run_scheduler():
        scheduler.start()
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.start()

    # Обработчик Команды Start 
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
        if option == "🪙Sell Price":
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)

            for coin_option in coin_options:
                button = telebot.types.InlineKeyboardButton(coin_option, callback_data=coin_option)
                markup.add(button)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Choose a coin :", reply_markup=markup)

        elif option == "🛎Daily Alert":
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)

            for daily_alert_option in dailyalert_options:
                button = telebot.types.InlineKeyboardButton(daily_alert_option, callback_data=daily_alert_option)
                markup.add(button)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберете название криптовалюты!💰\n\nДля возврата в главное меню \n\nВыберете Back 📃", reply_markup=markup)
            pass
        elif option == "⏰Coin Alert":
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)

            for alert_option in alert_options:
                button = telebot.types.InlineKeyboardButton(alert_option, callback_data=alert_option)
                markup.add(button)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Choose a coin alert:", reply_markup=markup)
            
        elif option == "🔧Help":
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)
            for back_option in back_options:
                button = telebot.types.InlineKeyboardButton(back_option, callback_data=back_option)
                markup.add(button)
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                   text="⚙️Help⚙️\n\n➡️Sell Price:\nНажми на интересующую монету\nи ты увидишь её актуальную цену\nграфик изменения цены за нужный период времени.\n\n\n➡️Daily ALert:\nПри выборе монеты ты можешь указать цену\nпри достижении которой я буду оповещать тебя.\n\n\n➡️Coin Alert:\nПри выборе монеты ты можешь выбрать время\nв которое я буду оповещать тебя о её текущей цене.\n\n\n➡️Conversion:\nТут вы можете узнать курс обмена криптовалют\n\n\n\n➡️ Для возврата в главное меню\nВыберете Back 📃", 
                                   reply_markup=markup)
            
            pass

    # Обработчик выбора варианта "Daily Alert"
    @bot.callback_query_handler(func=lambda call: call.data in dailyalert_options)
    def handle_daily_alert_option_click(call):
        daily_alert_option = call.data
        chat_id = call.message.chat.id
        if daily_alert_option == "Back":
            handle_button_click(call)
            return
        else:pass

        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        row_buttons = [telebot.types.InlineKeyboardButton(time_option, callback_data=f"{daily_alert_option}:{time_option}") for time_option in time_options]

        for i in range(0, len(row_buttons), 2):
            markup.add(row_buttons[i], row_buttons[i+1] if i+1 < len(row_buttons) else None)

        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Выберете время ⏰\n\nВ это время вы получите уведомление!💰\n\nДля возврата в главное меню \n\nВыберете Back 📃", reply_markup=markup)

        # Запланировать задачу на отправку сообщения в выбранное время
        for time_option in time_options:
            hour, minute = map(int, time_option.split('-'))
            scheduler.add_job(
                send_scheduled_message,
                trigger=CronTrigger(hour=hour, minute=minute),
                args=(time_option, chat_id, daily_alert_option),
            )

    coin_alert_options = {}
    notified_users = {}

    
    @bot.callback_query_handler(func=lambda call: call.data =="Manual")
    def coin_alert_manual_input_callback(call):
        global coin_manual_alert
        chat_id = call.message.chat.id
        user_id = call.from_user.id
        bot.send_message(chat_id, "Введите желаемую монеты\n\nнапример, btc:")
        bot.register_next_step_handler(call.message, coin_alert_manual_callback)
        
    def coin_alert_manual_callback(message):
        global coin_manual_alert
        coin_manual_alert = message.text.strip()
        coin_manual_alert = coin_manual_alert.lower()
        chat_id = message.chat.id
        user_id = message.from_user.id
        bot.send_message(chat_id, "Введите желаемую цену для монеты\n\nнапример, 30000:")
        bot.register_next_step_handler(message, set_desired_price)
     

    def set_desired_price(message):
        global coin_manual_alert
        chat_id = message.chat.id
        user_id = message.from_user.id
        desired_price = message.text.strip()

        try:
            desired_price = float(desired_price)

        # Сохранение желаемой цены для пользователя
            coin_alert_options[user_id] = desired_price

            bot.send_message(chat_id, f"Вы будете уведомлены, когда цена достигнет {desired_price}$")
        except ValueError:
            bot.send_message(chat_id, "Пожалуйста, введите числовое значение цены\n\nнапример, 30000.")

    def check_price():
        global coin_manual_alert
        
        while True:
            
            for user_id, desired_price in coin_alert_options.items():
                url = f"https://yobit.net/api/3/ticker/{coin_manual_alert}_usdt"  
                try:
                    req = requests.get(url)
                    req.raise_for_status()  # Проверка статуса запроса

                    response = req.json()
                    price = response.get(f"{coin_manual_alert}_usdt", {}).get("sell")

                    if price is not None and isinstance(price, (int, float)):
                        if abs(price - desired_price) < 0.0001:
                            if user_id not in notified_users or not notified_users[user_id]:
                                message_text = f"{coin_manual_alert} на продажу достиг {price}$"
                                bot.send_message(user_id, message_text)
                                print(f"Sent notification to user {user_id}: {message_text}")
                                notified_users[user_id] = True  # Отмечаем, что уведомление было отправлено
                        else:
                        # Сбрасываем флаг уведомления, если цена больше не соответствует условиям
                            notified_users[user_id] = False
                            print(f"Price for user {user_id}: {price}, Desired price: {desired_price}")
                    else:
                        print(f"Invalid or empty price data received from Yobit API")
                except requests.exceptions.RequestException as e:
                # Обработка ошибок при запросе к API (например, нет интернет-соединения или проблемы с URL)
                    print(f"Request error: {e}")        
                
            time.sleep(20) 

    check_price_thread = threading.Thread(target=check_price)
    check_price_thread.start()          

    @bot.callback_query_handler(func=lambda call: call.data in ["Back"])
    def handle_button_click(call):
        coin_alert_option = call.data
        chat_id = call.message.chat.id
        if coin_alert_option == "Back":
            handle_button_click(call)
            return
        pass



    # Обработчик выбора времени
    @bot.callback_query_handler(func=lambda call: call.data in [f"{option}:{time_option}" for option in dailyalert_options for time_option in time_options])
    def handle_time_option_click(call): 
        coin_alert_option = call.data
         
        full_data = call.data.split(":")
        daily_alert_option = full_data[0]
        time_option = full_data[1]
        chat_id = call.message.chat.id
        now = datetime.now().strftime("%H-%M")
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        back_button = telebot.types.InlineKeyboardButton("Back", callback_data="Back")
        markup.add(back_button)
    
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"✅Готово!\n\n\n💰Монета ➙ {daily_alert_option}\n\n⏰Время сейчас ➙ {now}\n\n⏳Время уведомления ➙ {time_option}\n\nДля возврата в главное меню \nВыберете Back 📃", reply_markup=markup)  

    # Отправка сообщений (цены криптоволюты) в выбраное время 
    def send_scheduled_message(time_option, chat_id, daily_alert_option):
        try:
            url = f"https://yobit.net/api/3/ticker/{daily_alert_option}_usd"
            req = requests.get(url)
            response = req.json()
            price = response.get(f"{daily_alert_option}_usd", {}).get("sell")   
        except Exception as ex:
                print(f"Error fetching BTC Price: {ex}")
                bot.send_message("Error fetching BTC Price, please try again later")


        now = datetime.now().strftime("%H-%M") 
        message = f"⌛Daily Alert\n\n\n⏰Время сейчас ➙ {now}\n\n🪙Монета ➙ {daily_alert_option}\n\n💸Цена ➙ {price}"     
        bot.send_message(chat_id, message)

    # Обработчик нажатия кнопки "Back"
    @bot.callback_query_handler(func=lambda call: call.data == "Back")
    def handle_button_click(call):
        if call.data == "Back":
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            handle_start(call.message)
           
    # Отправка цены криптоволюты 
    @bot.callback_query_handler(func=lambda call: call.data in coin_options)
    def handle_coin_option_click(call):
        coin_option = call.data
        if coin_option == "BTC Price":
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)
            time_frames = ["1 D", "5 D", "1 M", "3 M", "6 M", "1 Y"]

            for frame_option in time_frames:
                button = telebot.types.InlineKeyboardButton(frame_option, callback_data=frame_option)
                markup.add(button)

            try:
                req = requests.get("https://yobit.net/api/3/ticker/btc_usd")
                response = req.json()
                sell_price = response.get("btc_usd", {}).get("sell")

                if sell_price is not None:
                    message_text = f"Choose TimeFrame"
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text, reply_markup=markup)
                else:
                    bot.send_message(call.from_user.id, "BTC price data not available.")
            except Exception as ex:
                print(f"Error fetching BTC Price: {ex}")
                bot.send_message(call.from_user.id, "Error fetching BTC Price, please try again later")

    @bot.callback_query_handler(func=lambda call: call.data in ["1 D", "5 D", "1 M", "3 M", "6 M", "1 Y"])
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
                "| Symbol |   Price   | Change |\n"
                "|--------|-----------|--------|\n"
                f"| BTC    | {btc_data['Close'][-1]:.2f}  | {price_change:.2f} |\n"
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