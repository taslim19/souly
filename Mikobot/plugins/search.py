

# <============================================== IMPORTS =========================================================>
import json
import random
import aiohttp

from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto, Message

from Mikobot import app
from Mikobot.state import state
import logging

logging.basicConfig(level=logging.DEBUG)
# <======================================== CONFIGURATION =========================================================>
# Centralized configuration for API settings
API_CONFIG = {
    "news_api": {
        "url": "https://newsapi.org/v2/everything?q={}&apiKey={api_key}",
        "api_key": "a66730fffb6b4d5c9a9db2a69ad1f9b5",
    },
    "bing_search_api": {
        "url": "https://api.bing.microsoft.com/v7.0/search?q={query}",
        "api_key": "YOUR_BING_SEARCH_API_KEY",
    },
    "bing_image_api": {
        "url": "https://api.bing.microsoft.com/v7.0/images/search?q={query}",
        "api_key": "YOUR_BING_IMAGE_API_KEY",
    },
    "google_image_api": {
        "url": "https://customsearch.googleapis.com/customsearch/v1?q={query}&searchType=image&key={api_key}",
        "api_key": "AIzaSyAwq2Vx4lyuXv6ZcZNjbws2v8Jhl0nAAmA",
        "cx": "a364d574f6cea4fc9",
    },
}

# <================================================ FUNCTION =======================================================>

@app.on_message(filters.command("news"))
async def news(_, message: Message):
    keyword = message.text.split(" ", 1)[1].strip() if len(message.text.split()) > 1 else ""
    api_url = API_CONFIG["news_api"]["url"].format(keyword, api_key=API_CONFIG["news_api"]["api_key"])

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                print(f"Response Status Code: {response.status}")
                if response.status != 200:
                    await message.reply_text(f"API Error: {response.status}")
                    return
                
                news_data = await response.json()
                print(f"Response JSON: {news_data}")

                if news_data.get("status") == "ok":
                    articles = news_data.get("articles", [])
                    if articles:
                        news_item = random.choice(articles)
                        title = news_item.get("title", "No title")
                        excerpt = news_item.get("description", "No description")
                        source = news_item.get("source", {}).get("name", "Unknown source")
                        relative_time = news_item.get("publishedAt", "Unknown time")
                        news_url = news_item.get("url", "#")

                        message_text = f"𝗧𝗜𝗧𝗟𝗘: {title}\n𝗦𝗢𝗨𝗥𝗖𝗘: {source}\n𝗧𝗜𝗠𝗘: {relative_time}\n𝗘𝗫𝗖𝗘𝗥𝗣𝗧: {excerpt}\n𝗨𝗥𝗟: {news_url}"
                        await message.reply_text(message_text)
                    else:
                        await message.reply_text("No news found.")
                else:
                    await message.reply_text(f"API Response Error: {news_data.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Exception occurred: {e}")
        await message.reply_text(f"An error occurred: {str(e)}")



@app.on_message(filters.command("bingsearch"))
async def bing_search(client: Client, message: Message):
    try:
        if len(message.command) == 1:
            await message.reply_text("Please provide a keyword to search.")
            return

        keyword = " ".join(message.command[1:])
        api_url = API_CONFIG["bing_search_api"]["url"].format(query=keyword)
        headers = {"Ocp-Apim-Subscription-Key": API_CONFIG["bing_search_api"]["api_key"]}

        response = await state.get(api_url, headers=headers)

        if response.status_code == 200:
            results = response.json().get("webPages", {}).get("value", [])
            if not results:
                await message.reply_text("No results found.")
            else:
                message_text = ""
                for result in results[:7]:
                    title = result.get("name", "No title")
                    link = result.get("url", "No URL")
                    message_text += f"{title}\n{link}\n\n"
                await message.reply_text(message_text.strip())
        else:
            await message.reply_text("Sorry, something went wrong with the search.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")


@app.on_message(filters.command("bingimg"))
async def bingimg_search(client: Client, message: Message):
    try:
        text = message.text.split(None, 1)[1]
    except IndexError:
        return await message.reply_text("Provide me a query to search!")

    search_message = await message.reply_text("🔎")

    api_url = API_CONFIG["bing_image_api"]["url"].format(query=text)
    headers = {"Ocp-Apim-Subscription-Key": API_CONFIG["bing_image_api"]["api_key"]}
    response = await state.get(api_url, headers=headers)

    if response.status_code == 200:
        images = response.json().get("value", [])
        if not images:
            await message.reply_text("No images found.")
            return

        media = [InputMediaPhoto(media=img["contentUrl"]) for img in images[:7]]
        await message.reply_media_group(media=media)
    else:
        await message.reply_text("An error occurred while searching for images.")

    await search_message.delete()
    await message.delete()


@app.on_message(filters.command("googleimg"))
async def googleimg_search(_, message: Message):
    logging.debug("Google Image Search command invoked")
    try:
        query = message.text.split(None, 1)[1].strip() if len(message.text.split()) > 1 else None
        if not query:
            logging.debug("No query provided")
            return await message.reply_text("Please provide a search query!")

        logging.debug(f"Query: {query}")
        search_message = await message.reply_text("💭 Searching for images...")

        api_url = (
            f"https://www.googleapis.com/customsearch/v1"
            f"?q={query}&searchType=image&cx=YOUR_CSE_ID&key=YOUR_API_KEY&num=7"
        )
        logging.debug(f"API URL: {api_url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                logging.debug(f"API Response Status: {response.status}")
                if response.status != 200:
                    return await message.reply_text(f"Error: {response.status}")

                data = await response.json()
                logging.debug(f"API Response: {data}")

                items = data.get("items", [])
                if not items:
                    return await message.reply_text("No images found.")

                media = [InputMediaPhoto(item["link"]) for item in items[:7]]
                await message.reply_media_group(media=media)

        await search_message.delete()

    except IndexError:
        logging.exception("IndexError: No query provided")
        await message.reply_text("Provide me a query to search!")
    except Exception as e:
        logging.exception(f"Exception occurred: {str(e)}")
        await message.reply_text(f"An error occurred: {str(e)}")

# <=======================================================================================================>


# <=================================================== HELP ====================================================>
__mod_name__ = "SEARCH"

__help__ = """
💭 𝗦𝗘𝗔𝗥𝗖𝗛

➠ *Available commands:*

» /googleimg <search query>: Retrieve and display images from Google Image Search.

» /bingimg <search query>: Retrieve and display images from Bing Image Search.

» /news <search query>: Search for news articles.

» /bingsearch <search query>: Perform a Bing web search and get results with links.

➠ *Example:*
➠ `/bingsearch app`: Returns search results.
"""
# <================================================ END =======================================================>
