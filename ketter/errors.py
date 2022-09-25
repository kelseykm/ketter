"""errors provides custom errors"""


class KetterHTTPError(Exception):
    """for errors encountered while downloading"""

    ...


class KetterHTTPHeaderError(Exception):
    """for errors relating to custom headers"""

    ...


class KetterInvalidFileError(Exception):
    """for errors relating to url file"""

    ...
