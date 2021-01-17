#!/usr/bin/env python3

#Written by kelseykm

import asyncio
import aiohttp
import aiofiles
from urllib.parse import urlparse
import re
import os
import sys

version = 0.2
normal = '\033[0;39m'
green = '\033[1;32m'
red = '\033[1;31m'
orange = '\033[1;33m'
banner = f"""{orange}
 _        _   _             __
| | _____| |_| |_ ___ _ __  \ \\
| |/ / _ \ __| __/ _ \ '__|  \ \\
|   <  __/ |_| ||  __/ |     / /
|_|\_\___|\__|\__\___|_|    /_/
{normal}"""

class Ketter(object):
    def __init__(self, session, url, outfile):
        self.session = session
        self.url = url
        self.file_name = outfile
        self.chunk_size = 64*1024
        self.success = True

    async def _download(self):
        async with self.session.get(self.url) as response:
            if not response.status == 200:
                self.success = False
                await self.file_object.close()
                os.remove(self.file_name)
                return

            while True:
                chunk = await response.content.read(self.chunk_size)
                if not chunk:
                    return
                yield chunk

    async def write_to_file(self):
        print(f"{green}[INFO]{normal} DOWNLOAD STARTED: {orange}{self.file_name}{normal}")

        async with aiofiles.open(self.file_name, "wb") as self.file_object:
            async for chunk in self._download():
                await self.file_object.write(chunk)

        if self.success:
            print(f"{green}[INFO]{normal} DOWNLOAD FINISHED: {orange}{self.file_name}{normal}")
        else:
            print(f"{red}[ERROR]{normal} NON-200 RESPONSE; DOWNLOAD FAILED: {orange}{self.file_name}{normal}")

def usage():
    instructions = """
Usage: ketter <url-file>

Append all urls of items to be downloaded to a text file and add the path of the
url-file as an argument.

NB: Ensure that the urls are **FULLY WRITTEN**
    For example: 'https://example.com' and not 'example.com'

Options:
    -h, --help      Show usage
    -v, --version   Show version number
"""
    print(instructions)
    sys.exit()

async def main():
    if not sys.argv[1:]:
        usage()
    elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
        usage()
    elif sys.argv[1] == "-v" or sys.argv[1] == "--version":
        print(f"{green}[INFO]{normal} VERSION {orange}{version}{normal}")
        sys.exit()
    elif len(sys.argv[1:]) > 1:
        usage()

    url_file = sys.argv[1]
    if not os.path.exists(url_file):
        print(f"{red}[ERROR]{normal} {orange}{url_file}{normal} DOES NOT EXIST")
        sys.exit()
    elif not os.path.isfile(url_file):
        print(f"{red}[ERROR]{normal} {orange}{url_file}{normal} IS NOT A REGULAR FILE")
        sys.exit()

    with open(url_file) as f:
        urls = [ url.strip() for url in f.readlines()]

    t = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(timeout=t) as session:
        tasks = []

        for index, url in enumerate(urls):
            outfile = urlparse(url).path.split('/')[-1]
            outfile = re.sub(r'%20', ' ', outfile)
            if not outfile:
                outfile = f"file_{index+1}"

            k = Ketter(session, url, outfile)
            tasks.append(k.write_to_file())

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    print(banner)
    asyncio.run(main())
