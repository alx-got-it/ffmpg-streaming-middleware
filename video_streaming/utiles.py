import logging
import os
import re
import time
import warnings
from sys import platform


def get_path_info(path):
    dirname = os.path.dirname(path)
    name = str(os.path.basename(path).rsplit(".", 1)[0])

    return dirname, name


def mkdir(dirname: str) -> None:
    try:
        os.makedirs(dirname)
    except OSError as exc:
        logging.info(exc)


def rm(path: str) -> None:
    try:
        os.remove(path)
    except OSError as exc:
        logging.info(exc)


def clean_args(args: list) -> list:
    clean_args_ = []
    for arg in args:
        if " " in arg:
            arg = '"' + arg + '"'
        clean_args_.append(arg.replace("\\", "/").replace("__COLON__", ":"))

    return clean_args_


def convert_to_sec(time):
    h, m, s = time.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def get_time(key, string, default):
    time = re.search("(?<={})\w+:\w+:\w+".format(key), string)
    return convert_to_sec(time.group(0)) if time else default


def time_left(start_time, unit, total):
    if unit != 0:
        diff_time = time.time() - start_time
        return total * diff_time / unit - diff_time
    else:
        return 0


def deprecated(func):
    def deprecated_fun(*args, **kwargs):
        warnings.warn(
            "Метод {} будет удалён в следующей версии".format(func.__name__),
            DeprecationWarning,
            stacklevel=2,
        )
        return func(*args, **kwargs)

    return deprecated_fun


def get_os():
    if platform in ["linux", "linux2"]:
        return "linux"
    elif platform == "darwin":
        return "os_x"
    elif platform in ["win32", "Windows"]:
        return "windows"
    else:
        return "unknown"


def cnv_options_to_args(options: dict):
    args = []
    for k, v in options.items():
        args.append("-{}".format(k))
        if v is not None:
            args.append("{}".format(v))

    return args
