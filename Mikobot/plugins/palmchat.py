from pyrogram import filters
from MukeshAPI import api  # Import MukeshAPI

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
        # Use MukeshAPI's gemini method to generate a response
        response = api.gemini(query)
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)

        # Extract the response text from MukeshAPI
        reply_text = response["results"]

        if reply_text:
            await message.reply(reply_text)  # Send the response to the user
        else:
            await message.reply("Sorry, I couldn't find an answer. Please try again.")

    except requests.exceptions.RequestException as e:
        await message.reply(f"Error: An error occurred while calling the MukeshAPI. {e}")

    # Delete the "giving results" message
    await result_msg.delete()


help = """
➦ *Write Miko with any sentence it will work as chatbot.*

*Example*: Miko are you a bot?
"""

mod_name = "CHATBOT"
