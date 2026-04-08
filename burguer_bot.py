import logging
import json

from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import MessageHandler, filters
from telegram.ext import filters

#configuración de logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

ADMIN_ID = 7548098424

TOKEN = "8025561801:AAFdmQqU-diP9Pz4AjLGjF7apy4duWY_rw4"

COMANDOS = {
    "start": "Manda un mensaje de bienvenida con un botón que abre la MiniApp de MCBurguer",
    "help": "Muestra todos los comandos disponibles",
    "historial": "Muestra el historial de pedidos en la memoria",
    "admin": "Panel de estadísticas solo para el admin",
    "pedidos": "Solo para el admin. Lista todos los pedidos de los usuarios con sus totales."

}

#historial en memoria
historial_pedidos = {}
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = "📋 Comandos disponibes:\n"
    for comando, descripcion in COMANDOS.items():
        texto += f"/{comando}: {descripcion}\n"
    await update.message.reply_text(texto)
#Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botones = [[
        InlineKeyboardButton(
            "🍔 Ver menú",
            web_app=WebAppInfo(url="https://t-cantero.github.io/MCBurguer/")
        )
    ]]
    markup = InlineKeyboardMarkup(botones)

    await update.message.reply_text(
        "🍔 Bienvenido a MCBurguer! Pulsa para ver el menú.",
        reply_markup=markup
    )

#Recibe pedidos desde la WebApp
async def pedido_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(">>>>>PEDIDO RECIBIDO LLAMADO")
    if not update.message or not update.message.web_app_data:
        return

    try:
        data = json.loads(update.message.web_app_data.data)

        items = data.get("pedido", [])
        total = data.get("total", 0)

        user_id = update.effective_user.id
        nombre = update.effective_user.first_name

        # Guardar historial
        if user_id not in historial_pedidos:
            historial_pedidos[user_id] = []

        historial_pedidos[user_id].append({
            "items": items,
            "total": total
        })

        resumen = "\n".join([
            f"{item['emoji']} {item['nombre']} x{item['cantidad']} = {item['subtotal']}€"
            for item in items
        ])

        # Mensaje usuario
        await update.message.reply_text(
            f"✅ ¡Gracias {nombre}! Tu pedido está en camino 🚀\n\n"
            f"{resumen}\n\n"
            f"💰 Total: {total}€"
        )

        #Mensaje al admin
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"📦 NUEVO PEDIDO\n\n"
                f"👤 Usuario: {nombre} (ID: {user_id})\n\n"
                f"{resumen}\n\n"
                f"💰 Total: {total}€"
            )
        )

    except Exception as e:
        print("ERROR:", e)

#Comando /historial
async def historial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in historial_pedidos or len(historial_pedidos[user_id]) == 0:
        await update.message.reply_text("📭 No tienes pedidos en el historial.")
        return
    mensajes = []

    for i, pedido in enumerate(historial_pedidos[user_id], start=1):
        resumen = "\n".join([
            f"{item['emoji']} {item['nombre']} x{item['cantidad']}"
            for item in pedido["items"]
        ])
        mensajes.append(
            f"🧾 Pedido {i}:\n{resumen}\n💰 Total: {pedido['total']}€\n"
        )
    texto_final = "\n".join(mensajes)
    await update.message.reply_text(
        f"📜 Tu historial de pedidos:\n\n{texto_final}"
    )

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ No tienes permisos.")
        return
    total_pedidos = sum(len(p) for p in historial_pedidos.values())
    total_usuarios = len(historial_pedidos)

    await update.message.reply_text(
        f"📊 PANEL ADMIN\n\n"
        f"👥 Usuarios: {total_usuarios}\n"
        f"📦 Pedidos totales: {total_pedidos}"
    )

async def ver_pedidos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not historial_pedidos:
        await update.message.reply_text("📭 No hay pedidos aún.")
        return
    texto = ""
    for user_id, pedidos in historial_pedidos.items():
        texto += f"\n👤 Usuario {user_id}:\n"

        for i, pedido in enumerate(pedidos, 1):
            texto += f"  🧾 Pedido {i} - {pedido['total']}€\n"
    await update.message.reply_text(texto)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("historial",historial))
app.add_handler(CommandHandler("admin",admin))
app.add_handler(CommandHandler("pedidos",ver_pedidos))
app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, pedido_recibido))

print("BOT INICIADO...")
app.run_polling()