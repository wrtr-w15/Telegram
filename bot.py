import telegram.ext

Token = "6687531734:AAH8U1ZWLl7AWEEWw4cEr2vdi-NdCIEpJ1s"

updater = telegram.ext.Updater("6687531734:AAH8U1ZWLl7AWEEWw4cEr2vdi-NdCIEpJ1s", update_context=True)

dispatcher = updater.dispatcher 

def start(update, context):
    update.message.reply_text("Welcome to Tradign Alarm - useful bot where you can set alarm on any cryptocurrency that is available on Binance.com")

def help(update, context):
    update.message.reply_text(
    #За скобками можешь добавить еще команды
    """
    /start - Starts telegram bot  
    /help - List commands
    """
    )
# Через def добавляешь функцию команде

dispatcher.add_handle(telegram.ext.CommandHandler('/start', start))
dispatcher.add_handle(telegram.ext.CommandHandler('help', help))

updater.start_polling()
updater.idle()