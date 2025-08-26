import requests
import aria2p
from datetime import datetime
from status import format_progress_bar
import asyncio
import os, time
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Try to initialize aria2, but handle connection errors gracefully
aria2 = None
try:
    aria2 = aria2p.API(
        aria2p.Client(
            host="http://localhost",
            port=6800,
            secret=""
        )
    )
    options = {
        "max-tries": "50",
        "retry-wait": "3",
        "continue": "true"
    }
    aria2.set_global_options(options)
    logging.info("aria2c daemon connected successfully")
except Exception as e:
    logging.warning(f"aria2c daemon not available: {e}")
    aria2 = None


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

    # If aria2 is not available, provide direct download links
    if aria2 is None:
        buttons = [
            [InlineKeyboardButton("🚀 HD Video", url=hd_download_link)],
            [InlineKeyboardButton("⚡ Fast Download", url=fast_download_link)]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await reply_msg.edit_text(
            "📥 Direct download links (aria2c not available):",
            reply_markup=reply_markup
        )
        return None, None, None

    try:
        download = aria2.add_uris([fast_download_link])
        start_time = datetime.now()

        while not download.is_complete:
            download.update()
            percentage = download.progress
            done = download.completed_length
            total_size = download.total_length
            speed = download.download_speed
            eta = download.eta
            elapsed_time_seconds = (datetime.now() - start_time).total_seconds()
            progress_text = format_progress_bar(
                filename=video_title,
                percentage=percentage,
                done=done,
                total_size=total_size,
                status="Downloading",
                eta=eta,
                speed=speed,
                elapsed=elapsed_time_seconds,
                user_mention=user_mention,
                user_id=user_id,
                aria2p_gid=download.gid
            )
            await reply_msg.edit_text(progress_text)
            await asyncio.sleep(2)

        if download.is_complete:
            file_path = download.files[0].path

            thumbnail_path = "thumbnail.jpg"
            thumbnail_response = requests.get(thumbnail_url)
            with open(thumbnail_path, "wb") as thumb_file:
                thumb_file.write(thumbnail_response.content)

            await reply_msg.edit_text("ᴜᴘʟᴏᴀᴅɪɴɢ...")

            return file_path, thumbnail_path, video_title
    except Exception as e:
        logging.error(f"Error handling message: {e}")
        buttons = [
            [InlineKeyboardButton("🚀 HD Video", url=hd_download_link)],
            [InlineKeyboardButton("⚡ Fast Download", url=fast_download_link)]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await reply_msg.edit_text(
            "Fast Download Link For this Video is Broken, Download manually using the Link Below.",
            reply_markup=reply_markup
        )
        return None, None, None

# async def download_video(url, reply_msg, user_mention, user_id):
#     response = requests.get(f"https://teraboxvideodownloader.nepcoderdevs.workers.dev/?url={url}")
#     response.raise_for_status()
#     data = response.json()

#     resolutions = data["response"][0]["resolutions"]
#     fast_download_link = resolutions["Fast Download"]
#     hd_download_link = resolutions["HD Video"]
#     thumbnail_url = data["response"][0]["thumbnail"]
#     video_title = data["response"][0]["title"]

#     download = aria2.add_uris([fast_download_link])
#     start_time = datetime.now()

#     while not download.is_complete:
#         download.update()
#         percentage = download.progress
#         done = download.completed_length
#         total_size = download.total_length
#         speed = download.download_speed
#         eta = download.eta
#         elapsed_time_seconds = (datetime.now() - start_time).total_seconds()
#         progress_text = format_progress_bar(
#             filename=video_title,
#             percentage=percentage,
#             done=done,
#             total_size=total_size,
#             status="Downloading",
#             eta=eta,
#             speed=speed,
#             elapsed=elapsed_time_seconds,
#             user_mention=user_mention,
#             user_id=user_id,
#             aria2p_gid=download.gid
#         )
#         await reply_msg.edit_text(progress_text)
#         await asyncio.sleep(2)

#     if download.is_complete:
#         file_path = download.files[0].path

#         thumbnail_path = "thumbnail.jpg"
#         thumbnail_response = requests.get(thumbnail_url)
#         with open(thumbnail_path, "wb") as thumb_file:
#             thumb_file.write(thumbnail_response.content)

#         await reply_msg.edit_text("ᴜᴘʟᴏᴀᴅɪɴɢ...")

#         return file_path, thumbnail_path, video_title
#     else:
#         return markup


async def upload_video(client, file_path, thumbnail_path, video_title, reply_msg, collection_channel_id, user_mention, user_id, message, is_admin=False):
    file_size = os.path.getsize(file_path)
    uploaded = 0
    start_time = datetime.now()
    last_update_time = time.time()

    async def progress(current, total):
        nonlocal uploaded, last_update_time
        uploaded = current
        percentage = (current / total) * 100
        elapsed_time_seconds = (datetime.now() - start_time).total_seconds()
        
        if time.time() - last_update_time > 2:
            progress_text = format_progress_bar(
                filename=video_title,
                percentage=percentage,
                done=current,
                total_size=total,
                status="Uploading",
                eta=(total - current) / (current / elapsed_time_seconds) if current > 0 else 0,
                speed=current / elapsed_time_seconds if current > 0 else 0,
                elapsed=elapsed_time_seconds,
                user_mention=user_mention,
                user_id=user_id,
                aria2p_gid=""
            )
            try:
                await reply_msg.edit_text(progress_text)
                last_update_time = time.time()
            except Exception as e:
                logging.warning(f"Error updating progress message: {e}")

    with open(file_path, 'rb') as file:
        collection_message = await client.send_video(
            chat_id=collection_channel_id,
            video=file,
            caption=f"✨ {video_title}\n👤 ʟᴇᴇᴄʜᴇᴅ ʙʏ : {user_mention}\n📥 ᴜsᴇʀ ʟɪɴᴋ: tg://user?id={user_id}",
            thumb=thumbnail_path,
            progress=progress
        )
        await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=collection_channel_id,
            message_id=collection_message.id
        )
        await asyncio.sleep(1)
        await message.delete()

    await reply_msg.delete()
    sticker_message = await message.reply_sticker("CAACAgIAAxkBAAEZdwRmJhCNfFRnXwR_lVKU1L9F3qzbtAAC4gUAAj-VzApzZV-v3phk4DQE")
    os.remove(file_path)
    os.remove(thumbnail_path)
    await asyncio.sleep(5)
    await sticker_message.delete()
    return collection_message.id
