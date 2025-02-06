from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Mikobot import app
import google.generativeai as genai

# Configure Gemini API Key
GENAI_API_KEY = "AIzaSyBM0m9lnb1GlbnWcGWDe0otQ-aVnpIF974"
genai.configure(api_key=GENAI_API_KEY)

# Use the latest Gemini 1.5-Flash model
model = genai.GenerativeModel("gemini-1.5-flash")

# Store chatbot status per group
chatbot_enabled = {}

@app.on_message(filters.text & filters.group)
async def chatbot_handler(client: Client, message: Message):
    chat_id = message.chat.id

    # Debug: Print incoming messages
    print(f"Received message from {chat_id}: {message.text}")

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
        data = callback_query.data.split(":")
        if len(data) < 2:
            await callback_query.answer("Invalid data format.", show_alert=True)
            return

        action = data[1]
        chat_id = int(data[2])  # Ensure chat_id is a valid integer

        chatbot_enabled[chat_id] = (action == "on")

        await callback_query.edit_message_text(f"Chatbot is now {'enabled' if chatbot_enabled[chat_id] else 'disabled'}.")
        await callback_query.answer()

    except (IndexError, ValueError) as e:
        print(f"Error in callback data: {e}")
        await callback_query.answer("An error occurred. Please try again.", show_alert=True)
    except Exception as e:
        print(f"Unexpected error in callback: {e}")
        await callback_query.answer("An unexpected error occurred.", show_alert=True)

# Debugging function to check if the bot is receiving messages
@app.on_message(filters.group)
async def test_messages(client, message):
    print(f"Received message in group {message.chat.id}: {message.text}")

__help__ = """
➦ *Use /chatbot to control the chatbot in the group.*
➦ *To use the chatbot, start your message with "flash" followed by your query.*

*Example*: flash Are you a bot?
"""

__mod_name__ = "CHATBOT"
