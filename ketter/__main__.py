import aiohttp
import asyncio
from .utils import *
from .arguments import main as arguments_main
from .downloader import worker


async def main():
    """sets up everything"""

    headers, urls = arguments_main()

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
