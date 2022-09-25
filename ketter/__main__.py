import aiofiles
import aiohttp
import argparse
import asyncio
import functools
import os
import tqdm
import typing
import urllib.parse
from .utils import *
from .errors import *
from . import __version__ as VERSION, USER_AGENT


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

    desc = f"{info_banner()} Downloading: {format_user_submitted(file_name)}"
    bar_format = "{desc} \033[1;33m{bar}\033[0m \033[1m{percentage:06.2f}%\033[0m"

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
        headers["Range"] = f"bytes={file_size}-"

    download_generator = download(
        url=url,
        headers=headers,
        session=session,
        chunk_size=_CHUNK_SIZE
    )

    metadata = await download_generator.asend(None)

    if metadata["status"] >= 400:
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


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Asynchronous HTTP downloader", prog="ketter")
    parser.add_argument("-v", "--version", action="version",
                        version=f"{info_banner()} %(prog)s {VERSION}")
    parser.add_argument("--header", action="append",
                        metavar="key=value", help="""custom header to include
                        in all requests. More than one may be specified. May
                        also be used to overwrite automatically generated
                        headers such as the 'User-Agent' header""")
    parser.add_argument("URL_FILE",  help="""text file with urls to be
                        downloaded, separated by newlines. The urls should be
                        written in full, including the url scheme""")

    return parser


def validate_url_file(url_file: str):
    if not os.path.exists(url_file):
        raise KetterInvalidFileError(
            f"Url file does not exist: {format_user_submitted(url_file)}")

    elif not os.path.isfile(url_file):
        raise KetterInvalidFileError(
            f"Url file not regular file: {format_user_submitted(url_file)}")


def harvest_urls(url_file: str) -> list[str]:
    with open(url_file) as file:
        return [url.strip() for url in file.readlines()]


def harvest_headers(custom_headers: list[str]) -> dict[str, str]:
    def reduce_headers(accum_headers, curr_header):
        key, value = curr_header.split("=", maxsplit=1)
        key = key.lower()

        if value == "":
            raise KetterHTTPHeaderError(
                f"Invalid header: {format_user_submitted(curr_header)}")

        accum_headers[key] = value
        return accum_headers

    return functools.reduce(
        reduce_headers,
        custom_headers,
        {}
    )


async def main():
    parser = create_parser()
    args = parser.parse_args()

    try:
        custom_headers = harvest_headers(args.header or [])
        validate_url_file(args.URL_FILE)
        urls = harvest_urls(args.URL_FILE)
    except Exception as e:
        print(f"{error_banner()} {e}")
        return

    headers = {"user-agent": USER_AGENT}
    headers.update(custom_headers)

    def reduce_headers_capitalise(accum_headers, curr_header_key):
        accum_headers[capitalise(curr_header_key)] = headers[curr_header_key]
        return accum_headers

    headers = functools.reduce(reduce_headers_capitalise, headers, {})

    timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        workers = []

        for idx, url in enumerate(urls):
            workers.append(worker(idx, url, session))

        results = await asyncio.gather(*workers, return_exceptions=True)

        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                print(
                    f"{error_banner()} {format_user_submitted(urls[idx])}: {result}")


if __name__ == "__main__":
    print_ketter_banner()
    asyncio.run(main())
