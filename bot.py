from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen
import os

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


# 🔹 Start Message
@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    await message.reply_text(
        "📂 **This is a File Rename Bot**\n\n"
        "👑 Host: @Anime_friend001\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🖼 Send a photo to set your personal thumbnail.\n"
        "📁 Send a file to rename it.\n"
        "━━━━━━━━━━━━━━━━━━"
    )


# 🔹 Save Personal Thumbnail
@app.on_message(filters.photo)
async def save_thumb(client, message: Message):
    user_id = str(message.from_user.id)
    thumb_path = f"{THUMB_FOLDER}/{user_id}.jpg"

    await message.download(file_name=thumb_path)
    await message.reply_text("✅ Your personal thumbnail has been saved!")


# 🔹 Rename File With Personal Thumbnail
@app.on_message(filters.document)
async def rename_handler(client, message: Message):
    user_id = str(message.from_user.id)
    thumb_path = f"{THUMB_FOLDER}/{user_id}.jpg"

    await message.reply_text("✏️ Send new file name with extension (example: movie.mp4)")

    try:
        response = await client.listen(message.chat.id, timeout=60)
    except:
        return await message.reply_text("❌ Time expired. Send the file again.")

    new_name = response.text
    file_path = await message.download()

    await message.reply_document(
        document=file_path,
        file_name=new_name,
        thumb=thumb_path if os.path.exists(thumb_path) else None,
        caption="✅ File Renamed Successfully!"
    )

    os.remove(file_path)


app.run()
