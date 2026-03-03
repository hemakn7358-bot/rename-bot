from pyrogram import Client, filters
from pyrogram.types import Message
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

@app.on_message(filters.document)
async def rename_file(client, message: Message):
    file = message.document
    await message.reply_text("Send new file name with extension (example: movie.mp4)")

    new_name_msg = await client.listen(message.chat.id)
    new_name = new_name_msg.text

    await message.reply_document(
        document=file.file_id,
        file_name=new_name,
        caption="✅ File Renamed Successfully!"
    )

app.run()
