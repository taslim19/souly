# <============================================== IMPORTS =========================================================>
import os
import re
from html import escape
from random import choice

from telegram import (
    ChatMemberAdministrator,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ChatID, ChatType, ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, ContextTypes
from telegram.helpers import mention_html

from Database.sql.approve_sql import is_approved
from Infamous.karma import START_IMG
from Mikobot import DEV_USERS, DRAGONS, INFOPIC, OWNER_ID, function
from Mikobot.__main__ import STATS, USER_INFO
from Mikobot.plugins.helper_funcs.chat_status import support_plus
from Mikobot.plugins.users import get_user_id

# <=======================================================================================================>


# <================================================ FUNCTION =======================================================>
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.effective_message
    args = context.args
    bot = context.bot

    def reply_with_text(text):
        return message.reply_text(text, parse_mode=ParseMode.HTML)

    head = ""
    premium = False

    reply = await reply_with_text("<code>Getting information...</code>")

    user_id = None
    user_name = None

    if len(args) >= 1:
        if args[0][0] == "@":
            user_name = args[0]
            user_id = await get_user_id(user_name)

        if not user_id:
            try:
                chat_obj = await bot.get_chat(user_name)
                userid = chat_obj.id
            except BadRequest:
                await reply_with_text(
                    "I can't get information about this user/channel/group."
                )
                return
        else:
            userid = user_id
    elif len(args) >= 1 and args[0].lstrip("-").isdigit():
        userid = int(args[0])
    elif message.reply_to_message and not message.reply_to_message.forum_topic_created:
        if message.reply_to_message.sender_chat:
            userid = message.reply_to_message.sender_chat.id
        elif message.reply_to_message.from_user:
            if message.reply_to_message.from_user.id == ChatID.FAKE_CHANNEL:
                userid = message.reply_to_message.chat.id
            else:
                userid = message.reply_to_message.from_user.id
                premium = message.reply_to_message.from_user.is_premium
    elif not message.reply_to_message and not args:
        if message.from_user.id == ChatID.FAKE_CHANNEL:
            userid = message.sender_chat.id
        else:
            userid = message.from_user.id
            premium = message.from_user.is_premium

    try:
        chat_obj = await bot.get_chat(userid)
    except (BadRequest, UnboundLocalError):
        await reply_with_text("I can't get information about this user/channel/group.")
        return

    if chat_obj.type == ChatType.PRIVATE:
        if chat_obj.username:
            head = f"⇨【 USER INFORMATION 】⇦\n\n"
            if chat_obj.username.endswith("bot"):
                head = f"⇨【 BOT INFORMATION 】⇦\n\n"

        head += f"➲ ID: {chat_obj.id}"
        head += f"\n➲ First Name: {chat_obj.first_name}"
        if chat_obj.last_name:
            head += f"\n➲ Last Name: {chat_obj.last_name}"
        if chat_obj.username:
            head += f"\n➲ Username: @{chat_obj.username}"
        head += f"\n➲ Permalink: {mention_html(chat_obj.id, 'link')}"

        if chat_obj.username and not chat_obj.username.endswith("bot"):
            head += f"\n\n💎 Premium User: {premium}"

        if chat_obj.bio:
            head += f"\n\n➲ Bio: {chat_obj.bio}"

        chat_member = await chat.get_member(chat_obj.id)
        if isinstance(chat_member, ChatMemberAdministrator):
            head += f"\n➲ Presence: {chat_member.status}"
            if chat_member.custom_title:
                head += f"\n➲ Admin Title: {chat_member.custom_title}"
        else:
            head += f"\n➲ Presence: {chat_member.status}"

        if is_approved(chat.id, chat_obj.id):
            head += f"\n➲ Approved: This user is approved in this chat."

        disaster_level_present = False

        if chat_obj.id == OWNER_ID:
            head += "\n\n👑 The disaster level of this person is My Owner."
            disaster_level_present = True
        elif chat_obj.id in DEV_USERS:
            head += "\n\n🐉 This user is a member of Infamous Hydra."
            disaster_level_present = True
        elif chat_obj.id in DRAGONS:
            head += "\n\n🐲 The disaster level of this person is Dragon."
            disaster_level_present = True
        if disaster_level_present:
            head += " [?]"

        for mod in USER_INFO:
            try:
                mod_info = mod.__user_info__(chat_obj.id).strip()
            except TypeError:
                mod_info = mod.__user_info__(chat_obj.id, chat.id).strip()

            head += "\n\n" + mod_info if mod_info else ""

    if chat_obj.type == ChatType.SENDER:
        head = f"📨 Sender Chat Information:\n"
        await reply_with_text("Found sender chat, getting information...")
        head += f"ID: {chat_obj.id}"
        if chat_obj.title:
            head += f"\n🏷️ Title: {chat_obj.title}"
        if chat_obj.username:
            head += f"\n📧 Username: @{chat_obj.username}"
        head += f"\n🔗 Permalink: {mention_html(chat_obj.id, 'link')}"
        if chat_obj.description:
            head += f"\n📝 Description: {chat_obj.description}"

    elif chat_obj.type == ChatType.CHANNEL:
        head = f"Channel Information:\n"
        await reply_with_text("Found channel, getting information...")
        head += f"<b>ID:</b> {chat_obj.id}</code>"
        if chat_obj.title:
            head += f"\n<b>Title:</b> {chat_obj.title}"
        if chat_obj.username:
            head += f"\n<b>Username:</b> @{chat_obj.username}"
        head += f"\nPermalink: {mention_html(chat_obj.id, 'link')}"
        if chat_obj.description:
            head += f"\n<b>Description:</b> {chat_obj.description}"
        if chat_obj.linked_chat_id:
            head += f"\n<b>Linked Chat ID:</b> <code>{chat_obj.linked_chat_id}</code>"

    elif chat_obj.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        head = f"Group Information:\n"
        await reply_with_text("Found group, getting information...")
        head += f" ID: <code>{chat_obj.id}</code>"
        if chat_obj.title:
            head += f"\n Title:</b> {chat_obj.title}"
        if chat_obj.username:
            head += f"\n Username: @{chat_obj.username}"
        head += f"\nPermalink: {mention_html(chat_obj.id, 'link')}"
        if chat_obj.description:
            head += f"\n<b>Description:  {chat_obj.description}"

    if INFOPIC:
        try:
            if chat_obj.photo:
                _file = await chat_obj.photo.get_big_file()
                await _file.download_to_drive(f"{chat_obj.id}.png")
                await message.reply_photo(
                    photo=open(f"{chat_obj.id}.png", "rb"),
                    caption=(head),
                    parse_mode=ParseMode.HTML,
                )
                await reply.delete()
                os.remove(f"{chat_obj.id}.png")
            else:
                await reply_with_text(escape(head))
        except:
            await reply_with_text(escape(head))


@support_plus
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = "📊 <b>ʀᴇsᴏʟᴜᴛᴇ ᴅᴇғᴇɴᴅᴇʀ Bᴏᴛ's Sᴛᴀᴛɪsᴛɪᴄs:</b>\n\n" + "\n".join(
        [mod.__stats__() for mod in STATS]
    )
    result = re.sub(r"(\d+)", r"<code>\1</code>", stats)

    keyboard = [
        [
            InlineKeyboardButton(
                "𝑟𝑒𝑠𝑜𝑙𝑢𝑡𝑒 𝑑𝑒𝑓𝑒𝑛𝑑𝑒𝑟", url="https://t.me/Serene_Swordsman"
            ),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_message.reply_photo(
        photo=str(choice(START_IMG)),
        caption=result,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
    )


# <=================================================== HELP ====================================================>


__help__ = """
*Overall information about user:*

» /info : Fetch user information.

» /uinfo : Fetch user information in banner.
"""

# <================================================ HANDLER =======================================================>
STATS_HANDLER = CommandHandler(["stats", "gstats"], stats, block=False)
INFO_HANDLER = CommandHandler(("info", "book"), info, block=False)

function(STATS_HANDLER)
function(INFO_HANDLER)

__mod_name__ = "INFO"
__command_list__ = ["info"]
__handlers__ = [INFO_HANDLER, STATS_HANDLER]
# <================================================ END =======================================================>
