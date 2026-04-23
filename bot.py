import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# إعدادات أساسية
TOKEN = os.getenv("TOKEN")
CHANNEL = "@your_channel"  # حط اسم قناتك مع @

logging.basicConfig(level=logging.INFO)

# مراحل الإدخال
PAIR, TYPE, ENTRY, SL, TP1, TP2 = range(6)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 إرسال إشارة", callback_data="signal")],
    ]
    await update.message.reply_text(
        "أهلاً فيك 👋\nWelcome!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ضغط زر
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "signal":
        await query.message.reply_text("أدخل الزوج (مثال EURUSD):")
        return PAIR

# إدخال البيانات
async def get_pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pair"] = update.message.text
    await update.message.reply_text("BUY أو SELL؟")
    return TYPE

async def get_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["type"] = update.message.text.upper()
    await update.message.reply_text("Entry:")
    return ENTRY

async def get_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["entry"] = update.message.text
    await update.message.reply_text("SL:")
    return SL

async def get_sl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sl"] = update.message.text
    await update.message.reply_text("TP1:")
    return TP1

async def get_tp1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tp1"] = update.message.text
    await update.message.reply_text("TP2:")
    return TP2

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
        [
            InlineKeyboardButton("✅ TP1 HIT", callback_data="tp1"),
            InlineKeyboardButton("❌ SL HIT", callback_data="sl"),
        ]
    ]

    await context.bot.send_message(
        chat_id=CHANNEL,
        text=msg,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    await update.message.reply_text("✅ تم إرسال الإشارة")

    return ConversationHandler.END

# تشغيل البوت
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button)],
        states={
            PAIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_pair)],
            TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_type)],
            ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_entry)],
            SL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_sl)],
            TP1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tp1)],
            TP2: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tp2)],
        },
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
