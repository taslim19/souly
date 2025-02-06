from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Mikobot import app
from Mikobot.state import state  # Assuming this is where you store group settings
import os
import google.generativeai as genai

# Store chatbot status per group (replace with a database in production)
chatbot_enabled = {}

# Environment variable for API key
genai.configure(api_key=os.environ.get("AIzaSyBM0m9lnb1GlbnWcGWDe0otQ-aVnpIF974"))
model = genai.GenerativeModel("gemini-1.5-pro")

@app.on_message(filters.command("chatbot") & filters.group)
async def chatbot_menu(client: Client, message: Message):
    if message.from_user and message.from_user.id in await client.get_chat_administrators(message.chat.id):
        status = chatbot_enabled.get(message.chat.id, False)  # Get current status or False if not set
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Turn On", callback_data=f"chatbot_on:{message.chat.id}"),
                InlineKeyboardButton("Turn Off", callback_data=f"chatbot_off:{message.chat.id}"),
            ]
        ])
        await message.reply("Chatbot Control:", reply_markup=keyboard)
    else:
        await message.reply("You must be an admin to use this command.")


@app.on_callback_query(filters.regex("^chatbot_(on|off):"))
async def chatbot_toggle(client: Client, callback_query):
    data = callback_query.data.split(":")
    action = data[1]
    chat_id = int(data[2])  # Important: Convert chat_id to integer

    if callback_query.from_user.id in await client.get_chat_administrators(chat_id):
        if action == "on":
            chatbot_enabled[chat_id] = True
        elif action == "off":
            chatbot_enabled[chat_id] = False

        await callback_query.edit_message_text(f"Chatbot is now {'enabled' if chatbot_enabled.get(chat_id) else 'disabled'}")
        await callback_query.answer()  # Acknowledge the button press
    else:
        await callback_query.answer("You are not an admin.")


@app.on_message(filters.text & filters.group)
async def palm_chatbot(client: Client, message: Message):
    if not chatbot_enabled.get(message.chat.id):
        return

    # ... (rest of the palm_chatbot function remains the same)
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
➦ *Use /chatbot to control the chatbot in the group (admins only).*
➦ *To use the chatbot, start your message with "flash" followed by your query.*

*Example*: flash Are you a bot?
"""

__mod_name__ = "CHATBOT"
