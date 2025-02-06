from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Mikobot import app  # Make sure to import your app instance
import os
import google.generativeai as genai

# Store chatbot status per group (replace with a database in production)
chatbot_enabled = {}

# Environment variable for API key (highly recommended)
genai.configure(api_key=os.environ.get("AIzaSyBM0m9lnb1GlbnWcGWDe0otQ-aVnpIF974"))
model = genai.GenerativeModel("gemini-1.5-pro")

@app.on_message(filters.text & filters.group)
async def chatbot_menu_handler(client: Client, message: Message):
    if message.text.startswith("/chatbot"):
        chat_id = message.chat.id
        status = chatbot_enabled.get(chat_id, False)  # Get current status
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Turn On", callback_data=f"chatbot_on:{chat_id}"),
                InlineKeyboardButton("Turn Off", callback_data=f"chatbot_off:{chat_id}"),
            ]
        ])
        await message.reply("Chatbot Control:", reply_markup=keyboard)
        return  # Stop further processing of this message


@app.on_callback_query(filters.regex("^chatbot_(on|off):"))
async def chatbot_toggle(client: Client, callback_query):
    try:
        data = callback_query.data.split(":")
        action = data[1]
        chat_id = int(data[2])  # Convert to int here

        if action == "on":
            chatbot_enabled[chat_id] = True
        elif action == "off":
            chatbot_enabled[chat_id] = False

        await callback_query.edit_message_text(f"Chatbot is now {'enabled' if chatbot_enabled.get(chat_id) else 'disabled'}")
        await callback_query.answer()
    except (IndexError, ValueError) as e:  # Handle potential errors
        print(f"Error in callback data: {e}")
        await callback_query.answer("An error occurred. Please try again.")  # More user-friendly message
    except Exception as e:
        print(f"Unexpected error in callback: {e}")
        await callback_query.answer("An unexpected error occurred.")

@app.on_message(filters.text & filters.group)  # For the "flash" command
async def palm_chatbot(client: Client, message: Message):
    if not chatbot_enabled.get(message.chat.id):
        return

    if not message.text.startswith("flash"):
        return

    query = " ".join(message.text.split()[1:])

    if not query:
        await message.reply("Please provide a query after flash.")
        return

    result_msg = await message.reply("🔥")

    try:
        response = model.generate_content(f"Generate a response to the following query: {query}")
        reply_text = response.candidates[0].content.parts[0].text

    except Exception as e:
        reply_text = f"Error: An error occurred while calling the Gemini API. {e}"
        print(f"Gemini API Error: {e}")  # Log the error

    await result_msg.delete()
    await message.reply(reply_text)


__help__ = """
➦ *Use /chatbot to control the chatbot in the group.*
➦ *To use the chatbot, start your message with "flash" followed by your query.*

*Example*: flash Are you a bot?
"""

__mod_name__ = "CHATBOT"
