import aiohttp
import asyncio
import contextlib
import sys
from .utils import *
from .arguments import main as arguments_main
from .downloader import worker


async def main() -> int:
    """executes the program"""

    retval = 0

    headers, cookies, urls, max_downloads = arguments_main()

    if max_downloads is not None:
        sem = asyncio.Semaphore(max_downloads)
    else:
        sem = contextlib.nullcontext()

    timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(
        headers=headers,
        cookies=cookies,
        timeout=timeout
    ) as session:
        workers = []

        for idx, url in enumerate(urls):
            workers.append(worker(idx, url, session, sem))

        results = await asyncio.gather(*workers, return_exceptions=True)

        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                retval += 1
                print(
                    f"{error_banner()} {format_user_submitted(urls[idx])}: {result}")

    return retval


def cli():
    print_ketter_banner()
    sys.exit(asyncio.run(main()))


if __name__ == "__main__":
    cli()
