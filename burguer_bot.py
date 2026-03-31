import logging

from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
TOKEN = "8025561801:AAFdmQqU-diP9Pz4AjLGjF7apy4duWY_rw4"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botones = [[
        InlineKeyboardButton("🍔 Ver menú", web_app=WebAppInfo(url="https://tu-web.com"))
    ]]
    markup = InlineKeyboardMarkup(botones)
    await update.message.reply_text("🍔 Bienvenido a MCBurguer! Pulsa para ver el menú.", reply_markup=markup)

async def pedido_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pedido = update.message.web_app_data
    await update.message.reply_text(f"🍔 Pedido recibido:\n{pedido}")
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()