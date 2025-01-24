from pyrogram import filters
from pyrogram.enums import ParseMode

# Chat IDs where bug reports should be sent
BUG_REPORT_CHAT_IDS = [-1002287972008]

from Mikobot import app


# Define a handler for the /bug command
@app.on_message(filters.command("bug", prefixes="/"))
def bug_command_handler(client, message):
    # Check if the command is a reply
    if message.reply_to_message:
        # Get the message being replied to
        replied_message = message.reply_to_message

        # Extract message content
        content = replied_message.text or replied_message.caption or "No text provided"

        # Check if there is media content
        media_type = (
            "Media content included"
            if any(
                [replied_message.photo, replied_message.document, replied_message.video,
                 replied_message.audio, replied_message.animation]
            )
            else "No media content included"
        )

        # Handle cases where username is unavailable
        username = f"@{message.from_user.username}" if message.from_user.username else "an unknown user"

        # Handle cases where message link is unavailable
        message_link = (
            f"[Link to message]({replied_message.link})"
            if replied_message.link
            else "**Message link unavailable**"
        )

        # Prepare the report message
        report_message = (
            f"Bug reported by {username}:**\n\n"
            f"{content}\n\n"
            f"{media_type}\n\n"
            f"Message Link: {message_link}"
        )

        # Send the report message to all specified chat IDs
        for chat_id in BUG_REPORT_CHAT_IDS:
            client.send_message(chat_id, report_message, parse_mode=ParseMode.MARKDOWN)
    else:
        # If not a reply, prompt the user to reply with the command
        client.send_message(
            message.chat.id,
            "Please reply to a message using the /bug command to report an issue.",
            parse_mode=ParseMode.MARKDOWN,
        )
