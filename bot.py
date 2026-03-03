from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message
)
from pyromod import listen
import os
import mimetypes

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client(
    "rename-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

THUMB_FOLDER = "thumbnails"
os.makedirs(THUMB_FOLDER, exist_ok=True)


# ================= START ================= #

@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    await message.reply_text(
        "📂 **This is a File Rename Bot**\n\n"
        "👑 Host: @Anime_friend001\n\n"
        "🖼 Send photo to set thumbnail.\n"
        "📁 Send a file to rename."
    )


# ================= SAVE THUMB ================= #

@app.on_message(filters.photo)
async def save_thumb(client, message: Message):
    user_id = str(message.from_user.id)
    thumb_path = f"{THUMB_FOLDER}/{user_id}.jpg"
    await message.download(file_name=thumb_path)
    await message.reply_text("✅ Personal thumbnail saved!")


# ================= FILE DETECT ================= #

@app.on_message(filters.document)
async def detect_file(client, message: Message):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✏️ Rename", callback_data="rename"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel"),
            ]
        ]
    )

    await message.reply_text(
        f"📦 **File Detected**\n\n"
        f"📄 Name: `{message.document.file_name}`\n"
        f"📦 Size: {round(message.document.file_size / (1024*1024), 2)} MB",
        reply_markup=keyboard
    )


# ================= BUTTON HANDLER ================= #

@app.on_callback_query()
async def callback_handler(client, query: CallbackQuery):

    if query.data == "cancel":
        return await query.message.edit("❌ Cancelled.")

    if query.data == "rename":
        await query.message.edit("✏️ Send new file name with extension (example: movie.mkv)")

        try:
            response = await client.listen(
                chat_id=query.message.chat.id,
                filters=filters.user(query.from_user.id),
                timeout=120
            )
        except:
            return await query.message.edit("❌ Time expired.")

        new_name = response.text

        # Get last file message
        original = query.message.reply_to_message

        processing = await query.message.reply_text("⏳ Downloading...")

        file_path = await original.download()

        await processing.edit("⏫ Uploading...")

        user_id = str(query.from_user.id)
        thumb_path = f"{THUMB_FOLDER}/{user_id}.jpg"

        mime_type, _ = mimetypes.guess_type(new_name)

        if mime_type and mime_type.startswith("video"):
            await query.message.reply_video(
                video=file_path,
                caption="✅ File Renamed Successfully!",
                thumb=thumb_path if os.path.exists(thumb_path) else None
            )
        else:
            await query.message.reply_document(
                document=file_path,
                file_name=new_name,
                caption="✅ File Renamed Successfully!",
                thumb=thumb_path if os.path.exists(thumb_path) else None
            )

        os.remove(file_path)
        await processing.delete()


app.run()
