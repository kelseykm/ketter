import aiohttp
import asyncio
import sys
from .utils import *
from .arguments import main as arguments_main
from .downloader import worker


async def main() -> int:
    """executes the program"""

    retval = 0

    headers, urls = arguments_main()

    timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        workers = []

        for idx, url in enumerate(urls):
            workers.append(worker(idx, url, session))

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
    print_ketter_banner()
    sys.exit(asyncio.run(main()))
