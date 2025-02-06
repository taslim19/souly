from pyrogram import filters
from Mikobot import app
import google.generativeai as genai
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus

# Store chatbot state per chat
chatbot_states = {}

def get_inline_buttons(chat_id):
    state = chatbot_states.get(chat_id, False)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "Disable Chatbot" if state else "Enable Chatbot", 
            callback_data=f"toggle_chatbot_{chat_id}")]
    ])

@app.on_message(filters.command("chatbot"))
async def chatbot(client, message):
    if message.chat.type == "private":
        await message.reply("This command can only be used in groups.")
        return

    chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if chat_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await message.reply("Sorry, only group admins can use this command.")
        return

    await message.reply("Click the button to enable or disable the chatbot:", reply_markup=get_inline_buttons(message.chat.id))

@app.on_callback_query(filters.regex("toggle_chatbot_"))
async def toggle_chatbot(client, callback_query):
    chat_id = int(callback_query.data.split("_")[-1])
    chatbot_states[chat_id] = not chatbot_states.get(chat_id, False)
    state_text = "enabled" if chatbot_states[chat_id] else "disabled"
    await callback_query.message.edit(f"Chatbot is now {state_text}!", reply_markup=get_inline_buttons(chat_id))
    await callback_query.answer()

@app.on_message(filters.text)
async def palm_chatbot(client, message):
    if not chatbot_states.get(message.chat.id, False):
        return
    
    if not message.text.startswith("flash"):
        return

    query = " ".join(message.text.split()[1:])
    if not query:
        await message.reply("Please provide a query after 'flash'.")
        return

    result_msg = await message.reply("🔥")

    try:
        genai.configure(api_key="AIzaSyBM0m9lnb1GlbnWcGWDe0otQ-aVnpIF974")
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(query)
        reply_text = response.candidates[0].content.parts[0].text
    except Exception as e:
        reply_text = f"Error: An error occurred while calling the Gemini API. {e}"
    
    await result_msg.delete()
    await message.reply(reply_text)

help = """
➦ *Write 'flash' with any sentence, and it will work as a chatbot.*

*Example*: flash are you a bot?
"""
mod_name = "CHATBOT"
