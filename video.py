import requests
from datetime import datetime
from status import format_progress_bar
import asyncio
import os, time
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def download_video(url, reply_msg, user_mention, user_id):
    # Try multiple APIs for better reliability
    apis = [
        f"https://teraboxvideodownloader.nepcoderdevs.workers.dev/?url={url}",
        f"https://terabox.udayscriptsx.workers.dev/api?url={url}",
        f"https://terabox-dl.freemiumworld.workers.dev/?url={url}",
        f"https://terabox-downloader-ten.vercel.app/api/download?url={url}"
    ]
    
    data = None
    for api_url in apis:
        try:
            response = requests.get(api_url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                break
        except Exception as e:
            logging.warning(f"API {api_url} failed: {e}")
            continue
    
    if not data:
        return None, None, None

    # Handle different API response formats
    try:
        if "response" in data and len(data["response"]) > 0:
            # nepcoderdevs format
            resolutions = data["response"][0]["resolutions"]
            fast_download_link = resolutions["Fast Download"]
            hd_download_link = resolutions["HD Video"]
            thumbnail_url = data["response"][0]["thumbnail"]
            video_title = data["response"][0]["title"]
        elif "download_link" in data:
            # Alternative format
            fast_download_link = data["download_link"]
            hd_download_link = data.get("hd_download_link", fast_download_link)
            thumbnail_url = data.get("thumbnail", "")
            video_title = data.get("title", "Terabox Video")
        else:
            raise Exception("Unknown API response format")
    except (KeyError, IndexError) as e:
        raise Exception(f"Failed to parse API response: {e}")

    # Provide direct download links (cloud deployment)
    buttons = [
        [InlineKeyboardButton("🚀 HD Video", url=hd_download_link)],
        [InlineKeyboardButton("⚡ Fast Download", url=fast_download_link)]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await reply_msg.edit_text(
        "📥 Direct download links:",
        reply_markup=reply_markup
    )
    return None, None, None

async def upload_video(client, file_path, thumbnail_path, video_title, reply_msg, collection_channel_id, user_mention, user_id, message, is_admin=False):
    # This function won't be called since download_video returns None for cloud deployment
    pass