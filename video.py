import requests
from datetime import datetime
from status import format_progress_bar
import asyncio
import os, time
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def download_video(url, reply_msg, user_mention, user_id):
    # Use your Cloudflare Worker as primary method
    try:
        worker_url = f"https://tera.empiregroup.workers.dev/?src={url}"
        buttons = [[InlineKeyboardButton("📥 Download File", url=worker_url)]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await reply_msg.edit_text("⚡ Direct download link:", reply_markup=reply_markup)
        return None, None, None
    except Exception as e:
        logging.error(f"Worker failed: {e}")
        
    # Fallback APIs
    apis = [
        f"https://teraboxvideodownloader.nepcoderdevs.workers.dev/?url={url}",
        f"https://terabox.udayscriptsx.workers.dev/api?url={url}"
    ]
    
    for api_url in apis:
        try:
            response = requests.get(api_url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if "response" in data and len(data["response"]) > 0:
                    resolutions = data["response"][0]["resolutions"]
                    fast_link = resolutions["Fast Download"]
                    hd_link = resolutions["HD Video"]
                    buttons = [
                        [InlineKeyboardButton("🚀 HD Video", url=hd_link)],
                        [InlineKeyboardButton("⚡ Fast Download", url=fast_link)]
                    ]
                    reply_markup = InlineKeyboardMarkup(buttons)
                    await reply_msg.edit_text("📥 Backup download links:", reply_markup=reply_markup)
                    return None, None, None
        except Exception as e:
            logging.warning(f"API {api_url} failed: {e}")
            continue
    
    return None, None, None

async def upload_video(client, file_path, thumbnail_path, video_title, reply_msg, collection_channel_id, user_mention, user_id, message, is_admin=False):
    # This function won't be called since download_video returns None for cloud deployment
    pass