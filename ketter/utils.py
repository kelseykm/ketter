"""utils contains convenient helper functions and variables"""

from .colour import (
    BLUE_BACKGROUND,
    BOLD,
    NORMAL,
    RED_BACKGROUND,
    YELLOW,
)


def info_banner() -> str:
    """info_banner returns a formatted info banner"""
    return f"{BLUE_BACKGROUND}{BOLD}[INFO]{NORMAL}"


def error_banner() -> str:
    """error_banner returns a formatted error banner"""
    return f"{RED_BACKGROUND}{BOLD}[ERROR]{NORMAL}"


def print_ketter_banner():
    """prints ketter banner to stdout"""
    banner = [10, 32, 95, 32, 32, 32, 32, 32, 32, 32, 32, 95, 32, 32, 32, 95,
              32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 95, 95, 10,
              124, 32, 124, 32, 95, 95, 95, 95, 95, 124, 32, 124, 95, 124, 32,
              124, 95, 32, 95, 95, 95, 32, 95, 32, 95, 95, 32, 32, 92, 32, 92,
              10, 124, 32, 124, 47, 32, 47, 32, 95, 32, 92, 32, 95, 95, 124,
              32, 95, 95, 47, 32, 95, 32, 92, 32, 39, 95, 95, 124, 32, 32, 92,
              32, 92, 10, 124, 32, 32, 32, 60, 32, 32, 95, 95, 47, 32, 124, 95,
              124, 32, 124, 124, 32, 32, 95, 95, 47, 32, 124, 32, 32, 32, 32,
              32, 47, 32, 47, 10, 124, 95, 124, 92, 95, 92, 95, 95, 95, 124,
              92, 95, 95, 124, 92, 95, 95, 92, 95, 95, 95, 124, 95, 124, 32,
              32, 32, 32, 47, 95, 47, 10]

    print(f"{YELLOW}{BOLD}{bytes(banner).decode('utf-8')}{NORMAL}")
