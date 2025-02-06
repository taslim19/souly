from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Mikobot import app
import google.generativeai as genai

# Configure Gemini API Key directly
GENAI_API_KEY = "AIzaSyBM0m9lnb1GlbnWcGWDe0otQ-aVnpIF974"
genai.configure(api_key=GENAI_API_KEY)

# Use the latest Gemini 1.5-Flash model
model = genai.GenerativeModel("gemini-1.5-flash")

# Store chatbot status per group (Consider using a database in production)
chatbot_enabled = {}

@app.on_message(filters.text & filters.group)
async def chatbot_handler(client: Client, message: Message):
    chat_id = message.chat.id

    if message.text.startswith("/chatbot"):
        if not message.from_user:
            await message.reply("This command can only be used by group members.")
            return

        status = chatbot_enabled.get(chat_id, False)
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Turn On", callback_data=f"chatbot_on:{chat_id}"),
                InlineKeyboardButton("Turn Off", callback_data=f"chatbot_off:{chat_id}"),
            ]
        ])
        await message.reply("Chatbot Control:", reply_markup=keyboard)
        return

    if chatbot_enabled.get(chat_id) and message.text.startswith("flash"):
        query = " ".join(message.text.split()[1:])
        if not query:
            await message.reply("Please provide a query after 'flash'.")
            return

        result_msg = await message.reply("🔥 Generating response...")

        try:
            response = model.generate_content(query)
            reply_text = response.text if hasattr(response, "text") else "I couldn't generate a response."
        except Exception as e:
            reply_text = f"Error: Unable to fetch a response. {e}"
            print(f"Gemini API Error: {e}")

        await result_msg.delete()
        await message.reply(reply_text)

@app.on_callback_query(filters.regex("^chatbot_(on|off):"))
async def chatbot_toggle(client: Client, callback_query):
    try:
        action, chat_id = callback_query.data.split(":")[1], int(callback_query.data.split(":")[2])
        chatbot_enabled[chat_id] = (action == "on")
        await callback_query.edit_message_text(f"Chatbot is now {'enabled' if chatbot_enabled[chat_id] else 'disabled'}.")
        await callback_query.answer()
    except Exception as e:
        print(f"Error: {e}")
        await callback_query.answer("An error occurred. Please try again.")

__help__ = """
➦ *Use /chatbot to control the chatbot in the group.*
➦ *To use the chatbot, start your message with "flash" followed by your query.*

*Example*: flash Are you a bot?
"""

__mod_name__ = "CHATBOT"
