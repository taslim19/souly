from pyrogram import filters

from Mikobot import app
from Mikobot.state import state

import os
import google.generativeai as genai

# Configuration
PALM_API_URL = "https://lexica.qewertyy.dev/models" 
MODEL_ID = 5 



@app.on_message(filters.text)
async def handle_message(client, message):
    if not message.text.startswith("Miko"):
        return

    query = " ".join(message.text.split()[1:])

    if not query:
        await message.reply("Please provide a query after Miko.")
        return

    # Send the "giving results" message first
    result_msg = await message.reply("🔍")

    try:
        # Use the Gemini API to generate a response
        genai.configure(api_key="AIzaSyB4CnCcJKXSlKyYbNu-loj6LoKFkceedps") 
        model = genai.GenerativeModel("gemini-1.5-pro") 
        response = model.generate_content(f"Generate a response to the following query: {query}") 

    except Exception as e:
        response = f"Error: An error occurred while calling the Gemini API. {e}"

    # Delete the "giving results" message
    await result_msg.delete()

    # Send the chatbot response to the user
    await message.reply(response)

app.run()


__help__ = """
➦ *Write Miko with any sentence it will work as chatbot.*

*Example*: Miko are you a bot?
"""

__mod_name__ = "CHATBOT"
