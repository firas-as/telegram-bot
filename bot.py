import os
import json
import time
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ====== إعدادات ======
TOKEN = os.getenv("TOKEN")
ADMIN_ID = 1332757886
CHANNEL_ID = -1003989734235

WALLET = "TF7unwMkyxhNPMG5Yufec8zNdcAAgqjuMG"
NETWORK = "TRC20"

PLANS = {
    "plan_1": {"price": 90, "days": 30},
    "plan_3": {"price": 150, "days": 90},
    "plan_12": {"price": 250, "days": 365},
}

DB_FILE = "users.json"

logging.basicConfig(level=logging.INFO)

# ====== DB ======
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

db = load_db()

# ====== START ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("💎 دخول VIP", callback_data="vip")]]

    await update.message.reply_text(
        "💎 EvoraFX VIP\n\nاضغط للدخول",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ====== BUTTON ======
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "vip":
        buttons = [
            [InlineKeyboardButton("شهر 90$", callback_data="plan_1")],
            [InlineKeyboardButton("3 أشهر 150$", callback_data="plan_3")],
            [InlineKeyboardButton("سنة 250$", callback_data="plan_12")],
        ]
        await query.message.reply_text("اختر:", reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data in PLANS:
        context.user_data["plan"] = query.data
        price = PLANS[query.data]["price"]

        await query.message.reply_text(
            f"ادفع {price}$ على {NETWORK}\n{WALLET}\n\nأرسل صورة"
        )

    elif query.data.startswith("approve_"):
        user_id = int(query.data.split("_")[1])
        db[str(user_id)]["expiry"] = int(time.time()) + 86400 * 30
        save_db(db)

        await context.bot.send_message(user_id, "تم التفعيل")

# ====== PHOTO ======
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    plan = context.user_data.get("plan")

    if not plan:
        await update.message.reply_text("اختر باقة أولاً")
        return

    db[str(user.id)] = {"plan": plan, "expiry": 0}
    save_db(db)

    buttons = [[
        InlineKeyboardButton("قبول", callback_data=f"approve_{user.id}"),
        InlineKeyboardButton("رفض", callback_data=f"reject_{user.id}")
    ]]

    await context.bot.send_photo(
        ADMIN_ID,
        update.message.photo[-1].file_id,
        caption=f"طلب من {user.id}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    await update.message.reply_text("تم الإرسال")

# ====== RUN ======
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
