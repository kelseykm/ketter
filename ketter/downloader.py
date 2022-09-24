import aiohttp
from typing import Union


async def download(
        url: str,
        headers: dict[str, str],
        session: aiohttp.ClientSession,
        chunk_size: int,
) -> Union[dict[str, Union[str, int]], bytes]:
    """
    download is an async generator func that performs http get request for
    given url and returns metadata and chunked data
    """

    async with session.get(url=url, headers=headers) as response:
        metadata = {
            "content_type": response.content_type,
            "content_length": response.content_length,
            "status": response.status,
        }

        yield metadata

        if not response.ok:
            return

        async for data in response.content.iter_chunked(chunk_size):
            yield data
