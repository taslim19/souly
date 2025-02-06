from pyrogram import filters
import google.generativeai as genai  # Using Gemini API

from Mikobot import app
from Mikobot.state import state

import requests
from pyrogram.enums import ChatAction

@app.on_message(filters.text)
async def palm_chatbot(client, message):
    if not message.text.startswith("flash"):
        return

    query = " ".join(message.text.split()[1:])

    if not query:
        await message.reply("Please provide a query after flash.")
        return

    # Send the "giving results" message first
    result_msg = await message.reply("🔥")
    await app.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        # Use Gemini Flash 2.0 (Assuming this works with Google Generative AI API or a similar method)
        genai.configure(api_key="AIzaSyBM0m9lnb1GlbnWcGWDe0otQ-aVnpIF974")  # Make sure to use your valid API key
        model = genai.GenerativeModel("gemini-2.0")  # Or the appropriate model for Gemini Flash 2.0
        response = model.generate_content(f"Generate a response to the following query: {query}")

        # Extract only the reply text 
        reply_text = response.candidates[0].content.parts[0].text

        if reply_text:
            await message.reply(reply_text)  # Send the response to the user
        else:
            await message.reply("Sorry, I couldn't find an answer. Please try again.")

    except Exception as e:
        await message.reply(f"Error: An error occurred while calling the Gemini Flash 2.0 API. {e}")

    # Delete the "giving results" message
    await result_msg.delete()


help = """
➦ *Write Miko with any sentence it will work as chatbot.*

*Example*: Miko are you a bot?
"""

mod_name = "CHATBOT"
