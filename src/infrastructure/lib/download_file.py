import httpx


async def download_file(url: str, headers: dict) -> bytes:
    """Download a file from a URL and return the bytes."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.content
