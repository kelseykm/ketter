import aiofiles
import aiohttp
import argparse
import asyncio
import os
import tqdm
import typing
import urllib.parse
from .utils import *
from .errors import KetterHTTPError
from . import __version__ as VERSION


async def download(
        url: str,
        headers: dict[str, str],
        session: aiohttp.ClientSession,
        chunk_size: int,
) -> typing.Union[dict[str, typing.Union[str, int]], bytes]:
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


def progress_bar(file_name: str, total: typing.Optional[int]) -> tqdm.std.tqdm:
    """returns tqdm progress bar ready for use"""

    desc = f"{info_banner()} downloading: {UNDERLINE} {file_name} {NORMAL}"
    bar_format = "{desc} {bar} {percentage:6.2f}%"

    return tqdm.tqdm(
        desc=desc,
        total=total,
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
        headers["Range"] = f"bytes={file_name}-"

    download_generator = download(
        url=url,
        headers=headers,
        session=session,
        chunk_size=_CHUNK_SIZE
    )

    metadata = await download_generator.asend(None)

    if metadata["status"] < 400:
        raise KetterHTTPError(
            f"Response status {metadata['status']}, {HTTP_CODES[metadata['status']]}")

    bar = progress_bar(
        file_name=file_name,
        total=metadata["content_length"]
    )

    async with aiofiles.open(file_name, "ab") as file:
        async for data in download_generator:
            await file.write(data)
            bar.update(len(data))


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Asynchronous HTTP downloader", prog="ketter")
    parser.add_argument("-v", "--version", action="version",
                        version=f"%(prog)s {VERSION}")
    parser.add_argument(
        "URL_FILE",  help="""text file with urls to be downloaded, separated by
        newlines; the urls should be written in full, including the url
        scheme""")

    return parser


def valid_url_file(url_file: str) -> bool:
    if os.path.exists(url_file) and os.path.isfile(url_file):
        return True

    return False


def harvest_urls(url_file: str) -> list[str]:
    with open(url_file) as file:
        return [url.strip() for url in file.readlines()]


async def main():
    parser = create_parser()
    args = parser.parse_args()

    if not valid_url_file(args.URL_FILE):
        print(
            f"{error_banner()} Invalid URL_FILE: {format_user_submitted(args.URL_FILE)}",
            end="\n\n"
        )
        parser.print_usage()
        return

    try:
        urls = harvest_urls(args.URL_FILE)
    except Exception as e:
        print(f"{error_banner()} {e}")
        return

    timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        workers = []

        for idx, url in enumerate(urls):
            workers.append(worker(idx, url, session))

        results = await asyncio.gather(*workers, return_exceptions=True)

        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                print(
                    f"{error_banner()} {format_user_submitted(urls[idx])}: {repr(result)}")


if __name__ == "__main__":
    print_ketter_banner()
    asyncio.run(main())
