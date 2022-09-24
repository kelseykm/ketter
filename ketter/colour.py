_ESC = chr(27)

NORMAL = f"{_ESC}[0m"
BOLD = f"{_ESC}[1m"
ITALIC = f"{_ESC}[3m"
UNDERLINE = f"{_ESC}[4m"
BLINK = f"{_ESC}[5m"
INVERT = f"{_ESC}[7m"
INVISIBLE = f"{_ESC}[8m"
STRIKE_THROUGH = f"{_ESC}[9m"
OVERWRITE = f"{_ESC}[2K" + "\r"

BLACK = f"{_ESC}[30m"
RED = f"{_ESC}[31m"
GREEN = f"{_ESC}[32m"
YELLOW = f"{_ESC}[33m"
BLUE = f"{_ESC}[34m"
MAGENTA = f"{_ESC}[35m"
CYAN = f"{_ESC}[36m"
WHITE = f"{_ESC}[37m"

BLACK_BACKGROUND = f"{_ESC}[40m"
RED_BACKGROUND = f"{_ESC}[41m"
GREEN_BACKGROUND = f"{_ESC}[42m"
YELLOW_BACKGROUND = f"{_ESC}[43m"
BLUE_BACKGROUND = f"{_ESC}[44m"
MAGENTA_BACKGROUND = f"{_ESC}[45m"
CYAN_BACKGROUND = f"{_ESC}[46m"
WHITE_BACKGROUND = f"{_ESC}[47m"


def info_banner() -> str:
    """info_banner returns a formatted info banner"""
    return f"{BLUE_BACKGROUND}{BOLD}INFO{NORMAL}"


def error_banner() -> str:
    """error_banner returns a formatted error banner"""
    return f"{RED_BACKGROUND}{BOLD}ERROR{NORMAL}"
