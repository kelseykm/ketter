"""
downloader handles downloading, writing to disc and providing feedback through
a progress bar
"""

import aiofiles
import aiohttp
import os
import tqdm
import typing
import urllib.parse
from .utils import *
from .errors import *


async def download(
        url: str,
        headers: dict[str, str],
        session: aiohttp.ClientSession,
        chunk_size: int,
) -> typing.Union[dict[str, typing.Union[str, int]], bytes]:
    """
    performs http get request for given url and returns metadata and chunked
    data
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


def progress_bar(file_name: str, total: typing.Optional[int]) -> tqdm.std.tqdm:
    """returns tqdm progress bar ready for use"""

    desc = f"{info_banner()} Downloading: {format_user_submitted(file_name)}"

    if total is not None:
        bar_format = "{desc} |\033[1;33m{bar}\033[0m| " + \
            "\033[1m{percentage:06.2f}%\033[0m " + \
            "\033[1;32m{elapsed}\033[0m " + \
            "\033[7;37m{rate_fmt}\033[0m"

        return tqdm.tqdm(
            unit="B",
            unit_scale=True,
            desc=desc,
            total=total,
            bar_format=bar_format
        )

    bar_format = "{desc} \033[1;32m{elapsed}\033[0m \033[7;37m{rate_fmt}\033[0m"

    return tqdm.tqdm(
        unit="B",
        unit_scale=True,
        desc=desc,
        bar_format=bar_format
    )


async def worker(idx: int, url: str, session: aiohttp.ClientSession):
    """handles downloading, writing to disc and updating progress bar"""

    _CHUNK_SIZE = 60*1024

    parsed_url = urllib.parse.urlparse(url)
    file_name = parsed_url.path.split("/")[-1]
    file_name = urllib.parse.unquote(file_name)

    if file_name == "":
        file_name = f"file_{idx+1}"

    headers = {}
    resume_download = True if os.path.exists(file_name) else False
    if resume_download:
        file_size = os.stat(file_name).st_size
        headers["Range"] = f"bytes={file_size}-"

    download_generator = download(
        url=url,
        headers=headers,
        session=session,
        chunk_size=_CHUNK_SIZE
    )

    metadata = await download_generator.asend(None)

    if metadata["status"] == 416:
        bar = progress_bar(file_name=file_name, total=file_size)
        bar.update(file_size)
        return

    elif metadata["status"] >= 400:
        raise KetterHTTPError(
            f"Response status {metadata['status']}, {HTTP_CODES[metadata['status']]}")

    really_resume_download = resume_download and metadata["status"] == 206

    total = metadata["content_length"]
    if really_resume_download:
        total += file_size

    bar = progress_bar(file_name=file_name, total=total)

    if really_resume_download:
        bar.update(file_size)

    open_mode = "ab" if really_resume_download else "wb"
    async with aiofiles.open(file_name, open_mode) as file:
        async for data in download_generator:
            await file.write(data)
            bar.update(len(data))
