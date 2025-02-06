import os
from pyrogram import filters
import google.generativeai as genai
from Mikobot import app
from pyrogram.enums import ChatAction

# 1. Secure API Key Handling (Environment Variable)
genai.configure(api_key=os.environ.get("AIzaSyBM0m9lnb1GlbnWcGWDe0otQ-aVnpIF974"))  # Set GEMINI_API_KEY in your environment

@app.on_message(filters.text)
async def palm_chatbot(client, message):
    if not message.text.startswith("flash"):
        return

    query = " ".join(message.text.split()[1:])

    if not query:
        await message.reply("Please provide a query after flash.")
        return

    result_msg = await message.reply("🔥")
    await app.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        # 2. List Models (Crucial)
        available_models = genai.list_models()
        gemini_model = None
        for model in available_models:
            if "gemini" in model.name.lower() and model.supported_methods and "generateContent" in model.supported_methods: # Find a Gemini model
                gemini_model = model
                break

        if not gemini_model:
            await message.reply("No suitable Gemini model found.")  # Handle the case where no models are found
            await result_msg.delete()
            return

        # 3. Use the correct model name from the list
        model = genai.GenerativeModel(gemini_model.name)

        # 4. Make the API call
        response = model.generate_content(
            contents=[{"role": "user", "parts": [{"text": f"Generate a response to the following query: {query}"}]}]
            )

        reply_text = ""
        if response.candidates:
            for candidate in response.candidates:  # Handle multiple candidates (if applicable)
                for part in candidate.content.parts:
                    if hasattr(part, 'text'):  # Check if the part has a text attribute
                        reply_text += part.text

        if reply_text:
            await message.reply(reply_text)
        else:
            await message.reply("Sorry, I couldn't find an answer. Please try again.")

    except genai.APIError as e:  # Catch specific Gemini API errors
        await message.reply(f"Gemini API Error: {e}")
    except Exception as e:  # Catch other exceptions
        await message.reply(f"An unexpected error occurred: {e}")

    await result_msg.delete()


help = """
➦ *Write Miko with any sentence it will work as chatbot.*

*Example*: Miko are you a bot?
"""

mod_name = "CHATBOT"
