from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN:  Final = '6687531734:AAH8U1ZWLl7AWEEWw4cEr2vdi-NdCIEpJ1s'
BOT_USERNAME: Final = 'tradingalarmukraine_bot'

async def start_command(update: Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello!Welcome to Ucrainian Trading Alarm Bot =)')

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler('start',start_command))