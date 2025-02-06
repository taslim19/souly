import os
import requests
from pyrogram import filters

from Database.mongodb.toggle_mongo import is_nsfw_on, nsfw_off, nsfw_on
from Mikobot import BOT_USERNAME, DRAGONS, app
from Mikobot.state import arq
from Mikobot.utils.can_restrict import can_restrict
from Mikobot.utils.errors import capture_err

# Function to check NSFW content using Sightengine API
def check_nsfw(image_path):
    url = "https://api.sightengine.com/1.0/nsfw.json"
    params = {
        'api_user': '1406815393',  # Replace with your API User
        'api_secret': 'Ni2VcsEKGXwaxbLBvtks3psaAnvPaanG',  # Replace with your API Secret
    }
    with open(image_path, 'rb') as image_file:
        files = {'media': image_file}  # Corrected the form data key to 'media'
        response = requests.post(url, data=params, files=files)
        return response.json()

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
    
    # Check NSFW using the alternative method
    try:
        nsfw_result = check_nsfw(file)
    except Exception as e:
        return await message.reply_text(f"An error occurred: {str(e)}")
    
    # Extract the NSFW score
    nsfw_score = nsfw_result.get('nsfw', 0)
    
    # If the user is a "dragon", don't delete the message
    if message.from_user.id in DRAGONS:
        return
    
    # If NSFW content detected, delete the message and reply with the details
    if nsfw_score > 0.5:  # Threshold for NSFW content detection (adjustable)
        try:
            await message.delete()
        except Exception:
            return
        await message.reply_text(
            f"""
**🔞 NSFW Image Detected & Deleted Successfully!**

**✪ User:** {message.from_user.mention} [`{message.from_user.id}`]
**✪ NSFW Score:** `{nsfw_score * 100}%`
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

    # Check NSFW using the alternative method
    try:
        nsfw_result = check_nsfw(file)
    except Exception as e:
        return await m.edit(f"An error occurred: {str(e)}")
    
    # Extract the NSFW score
    nsfw_score = nsfw_result.get('nsfw', 0)
    
    await m.edit(
        f"""
**➢ NSFW Score:** `{nsfw_score * 100}%`
**➢ NSFW Detected:** `{('Yes' if nsfw_score > 0.5 else 'No')}`
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
