import hashlib
import hmac
import base64
import httpx
from Crypto.Cipher import AES
from typing import Literal

MEDIA_TYPE_IMAGE = 1
MEDIA_TYPE_VIDEO = 2
MEDIA_TYPE_AUDIO = 3
MEDIA_TYPE_DOCUMENT = 4


MediaType = Literal[1, 2, 3, 4]

APP_INFO_MAPPING = {
    MEDIA_TYPE_IMAGE: "image",
    MEDIA_TYPE_VIDEO: "video",
    MEDIA_TYPE_AUDIO: "audio",
    MEDIA_TYPE_DOCUMENT: "document",
}

APP_INFO = {
    "image": b"WhatsApp Image Keys",
    "video": b"WhatsApp Video Keys",
    "audio": b"WhatsApp Audio Keys",
    "document": b"WhatsApp Document Keys",
    "image/webp": b"WhatsApp Image Keys",
    "image/jpeg": b"WhatsApp Image Keys",
    "image/png": b"WhatsApp Image Keys",
    "video/mp4": b"WhatsApp Video Keys",
    "audio/aac": b"WhatsApp Audio Keys",
    "audio/ogg": b"WhatsApp Audio Keys",
    "audio/wav": b"WhatsApp Audio Keys",
}

EXTENSION_MAPPING = {
    MEDIA_TYPE_IMAGE: "jpg",
    MEDIA_TYPE_VIDEO: "mp4",
    MEDIA_TYPE_AUDIO: "ogg",
    MEDIA_TYPE_DOCUMENT: "bin",
}

EXTENSION = {
    "image": "jpg",
    "video": "mp4",
    "audio": "ogg",
    "document": "bin",
}


async def download_encrypted_media(media_url: str):
    try:

        async with httpx.AsyncClient() as client:
            response = await client.get(media_url)
            response.raise_for_status()
            return response.content, None
    except httpx.RequestError as e:
        return None, f"Error downloading media from URL: {e}"


def HKDF_CUSTOM(key, length, app_info_bytes=b""):
    key = hmac.new(b"\0" * 32, key, hashlib.sha256).digest()
    keyStream = b""
    keyBlock = b""
    blockIndex = 1
    while len(keyStream) < length:
        keyBlock = hmac.new(
            key,
            msg=keyBlock + app_info_bytes + (chr(blockIndex).encode("utf-8")),
            digestmod=hashlib.sha256,
        ).digest()
        blockIndex += 1
        keyStream += keyBlock
    return keyStream[:length]


def AESUnpad_CUSTOM(s):
    return s[: -ord(s[len(s) - 1 :])]


def AESDecrypt_CUSTOM(key, ciphertext, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)
    return AESUnpad_CUSTOM(plaintext)


def decrypt_media(enc_file_data, base64_media_key, media_type_int):
    try:
        media_key_blob = base64.b64decode(base64_media_key)
    except base64.binascii.Error as e:
        return None, f"Error decoding base64 media key: {e}"

    media_type_str = APP_INFO_MAPPING.get(media_type_int)
    if not media_type_str:
        return None, "Invalid media type"

    media_type_app_info = APP_INFO.get(media_type_str)
    if media_type_app_info is None:
        media_type_app_info = APP_INFO.get(EXTENSION_MAPPING.get(media_type_int))
        if media_type_app_info is None:
            media_type_app_info = b"WhatsApp Media Keys"

    mediaKeyExpanded = HKDF_CUSTOM(media_key_blob, 112, media_type_app_info)
    macKey = mediaKeyExpanded[48:80]
    file = enc_file_data[:-10]
    mac = enc_file_data[-10:]

    try:
        data = AESDecrypt_CUSTOM(mediaKeyExpanded[16:48], file, mediaKeyExpanded[:16])
    except Exception as e:
        return None, f"AES Decryption error: {e}"

    return data, None


def decrypt_media_file(enc_file_data, base64_media_key, media_type: MediaType):
    return decrypt_media(enc_file_data, base64_media_key, media_type)


async def decrypt_whatsapp_media(
    media_url: str, base64_media_key: str, media_type: MediaType
) -> tuple[bytes, str]:
    """
    Decrypt WhatsApp media file from URL
    Args:
        media_url: URL of the encrypted media file
        base64_media_key: Base64-encoded media key
        media_type: Media type (1 = image, 2 = video, 3 = audio, 4 = doc)
        output_file: Optional output file path
    Returns:
        Tuple of (output_path, error_message)
    """
    if media_type not in APP_INFO_MAPPING:
        return (
            None,
            f"Invalid media type. Must be one of: {', '.join(map(str, APP_INFO_MAPPING.keys()))}",
        )

    enc_media_data, download_error = await download_encrypted_media(media_url)
    if download_error:
        return None, f"Download error: {download_error}"

    data, err_msg = decrypt_media_file(enc_media_data, base64_media_key, media_type)
    if err_msg:
        return None, f"Decryption failed: {err_msg}"

    return data
