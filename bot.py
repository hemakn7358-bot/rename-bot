from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyromod import listen
import os
import mimetypes
import time

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


# ================= PROGRESS ================= #

async def progress(current, total, message, start, action):
    now = time.time()
    diff = now - start

    if diff < 1:
        return

    percentage = current * 100 / total
    speed = current / diff
    eta = round((total - current) / speed) if speed > 0 else 0

    bar_len = 20
    filled = int(bar_len * current // total)
    bar = "■" * filled + "□" * (bar_len - filled)

    try:
        await message.edit_text(
            f"{action}...\n\n"
            f"{bar}\n\n"
            f"📁 Size : {round(current/(1024*1024),2)} MB | {round(total/(1024*1024),2)} MB\n"
            f"⏳ Done : {round(percentage,2)}%\n"
            f"🚀 Speed : {round(speed/1024,2)} KB/s\n"
            f"⏰ ETA : {eta} sec"
        )
    except:
        pass


# ================= START ================= #

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text(
        "📂 File Rename Bot\n\n"
        "👑 Host: @Anime_friend001\n\n"
        "🖼 Send photo to set thumbnail\n"
        "📁 Send file to rename"
    )


# ================= SAVE THUMB ================= #

@app.on_message(filters.photo)
async def save_thumb(client, message):
    user_id = str(message.from_user.id)
    thumb_path = f"{THUMB_FOLDER}/{user_id}.jpg"

    await message.download(file_name=thumb_path)
    await message.reply_text("✅ Personal thumbnail saved!")


# ================= FILE DETECT ================= #

@app.on_message(filters.document)
async def detect_file(client, message):

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✏️ Rename", callback_data=f"rename|{message.id}")]]
    )

    await message.reply_text(
        f"📦 File Detected\n\n"
        f"📄 {message.document.file_name}\n"
        f"📦 {round(message.document.file_size/(1024*1024),2)} MB",
        reply_markup=keyboard
    )


# ================= CALLBACK ================= #

@app.on_callback_query()
async def rename_handler(client, query):

    data = query.data.split("|")

    if data[0] != "rename":
        return

    msg_id = int(data[1])

    original = await client.get_messages(query.message.chat.id, msg_id)

    await query.message.edit(
        "✏️ Send new file name with extension\n(example: movie.mkv)"
    )

    try:
        response = await client.listen(
            chat_id=query.message.chat.id,
            filters=filters.user(query.from_user.id),
            timeout=120
        )
    except:
        return await query.message.reply_text("❌ Time expired")

    new_name = response.text

    processing = await query.message.reply_text("Starting...")

    # ---------- DOWNLOAD ----------

    start = time.time()

    file_path = await original.download(
        progress=progress,
        progress_args=(processing, start, "Downloading")
    )

    new_file = os.path.join(os.path.dirname(file_path), new_name)

    os.rename(file_path, new_file)

    # ---------- UPLOAD ----------

    start = time.time()

    user_id = str(query.from_user.id)
    thumb_path = f"{THUMB_FOLDER}/{user_id}.jpg"

    mime, _ = mimetypes.guess_type(new_name)

    if mime and mime.startswith("video"):

        await query.message.reply_video(
            video=new_file,
            caption="✅ File Renamed Successfully!",
            thumb=thumb_path if os.path.exists(thumb_path) else None,
            progress=progress,
            progress_args=(processing, start, "Uploading")
        )

    else:
        await query.message.reply_document(
            document=new_file,
            file_name=new_name,
            caption="✅ File Renamed Successfully!",
            thumb=thumb_path if os.path.exists(thumb_path) else None,
            progress=progress,
            progress_args=(processing, start, "Uploading")
        )

    os.remove(new_file)

    await processing.delete()


app.run()
