from os import remove
import requests
from pyrogram import filters
from Database.mongodb.toggle_mongo import is_nsfw_on, nsfw_off, nsfw_on
from Mikobot import BOT_USERNAME, DRAGONS, app
from Mikobot.utils.can_restrict import can_restrict
from Mikobot.utils.errors import capture_err

# Sightengine API credentials
API_USER = "1406815393"
API_SECRET = "Ni2VcsEKGXwaxbLBvtks3psaAnvPaanG"

# <================================================ FUNCTION =======================================================>
async def get_file_id_from_message(message):
    file_id = None
    if message.document:
        if int(message.document.file_size) > 3145728:
            return
        mime_type = message.document.mime_type
        if mime_type not in ("image/png", "image/jpeg"):
            return
        file_id = message.document.file_id

    if message.sticker:
        if message.sticker.is_animated:
            if not message.sticker.thumbs:
                return
            file_id = message.sticker.thumbs[0].file_id
        else:
            file_id = message.sticker.file_id

    if message.photo:
        file_id = message.photo.file_id

    if message.animation:
        if not message.animation.thumbs:
            return
        file_id = message.animation.thumbs[0].file_id

    if message.video:
        if not message.video.thumbs:
            return
        file_id = message.video.thumbs[0].file_id
    return file_id

# Function to scan NSFW content using Sightengine API
async def scan_nsfw_with_sightengine(file):
    # Upload file to Sightengine API
    response = requests.post(
        "https://api.sightengine.com/1.0/check.json",
        params={
            "models": "nudity",
            "api_user": API_USER,
            "api_secret": API_SECRET,
        },
        files={"image": file},
    )

    # Check the response
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

@app.on_message(
    (
        filters.document
        | filters.photo
        | filters.sticker
        | filters.animation
        | filters.video
    )
    & ~filters.private,
    group=8,
)
@capture_err
async def detect_nsfw(_, message):
    if not await is_nsfw_on(message.chat.id):
        return
    if not message.from_user:
        return
    file_id = await get_file_id_from_message(message)
    if not file_id:
        return
    file = await _.download_media(file_id)
    
    try:
        # Scan NSFW using Sightengine
        results = await scan_nsfw_with_sightengine(file)
    except Exception:
        return
    
    if not results:
        return
    
    remove(file)
    
    # Extract results from Sightengine API
    nsfw_score = results.get('nudity', {}).get('safe', 0)
    
    if message.from_user.id in DRAGONS:
        return
    
    if nsfw_score < 0.7:  # 70% confidence for NSFW
        return
    
    try:
        await message.delete()
    except Exception:
        return
    
    await message.reply_text(
        f"""
**🔞 NSFW Image Detected & Deleted Successfully!**

**✪ User:** {message.from_user.mention} [`{message.from_user.id}`]
**✪ Safe:** `{results.get('nudity', {}).get('safe', 0)} %`
**✪ Porn:** `{results.get('nudity', {}).get('porn', 0)} %`
**✪ Adult:** `{results.get('nudity', {}).get('sexy', 0)} %`
"""
    )


@app.on_message(filters.command(["nsfwscan", f"nsfwscan@{BOT_USERNAME}"]))
@capture_err
async def nsfw_scan_command(_, message):
    if not message.reply_to_message:
        await message.reply_text(
            "Reply to an image/document/sticker/animation to scan it."
        )
        return
    reply = message.reply_to_message
    if (
        not reply.document
        and not reply.photo
        and not reply.sticker
        and not reply.animation
        and not reply.video
    ):
        await message.reply_text(
            "Reply to an image/document/sticker/animation to scan it."
        )
        return
    m = await message.reply_text("Scanning")
    file_id = await get_file_id_from_message(reply)
    if not file_id:
        return await m.edit("Something wrong happened.")
    file = await _.download_media(file_id)
    
    try:
        # Scan NSFW using Sightengine
        results = await scan_nsfw_with_sightengine(file)
    except Exception:
        return
    
    remove(file)
    
    if not results:
        return await m.edit("Failed to scan the image.")
    
    nsfw_score = results.get('nudity', {}).get('safe', 0)
    
    await m.edit(
        f"""
**➢ Safe:** `{results.get('nudity', {}).get('safe', 0)} %`
**➢ Porn:** `{results.get('nudity', {}).get('porn', 0)} %`
**➢ Adult:** `{results.get('nudity', {}).get('sexy', 0)} %`
**➢ NSFW:** `{nsfw_score >= 0.7}`
"""
    )


@app.on_message(
    filters.command(["antinsfw", f"antinsfw@{BOT_USERNAME}"]) & ~filters.private
)
@can_restrict
async def nsfw_enable_disable(_, message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /antinsfw [on/off]")
        return
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    if status in ("on", "yes"):
        if await is_nsfw_on(chat_id):
            await message.reply_text("Antinsfw is already enabled.")
            return
        await nsfw_on(chat_id)
        await message.reply_text(
            "Enabled AntiNSFW System. I will Delete Messages Containing Inappropriate Content."
        )
    elif status in ("off", "no"):
        if not await is_nsfw_on(chat_id):
            await message.reply_text("Antinsfw is already disabled.")
            return
        await nsfw_off(chat_id)
        await message.reply_text("Disabled AntiNSFW System.")
    else:
        await message.reply_text("Unknown Suffix, Use /antinsfw [on/off]")


# <=================================================== HELP ====================================================>


__mod_name__ = "ANTI-NSFW"

__help__ = """
*🔞 Helps in detecting NSFW material and removing it*.

➠ *Usage:*

» /antinsfw [on/off]: Enables Anti-NSFW system.

» /nsfwscan <reply to message>: Scans the file replied to.
"""
# <================================================ END =======================================================>
