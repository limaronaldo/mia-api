from ..download_file import download_file

from decouple import config


async def download_whatsapp_file(filename: str, api_key: str, session: str) -> bytes:
    return await download_file(
        f"{config('WHATSAPP_FILES_BASE_URL')}/{session}/{filename}",
        headers={"X-Api-Key": api_key},
    )
