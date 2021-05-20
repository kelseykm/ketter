#!/usr/bin/env python3

#Written by kelseykm

import asyncio
import aiohttp
import aiofiles
from urllib.parse import urlparse
import re
import os
import sys
import tqdm

version = 0.3
normal = '\033[0;39m'
white = '\033[1;39m'
green = '\033[1;32m'
red = '\033[1;31m'
orange = '\033[1;33m'
italic_white = '\033[3;39m'
banner = f"""{orange}
 _        _   _             __
| | _____| |_| |_ ___ _ __  \ \\
| |/ / _ \ __| __/ _ \ '__|  \ \\
|   <  __/ |_| ||  __/ |     / /
|_|\_\___|\__|\__\___|_|    /_/
{normal}"""

class Ketter:
    def __init__(self, session, url, outfile, resume):
        self.session = session
        self.url = url
        self.file_name = outfile
        self.resume = resume
        self.chunk_size = 64*1024
        self.success = True
        self.existing_outfile_size = os.stat(self.file_name).st_size if self.resume else None
        self.codes = {
            100: 'Continue', 101: 'Switching Protocols', 102: 'Processing', 103: 'Early Hints', 200: 'OK', 201: 'Created', 202: 'Accepted', 203: 'Non-Authoritative Information', 204: 'No Content', 205: 'Reset Content', 206: 'Partial Content', 207: 'Multi-Status', 208: 'Already Reported', 226: 'IM Used', 300: 'Multiple Choices', 301: 'Moved Permanently', 302: 'Found', 303: 'See Other', 304: 'Not Modified', 305: 'Use Proxy', 306: 'Switch Proxy', 307: 'Temporary Redirect', 308: 'Permanent Redirect', 400: 'Bad Request', 401: 'Unauthorized', 402: 'Payment Required', 403: 'Forbidden', 404: 'Not Found', 405: 'Method Not Allowed', 406: 'Not Acceptable', 407: 'Proxy Authentication Required', 408: 'Request Timeout', 409: 'Conflict', 410: 'Gone', 411: 'Length Required', 412: 'Precondition Failed', 413: 'Payload Too Large', 414: 'URI Too Long', 415: 'Unsupported Media Type', 416: 'Range Not Satisfiable', 417: 'Expectation Failed', 418: "I'm a teapot", 421: 'Misdirected Request', 422: 'Unprocessable Entity', 423: 'Locked', 424: 'Failed Dependency', 425: 'Too Early', 426: 'Upgrade Required', 428: 'Precondition Required', 429: 'Too Many Requests', 431: 'Request Header Fields Too Large', 451: 'Unavailable For Legal Reasons', 500: 'Internal Server Error', 501: 'Not Implemented', 502: 'Bad Gateway', 503: 'Service Unavailable', 504: 'Gateway Timeout', 505: 'HTTP Version Not Supported', 506: 'Variant Also Negotiates', 507: 'Insufficient Storage', 508: 'Loop Detected', 510: 'Not Extended', 511: 'Network Authentication Required'
         }


    async def download(self):
        try:
            headers = { "Range": f"bytes={self.existing_outfile_size}-" } if self.resume else None

            async with self.session.get(url=self.url, headers=headers) as response:
                if not response.ok:
                    print(f"{red}[ERROR]{normal} DOWNLOAD FAILED: {orange}{self.file_name}{normal}")
                    if response.status in self.codes:
                        print(f"  {chr(9658)} {italic_white}Response status: {response.status} {self.codes[response.status]}{normal}")
                    else:
                        print(f"  {chr(9658)} {italic_white}Response status: {response.status}{normal}")
                    return

                if self.resume and response.content_type == "text/html":
                    self.resume = False

                if self.resume and response.content_length:
                    self.content_length = response.content_length + self.existing_outfile_size
                else:
                    self.content_length = response.content_length

                if self.content_length:
                    bar_format='{desc} |{bar}|{percentage:.2f}%|'
                    progress_bar = tqdm.tqdm(desc=f"{green}[INFO]{normal} DOWNLOADING: {orange}{self.file_name}{white}", total=self.content_length, bar_format=bar_format)

                    if self.resume:
                        progress_bar.update(self.existing_outfile_size)

                    mode = "ab" if self.resume else "wb"
                    async with aiofiles.open(self.file_name, mode) as self.file_object:
                        with progress_bar:
                            async for chunk in response.content.iter_chunked(self.chunk_size):
                                await self.file_object.write(chunk)
                                progress_bar.update(len(chunk))
                else:
                    print(f"{green}[INFO]{normal} DOWNLOAD STARTED: {orange}{self.file_name}{normal}")

                    async with aiofiles.open(self.file_name, "wb") as self.file_object:
                        async for chunk in response.content.iter_chunked(self.chunk_size):
                            await self.file_object.write(chunk)

                    print(f"{green}[INFO]{normal} DOWNLOAD FINISHED: {orange}{self.file_name}{normal}")

        except Exception as e:
            print(f"{red}[ERROR]{normal} DOWNLOAD FAILED: {orange}{self.file_name}{normal}")
            print(f"  {chr(9658)} {italic_white}Exception: {e}{normal}")


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

            resume = True if os.path.exists(outfile) else False

            k = Ketter(session, url, outfile, resume)
            tasks.append(k.download())

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    print(banner)
    asyncio.run(main())
