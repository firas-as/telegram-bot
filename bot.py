import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import *

TOKEN = os.getenv("TOKEN")
CHANNEL = "@Evora Fx VIP GOLD"

user_data_store = {}

logging.basicConfig(level=logging.INFO)

# start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 إرسال إشارة", callback_data="signal")],
        [InlineKeyboardButton("📈 الصفقات", callback_data="trades")],
    ]
    await update.message.reply_text(
        "Welcome / أهلاً فيك",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# signal flow
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "signal":
        await query.message.reply_text("Send pair / أرسل الزوج:")
        return 1

# steps
async def get_pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pair"] = update.message.text
    await update.message.reply_text("BUY or SELL?")
    return 2

async def get_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["type"] = update.message.text.upper()
    await update.message.reply_text("Entry:")
    return 3

async def get_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["entry"] = update.message.text
    await update.message.reply_text("SL:")
    return 4

async def get_sl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sl"] = update.message.text
    await update.message.reply_text("TP1:")
    return 5

async def get_tp1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tp1"] = update.message.text
    await update.message.reply_text("TP2:")
    return 6

async def get_tp2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tp2"] = update.message.text

    msg = f"""
📊 {context.user_data['pair']} — {context.user_data['type']}

Entry: {context.user_data['entry']}
SL: {context.user_data['sl']}
TP1: {context.user_data['tp1']}
TP2: {context.user_data['tp2']}

Risk: 1%
"""

    buttons = [
        [InlineKeyboardButton("✅ TP1", callback_data="tp1"),
         InlineKeyboardButton("❌ SL", callback_data="sl")]
    ]

    await context.bot.send_message(
        chat_id=CHANNEL,
        text=msg,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    await update.message.reply_text("✅ Sent!")

    return ConversationHandler.END

# main
app = ApplicationBuilder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(button)],
    states={
        1: [MessageHandler(filters.TEXT, get_pair)],
        2: [MessageHandler(filters.TEXT, get_type)],
        3: [MessageHandler(filters.TEXT, get_entry)],
        4: [MessageHandler(filters.TEXT, get_sl)],
        5: [MessageHandler(filters.TEXT, get_tp1)],
        6: [MessageHandler(filters.TEXT, get_tp2)],
    },
    fallbacks=[]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(conv)

app.run_polling()
