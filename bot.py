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

VIP_LINK = "https://t.me/+U0qTr_Ck7YszNzE8"

WALLET = "TF7unwMkyxhNPMG5Yufec8zNdcAAgqjuMG"
NETWORK = "TRC20"

PLANS = {
    "plan_1": {"name": "شهر", "price": 90, "days": 30},
    "plan_3": {"name": "3 أشهر", "price": 150, "days": 90},
    "plan_12": {"name": "سنة", "price": 250, "days": 365},
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
    keyboard = [
        [InlineKeyboardButton("💎 VIP", callback_data="vip")],
    ]
    await update.message.reply_text(
        "أهلاً فيك 👋",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ====== BUTTON ======
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "vip":
        buttons = [
            [InlineKeyboardButton("📅 شهر - 90$", callback_data="plan_1")],
            [InlineKeyboardButton("📆 3 أشهر - 150$", callback_data="plan_3")],
            [InlineKeyboardButton("📊 سنة - 250$", callback_data="plan_12")],
        ]
        await query.message.reply_text("اختر الباقة:", reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data in PLANS:
        plan = PLANS[query.data]
        context.user_data["plan"] = query.data

        await query.message.reply_text(
            f"💰 الدفع عبر {NETWORK}\n\n"
            f"{plan['price']}$\n{WALLET}\n\n"
            f"أرسل صورة الدفع"
        )

    elif query.data.startswith("approve_"):
        user_id = query.data.split("_")[1]
        plan_key = db[user_id]["plan"]
        days = PLANS[plan_key]["days"]

        db[user_id]["expiry"] = int(time.time()) + days * 86400
        save_db(db)

        await context.bot.send_message(
            chat_id=int(user_id),
            text=f"✅ تم التفعيل\n{VIP_LINK}"
        )

    elif query.data.startswith("reject_"):
        user_id = query.data.split("_")[1]
        await context.bot.send_message(
            chat_id=int(user_id),
            text="❌ تم الرفض"
        )

# ====== PHOTO ======
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    plan = context.user_data.get("plan")

    if not plan:
        await update.message.reply_text("اختر الباقة أولاً")
        return

    db[str(user.id)] = {"plan": plan, "expiry": 0}
    save_db(db)

    buttons = [[
        InlineKeyboardButton("✅ قبول", callback_data=f"approve_{user.id}"),
        InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user.id}")
    ]]

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"طلب VIP\nID: {user.id}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    await update.message.reply_text("تم إرسال الطلب")

# ====== RUN ======
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("vip", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
