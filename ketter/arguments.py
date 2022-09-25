"""
arguments is responsible getting, validating and formatting user entered data
to make it ready for use by the program
"""
import argparse
import functools
import os
from .utils import *
from .errors import *
from . import __version__ as VERSION


def create_parser() -> argparse.ArgumentParser:
    """creates and returns a commandline arguments parser"""

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
    """ensures the url file exists and is a regular file"""

    if not os.path.exists(url_file):
        raise KetterInvalidFileError(
            f"Url file does not exist: {format_user_submitted(url_file)}")

    elif not os.path.isfile(url_file):
        raise KetterInvalidFileError(
            f"Url file not regular file: {format_user_submitted(url_file)}")


def harvest_urls(url_file: str) -> list[str]:
    """reads and formats urls from url file"""

    with open(url_file) as file:
        return [url.strip() for url in file.readlines()]


def harvest_headers(custom_headers: list[str]) -> dict[str, str]:
    """validates and formats passed headers for ready use"""

    def reduce_headers(
            accum_headers: dict[str, str],
            curr_header: str
    ) -> dict[str, str]:
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


def main() -> tuple[dict[str, str], list[str]]:
    """returns all commandline arguments ready for use"""

    parser = create_parser()
    args = parser.parse_args()

    try:
        custom_headers = harvest_headers(args.header or [])
        validate_url_file(args.URL_FILE)
        urls = harvest_urls(args.URL_FILE)
    except Exception as e:
        parser.exit(2, f"{error_banner()} {e}")

    headers = {"user-agent": f"ketter/{VERSION}"}
    headers.update(custom_headers)

    def reduce_headers_capitalise(
            accum_headers: dict[str, str],
            curr_header_key: str
    ) -> dict[str, str]:
        accum_headers[capitalise(curr_header_key)] = headers[curr_header_key]
        return accum_headers

    headers = functools.reduce(reduce_headers_capitalise, headers, {})

    return headers, urls
