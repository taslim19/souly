# <============================================== IMPORTS =========================================================>
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from telegram.error import BadRequest

from Mikobot import function, LOGGER as logger
from Mikobot.plugins.helper_funcs.chat_status import check_admin, connection_status, is_user_admin

# <=======================================================================================================>

# <================================================ BAN ALL FUNCTION =====================================================>

@connection_status
@check_admin(permission="can_restrict_members", is_both=True)
async def ban_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user
    log_message = ""
    bot = context.bot

    # Get all members in the chat
    members = await chat.get_members()
    admin_ids = [admin.user.id for admin in await chat.get_administrators()]

    for member in members:
        if member.user.id not in admin_ids and member.user.id != bot.id:
            try:
                await chat.ban_member(member.user.id)
                log_message += f"Banned {member.user.first_name} ({member.user.id})\n"
            except BadRequest as excp:
                logger.warning(f"Failed to ban {member.user.id}: {excp.message}")
                log_message += f"Failed to ban {member.user.first_name} ({member.user.id}): {excp.message}\n"

    await update.effective_message.reply_text("All non-admin members have been banned.")
    return log_message

# <================================================ HANDLER =======================================================>
# Register the ban_all command handler
function(CommandHandler("banall", ban_all, block=False))

# <================================================ END =======================================================>
