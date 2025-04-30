# telegram_spoofer_bot.py

from telegram import Update, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    CallbackQueryHandler,
    filters  # ✅ Correct filter import here
)

from datetime import datetime, timedelta
import os

from utils import spoof_and_zip_files, clean_user_temp_folder, valid_file_type, convert_if_needed
from db import get_access_status, grant_access, has_access, init_db
from payments import create_invoice
from settings_manager import set_setting, get_user_settings, reset_user_settings

BOT_TOKEN = "7936921247:AAGJnZZRcJMjyMVExUDJ5RL5Ahtu3MO7jMk"
MONTHLY_PRICE = 19.99
LIFETIME_PRICE = 199.00

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# ======================== BOT COMMANDS ========================

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to 1OF1 Spoofer.\nUse /subscribe to gain access.")

async def status(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    access = get_access_status(user_id)
    if access:
        await update.message.reply_text(f"✅ Access type: {access['type']}\nExpires: {access['expires']}")
    else:
        await update.message.reply_text("❌ You don't have access. Use /subscribe to unlock.")

async def subscribe(update: Update, context: CallbackContext):
    text = (
        "💸 Choose a subscription option:\n"
        f"/monthly - ${MONTHLY_PRICE} for 30-day access\n"
        f"/lifetime - ${LIFETIME_PRICE} one-time forever access"
    )
    await update.message.reply_text(text)

async def sub_monthly(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    invoice = create_invoice(user_id, MONTHLY_PRICE, "1OF1 Spoofer - Monthly Access")
    await update.message.reply_text(f"🧾 Pay $19.99 USDT here:\n{invoice}")

async def sub_lifetime(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    invoice = create_invoice(user_id, LIFETIME_PRICE, "1OF1 Spoofer - Lifetime Access")
    await update.message.reply_text(f"🧾 Pay $199 USDT here:\n{invoice}")

# ======================== FILE HANDLER ========================

async def handle_file(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if not has_access(user_id):
        await update.message.reply_text("🔒 You need to subscribe. Use /subscribe")
        return

    file = update.message.document or update.message.video or update.message.photo[-1]
    file_name = file.file_name if hasattr(file, 'file_name') else f"file_{user_id}"
    if not valid_file_type(file_name):
        await update.message.reply_text("Unsupported file type. Allowed: JPG, PNG, HEIC, WEBP, MP4, MOV")
        return

    folder = os.path.join(TEMP_DIR, user_id)
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, file_name)
    tg_file = await file.get_file()
    await tg_file.download_to_drive(custom_path=filename)

    context.user_data['uploaded_file'] = filename

    keyboard = [[
        InlineKeyboardButton("1", callback_data="copies_1"),
        InlineKeyboardButton("3", callback_data="copies_3"),
        InlineKeyboardButton("5", callback_data="copies_5")
    ]]
    await update.message.reply_text("How many spoofed versions do you want?", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = str(query.from_user.id)
    await query.answer()
    data = query.data

    if data.startswith("copies_"):
        count = int(data.split("_")[1])
        set_setting(user_id, "copies", count)
        keyboard = [[
            InlineKeyboardButton("10px", callback_data="crop_10"),
            InlineKeyboardButton("15px", callback_data="crop_15"),
            InlineKeyboardButton("20px", callback_data="crop_20")
        ]]
        await query.edit_message_text("Select crop intensity:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("crop_"):
        crop = int(data.split("_")[1])
        set_setting(user_id, "crop", crop)
        keyboard = [[
            InlineKeyboardButton("Yes", callback_data="flip_yes"),
            InlineKeyboardButton("No", callback_data="flip_no")
        ]]
        await query.edit_message_text("Apply random horizontal flip?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("flip_"):
        flip = data.split("_")[1] == "yes"
        set_setting(user_id, "flip", flip)

        filename = context.user_data.get('uploaded_file')
        if not filename:
            await query.edit_message_text("File not found. Please re-upload.")
            return

        await query.edit_message_text("✅ Got it. Processing your spoofed files...")
        folder = os.path.dirname(filename)
        converted_path = convert_if_needed(filename)
        settings = get_user_settings(user_id)
        zip_path = spoof_and_zip_files([converted_path], folder, settings)
        await context.bot.send_document(chat_id=query.message.chat.id, document=InputFile(zip_path))
        clean_user_temp_folder(user_id)
        reset_user_settings(user_id)

# ======================== MAIN APP ========================

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("monthly", sub_monthly))
    app.add_handler(CommandHandler("lifetime", sub_lifetime))

    # ✅ Replaces crashing filters.Video with filters.ATTACHMENT
    app.add_handler(MessageHandler(filters.ATTACHMENT | filters.PHOTO, handle_file))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
