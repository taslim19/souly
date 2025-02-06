from pyrogram import filters
from MukeshAPI import api  # Import MukeshAPI

from Mikobot import app
from Mikobot.state import state

import os
import google.generativeai as genai

# Remove the Gemini API key configuration
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

    try:
        # Use MukeshAPI instead of Gemini API to generate a response
        response = api.query(query)  # MukeshAPI call

        # Extract the reply text from MukeshAPI response
        reply_text = response["result"]  # Assuming MukeshAPI returns a dictionary with 'result'

    except Exception as e:
        reply_text = f"Error: An error occurred while calling the MukeshAPI. {e}"

    # Delete the "giving results" message
    await result_msg.delete()

    # Send the chatbot response to the user
    await message.reply(reply_text)


help = """
➦ *Write Miko with any sentence it will work as chatbot.*

*Example*: Miko are you a bot?
"""

mod_name = "CHATBOT"
