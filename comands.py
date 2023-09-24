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
from functools import partial
from telegram.ext import Updater, CommandHandler
from menu_options import menu_options, coin_options, dailyalert_options , time_options , back_options, alert_options, alert_options,convert_options1

def telegram_bot(token):
    bot = telebot.TeleBot(token)
    coin_manual_alert = None
    printy = bot.send_message
    
    edity = bot.edit_message_text
    coin1 = None
    coin2 = None
    price_coin1 = None
    price_coin2 = None
    price_amount = None
    quantity_coin1 = None
    quantity_coin2= None
    quantity_amount = None
    quantity_coin1_price = None
    quantity_coin2_price = None
         
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

        printy(message.chat.id, "Привет👋\n\n\nЯ, Treiding Alarm - бот, который поможет тебе отслеживать курс криптовалют, просматривать график цены и устанавливать оповещения при достижении монетой желаемой цены. \n\n\nДавай посмотрим, что там👇", reply_markup=markup)



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
        elif option == "📊Conversion":
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)
            for convert_option1 in convert_options1:
                button = telebot.types.InlineKeyboardButton(convert_option1, callback_data=convert_option1)
                markup.add(button)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                   text="Нажми на интересующую монету\nИ ты увидишь её курс относительно другой валютной пары\n\n\nДля возврата в главное меню\nВыберете Back 📃", 
                                   reply_markup=markup)
            
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

    # Обработчик выбора варианта "convert"
    @bot.callback_query_handler(func=lambda call: call.data in convert_options1)
    def handle_convert_option_click(call):
        chat_id = call.message.chat.id
        convert_option1 = call.data
        if convert_option1 == "Back":
            handle_button_click(call)
            return

        elif convert_option1 == "Price":
            
            chat_id = call.message.chat.id
            bot.send_message(chat_id, "Введите сумму которую вы хотите обменять:")
            bot.register_next_step_handler(call.message, handle_amount_input)
            
        elif convert_option1 == "Quantity":
            
            chat_id = call.message.chat.id
            bot.send_message(chat_id, "Введите криптовалюту которую вы хотите обменять:")
            bot.register_next_step_handler(call.message, handle_quantity_input)

    @bot.message_handler(func=lambda message: True)
    def handle_quantity_input(message):
        chat_id = message.chat.id
        global quantity_coin1
        quantity_coin1 = message.text
        bot.send_message(chat_id, f'На какую монету вы хотите обменять {quantity_coin1}\n\nВведите:')
        bot.register_next_step_handler(message, handle_quantity2_input)

    @bot.message_handler(func=lambda message: True)
    def handle_quantity2_input(message):
        chat_id = message.chat.id
        global quantity_coin2
        global quantity_coin1
        global quantity_amount
        quantity_coin2 = message.text
        bot.send_message(chat_id, f'Какое количество {quantity_coin1} вы хотите обменять\n\nВведите:')
        bot.register_next_step_handler(message, handle_quantity_amount_input)
         

    
    @bot.message_handler(func=lambda message: True)
    def handle_quantity_amount_input(message):
        global quantity_amount
        chat_id = message.chat.id
        quantity_amount = message.text.strip()
        try:
            quantity_amount = float(quantity_amount)
        except ValueError:
            bot.send_message(chat_id, "Неверный формат количества. Введите число.")
            return
        send_quantyty_convert_message(message)      

    def send_quantyty_convert_message(message):
        chat_id = message.chat.id
        global quantity_coin1_price 
        global quantity_coin2_price
        global quantity_amount
        global quantity_coin1
        global quantity_coin2

        quantity_coin1_price,quantity_coin2_price = get_quantity_crypto_prices(quantity_coin1,quantity_coin2)
        if quantity_coin1_price is None:
            bot.send_message(chat_id, f"Не удалось получить цену для {quantity_coin1}")
            return
        if quantity_coin2_price is None:
            bot.send_message(chat_id, f"Не удалось получить цену для {quantity_coin2}")
            return

        result_quantity_convert = (quantity_amount*quantity_coin1_price) / quantity_coin2_price
        bottom_markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        back_button = telebot.types.InlineKeyboardButton("Back", callback_data="Back")
        bottom_markup.add(back_button)

        for button in bottom_markup.keyboard:
            markup.add(*button)

        bot.send_message(chat_id, f'Результат: {result_quantity_convert}', reply_markup=markup)

    def get_quantity_crypto_prices(quantity_coin1,quantity_coin2):
        try:
            global quantity_coin1_price
            quantity_coin1 = quantity_coin1.lower()
            url = f"https://yobit.net/api/3/ticker/{quantity_coin1}_usd"
            req = requests.get(url)
            response = req.json()
            quantity_coin1_price = response.get(f"{quantity_coin1}_usd", {}).get("sell")
        except Exception as ex:
            print(f"Error fetching {quantity_coin1} Price: {ex}")
            quantity_coin1_price = None
            
        try:
            global quantity_coin2_price
            quantity_coin2 = quantity_coin2.lower()
            url = f"https://yobit.net/api/3/ticker/{quantity_coin2}_usd"
            req = requests.get(url)
            response = req.json()
            quantity_coin2_price = response.get(f"{quantity_coin2}_usd", {}).get("sell")
        except Exception as ex:
            print(f"Error fetching {quantity_coin2} Price: {ex}")
            quantity_coin2_price = None

        return quantity_coin1_price,quantity_coin2_price  

    @bot.message_handler(func=lambda message: True)
    def handle_amount_input(message):
        global price_amount
        chat_id = message.chat.id
        price_amount = message.text.strip()
        try:
            price_amount = float(price_amount)
        except ValueError:
            bot.send_message(chat_id, "Неверный формат суммы. Введите число.")
            return
        bot.send_message(chat_id, f'На какую монету вы хотите обменять {price_amount}\n\nВведите:')
        bot.register_next_step_handler(message, handle_coin1_input)
    

    @bot.message_handler(func=lambda message: True)
    def handle_coin1_input(message):
        chat_id = message.chat.id
        global coin1
        coin1 = message.text
        send_price_convert_message(message)

    def send_price_convert_message(message):
        chat_id = message.chat.id
        global price_coin2
        global price_amount
        global price_coin1
        global coin1

        price_coin1 = get_crypto_prices(coin1)
        if price_coin1 is None:
            bot.send_message(chat_id, f"Не удалось получить цену для {coin1}")
            return
        
        
        result_convert = price_amount / price_coin1

        bottom_markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        back_button = telebot.types.InlineKeyboardButton("Back", callback_data="Back")
        
        bottom_markup.add(back_button)
        for button in bottom_markup.keyboard:
            markup.add(*button)

        bot.send_message(chat_id, f'Результат: {result_convert}', reply_markup=markup)

# Функция для получения цен на криптовалюты
    def get_crypto_prices(coin1):
        try:
            global price_coin1
            coin1 = coin1.lower()
            url = f"https://yobit.net/api/3/ticker/{coin1}_usd"
            req = requests.get(url)
            response = req.json()
            price_coin1 = response.get(f"{coin1}_usd", {}).get("sell")
        except Exception as ex:
            print(f"Error fetching {coin1} Price: {ex}")
            price_coin1 = None

        return price_coin1
               
    # Обработчик выбора варианта "Daily Alert"
    @bot.callback_query_handler(func=lambda call: call.data in dailyalert_options)
    def handle_daily_alert_option_click(call):
        daily_alert_option = call.data
        chat_id = call.message.chat.id
        if daily_alert_option == "Back":
            handle_button_click(call)
            return

        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        row_buttons = [telebot.types.InlineKeyboardButton(time_option, callback_data=f"{daily_alert_option}:{time_option}") for time_option in time_options]

        for i in range(0, len(row_buttons), 2):
            markup.add(row_buttons[i], row_buttons[i+1] if i+1 < len(row_buttons) else None)

        bottom_markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        manual_button = telebot.types.InlineKeyboardButton("Manual", callback_data="Manual")
        back_button = telebot.types.InlineKeyboardButton("Back", callback_data="Back")
        
        bottom_markup.add(manual_button, back_button)


        for button in bottom_markup.keyboard:
            markup.add(*button)

        edity(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="Выберете время ⏰\n\nВ это время вы получите уведомление!💰\n\nДля возврата в главное меню \n\nВыберете Back 📃",
            reply_markup=markup
        )
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

        now = datetime.now().strftime("%H-%M")
        chat_id = call.message.chat.id
        full_data = call.data.split(":")
        daily_alert_option = full_data[0]
        time_option = full_data[1]
    
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
                printy("Error fetching BTC Price, please try again later")


        now = datetime.now().strftime("%H-%M") 
        message = f"⌛Daily Alert\n\n\n⏰Время сейчас ➙ {now}\n\n🪙Монета ➙ {daily_alert_option}\n\n💸Цена ➙ {price}"     
        bot.send_message(chat_id, message)

    # Обработчик нажатия кнопки "Back"
    @bot.callback_query_handler(func=lambda call: call.data == "Back")
    def handle_button_click(call):
        if call.data == "Back":
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            handle_start(call.message)
           
    #Coin price and graph
    @bot.callback_query_handler(func=lambda call: call.data in coin_options)
    def handle_coin_option_click(call):
        coin_option = call.data
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        time_frames = {"1 day": "1d", "5 days": "5d", "1 month": "1mo", "3 month": "3mo", "6 month": "6mo", "1 year": "1y"}

        for frame_option, frame_period in time_frames.items():
            button = telebot.types.InlineKeyboardButton(frame_option, callback_data=f"{coin_option}|{frame_period}")
            markup.add(button)

        try:
            message_text = f"Choose TimeFrame for {coin_option}"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text, reply_markup=markup)
        except Exception as ex:
            print(f"Error updating message: {ex}")
            bot.send_message(call.from_user.id, "Error updating message, please try again later")

    @bot.callback_query_handler(func=lambda call: "|" in call.data)
    def handle_time_frame_click(call):
        coin_option, frame_period = call.data.split("|")
        try:
            coin_data = yf.download(coin_option, period=frame_period, interval="1h")

            # Create a plot
            plt.figure(figsize=(10, 6))
            plt.plot(coin_data.index, coin_data["Close"], label=f"{coin_option} Price")
            plt.xlabel("Date")
            plt.ylabel("Price (USD)")
            plt.title(f"{coin_option} Price Chart ({frame_period} timeframe)")
            plt.legend()

            # Calculate price change
            price_change = coin_data["Close"][-1] - coin_data["Close"][0]

            # Convert the plot to an image
            image_stream = io.BytesIO()
            plt.savefig(image_stream, format="png")
            image_stream.seek(0)

            # Construct the table-like message
            message_text = (
                f"{coin_option} Price: {coin_data['Close'][-1]:.2f}\n"
                f"Price Change: {price_change:.2f}\n\n"
                "```\n"
                "| Symbol |   Price   | Change |\n"
                "|--------|-----------|--------|\n"
                f"| {coin_option} | {coin_data['Close'][-1]:.2f} | {price_change:.2f} |\n"
                "```"
            )

            # Send the image with the message to the user
            bot.send_photo(call.from_user.id, photo=image_stream, caption=message_text, parse_mode="Markdown")

            # Close the plot
            plt.close()
        except Exception as ex:
            print(f"Error creating {coin_option} price chart: {ex}")
            bot.send_message(call.from_user.id, f"Error creating {coin_option} price chart ({frame_period} timeframe), please try again later")
            
    bot.polling()

telegram_bot(token)