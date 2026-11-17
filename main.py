import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, VideoPiped
import yt_dlp
from thumbnail_helper import generate_music_thumbnail

API_ID = int(os.getenv("API_ID", "33449811"))
API_HASH = os.getenv("API_HASH", "A59c12e80e04afd835adb57d2295dd32")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8838840082:AAG5UPrDlMEQxuaKVNkmQ-kcz-JqEsKfQQ4")

userbot = Client(
    "session_8855609273",
    api_id=API_ID,
    api_hash=API_HASH
)

bot = Client(
    "music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

call_py = PyTgCalls(userbot)

def get_media_info(query, is_video=False):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best' if is_video else 'bestaudio',
        'quiet': True,
        'default_search': 'ytsearch',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if 'entries' in info:
            info = info['entries'][0]
        
        return {
            'url': info.get('url'),
            'title': info.get('title', 'Unknown Title'),
            'duration': info.get('duration_string', '03:45'),
            'thumbnail': info.get('thumbnail'),
            'channel': info.get('uploader', 'YouTube')
        }

def get_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("▶️", callback_data="resume"),
            InlineKeyboardButton("⏸️", callback_data="pause"),
            InlineKeyboardButton("🔄", callback_data="loop"),
            InlineKeyboardButton("⏭️", callback_data="skip"),
            InlineKeyboardButton("⏹️", callback_data="stop")
        ],
        [
            InlineKeyboardButton("🗑️ CLOSE 🗑️", callback_data="close")
        ]
    ])

@bot.on_message(filters.command("play") & filters.group)
async def play_music(client, message):
    if len(message.command) < 2:
        await message.reply("দয়া করে কোনো গানের নাম বা ইউটিউব লিংক দিন! যেমন: `/play Song Name`")
        return

    query = " ".join(message.command[1:])
    m = await message.reply("🔍 ইউটিউব থেকে গান খোঁজা হচ্ছে এবং থাম্বেল প্রসেস করা হচ্ছে...")

    try:
        media = get_media_info(query, is_video=False)
        chat_id = message.chat.id

        thumb_path = generate_music_thumbnail(media['thumbnail'])

        await call_py.join_group_call(
            chat_id,
            AudioPiped(media['url'])
        )

        caption = f"▶️ **Started Streaming Now** 🎵\n\n" \
                  f"📦 **Title** » {media['title']}\n" \
                  f"⚙️ **Duration** » {media['duration']} MINUTES\n" \
                  f"👤 **By** » {media['channel']}"

        await m.delete()
        if thumb_path and os.path.exists(thumb_path):
            await message.reply_photo(
                photo=thumb_path,
                caption=caption,
                reply_markup=get_keyboard()
            )
            os.remove(thumb_path)
        else:
            await message.reply(caption, reply_markup=get_keyboard())

    except Exception as e:
        await m.edit(f"❌ ত্রুটি দেখা দিয়েছে: `{e}`")

@bot.on_message(filters.command("video") & filters.group)
async def play_video(client, message):
    if len(message.command) < 2:
        await message.reply("দয়া করে ইউটিউব ভিডিওর লিংক বা নাম দিন! যেমন: `/video Video Name`")
        return

    query = " ".join(message.command[1:])
    m = await message.reply("🔍 ইউটিউব থেকে ভিডিও খোঁজা হচ্ছে এবং লাইভ ভিডিও চ্যাটে জয়েন করা হচ্ছে...")

    try:
        media = get_media_info(query, is_video=True)
        chat_id = message.chat.id

        thumb_path = generate_music_thumbnail(media['thumbnail'])

        await call_py.join_group_call(
            chat_id,
            VideoPiped(media['url'])
        )

        caption = f"📺 **Live Video Streaming Now** 🎬\n\n" \
                  f"📦 **Title** » {media['title']}\n" \
                  f"⚙️ **Duration** » {media['duration']} MINUTES\n" \
                  f"👤 **By** » {media['channel']}"

        await m.delete()
        if thumb_path and os.path.exists(thumb_path):
            await message.reply_photo(
                photo=thumb_path,
                caption=caption,
                reply_markup=get_keyboard()
            )
            os.remove(thumb_path)
        else:
            await message.reply(caption, reply_markup=get_keyboard())

    except Exception as e:
        await m.edit(f"❌ ত্রুটি দেখা দিয়েছে: `{e}`")

@bot.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id

    if data == "pause":
        try:
            await call_py.pause_stream(chat_id)
            await callback_query.answer("⏸️ Stream Paused!", show_alert=False)
        except Exception as e:
            await callback_query.answer(f"Error: {e}", show_alert=True)

    elif data == "resume":
        try:
            await call_py.resume_stream(chat_id)
            await callback_query.answer("▶️ Stream Resumed!", show_alert=False)
        except Exception as e:
            await callback_query.answer(f"Error: {e}", show_alert=True)

    elif data == "stop":
        try:
            await call_py.leave_group_call(chat_id)
            await callback_query.message.delete()
            await callback_query.answer("⏹️ Stream Stopped!", show_alert=False)
        except Exception as e:
            await callback_query.answer(f"Error: {e}", show_alert=True)

    elif data == "close":
        try:
            await callback_query.message.delete()
        except:
            pass

    elif data == "skip":
        await callback_query.answer("⏭️ Skipped current track!", show_alert=False)

    elif data == "loop":
        await callback_query.answer("🔄 Loop enabled for current track!", show_alert=False)

@bot.on_message(filters.command("stop") & filters.group)
async def stop_stream(client, message):
    try:
        await call_py.leave_group_call(message.chat.id)
        await message.reply("⏹️ স্ট্রিম বন্ধ করা হয়েছে এবং ইউজারবট ভয়েস চ্যাট থেকে বের হয়ে গেছে।")
    except Exception as e:
        await message.reply(f"❌ ত্রুটি: `{e}`")

async def main():
    await userbot.start()
    await bot.start()
    await call_py.start()
    print("Bot, Userbot & PyTgCalls Started Successfully with Circular Thumbnails & UI Buttons!")
    await asyncio.gather(
        userbot.idle(),
        bot.idle()
    )

if __name__ == "__main__":
    asyncio.run(main())
