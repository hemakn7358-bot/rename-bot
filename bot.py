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


# ================= PROGRESS FUNCTION ================= #

async def progress(current, total, message, start, action):
    now = time.time()
    diff = now - start

    if diff < 1:
        return

    percentage = current * 100 / total
    speed = current / diff
    eta = round((total - current) / speed) if speed > 0 else 0

    bar_length = 20
    filled_length = int(bar_length * current // total)
    bar = "■" * filled_length + "□" * (bar_length - filled_length)

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
                InlineKeyboardButton(
                    "✏️ Rename",
                    callback_data=f"rename_{message.id}"
                ),
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


# ================= CALLBACK HANDLER ================= #

@app.on_callback_query()
async def callback_handler(client, query: CallbackQuery):

    if query.data == "cancel":
        return await query.message.edit("❌ Cancelled.")

    if query.data.startswith("rename_"):

        file_message_id = int(query.data.split("_")[1])

        original = await client.get_messages(
            chat_id=query.message.chat.id,
            message_ids=file_message_id
        )

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
            return await query.message.edit("❌ Time expired.")

        new_name = response.text

        processing = await query.message.reply_text("Starting...")

        # ---------- DOWNLOAD ----------
        start = time.time()

        file_path = await original.download(
            progress=progress,
            progress_args=(processing, start, "Downloading")
        )

        # Rename locally
        new_file_path = os.path.join(
            os.path.dirname(file_path),
            new_name
        )
        os.rename(file_path, new_file_path)

        # ---------- UPLOAD ----------
        start = time.time()

        user_id = str(query.from_user.id)
        thumb_path = f"{THUMB_FOLDER}/{user_id}.jpg"

        mime_type, _ = mimetypes.guess_type(new_name)

        if mime_type and mime_type.startswith("video"):
            await query.message.reply_video(
                video=new_file_path,
                caption="✅ File Renamed Successfully!",
                thumb=thumb_path if os.path.exists(thumb_path) else None,
                progress=progress,
                progress_args=(processing, start, "Uploading")
            )
        else:
            await query.message.reply_document(
                document=new_file_path,
                file_name=new_name,
                caption="✅ File Renamed Successfully!",
                thumb=thumb_path if os.path.exists(thumb_path) else None,
                progress=progress,
                progress_args=(processing, start, "Uploading")
            )

        os.remove(new_file_path)
        await processing.delete()


app.run()            )
        else:
            await query.message.reply_document(
                document=new_file_path,
                file_name=new_name,
                caption="✅ File Renamed Successfully!",
                thumb=thumb_path if os.path.exists(thumb_path) else None,
                progress=progress,
                progress_args=(processing, start, "Uploading")
            )

        os.remove(new_file_path)
        await processing.delete()
        #========= FILE DETECT ================= #




# ================= BUTTON HANDLER ================= #

import mimetypes

import time

async def progress(current, total, message, start, action):
    now = time.time()
    diff = now - start

    if diff < 1:
        return

    percentage = current * 100 / total
    speed = current / diff
    eta = round((total - current) / speed) if speed > 0 else 0

    bar_length = 20
    filled_length = int(bar_length * current // total)
    bar = "■" * filled_length + "□" * (bar_length - filled_length)

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
