import logging
import os
import time
from django.conf import settings
from concurrent_log_handler import ConcurrentTimedRotatingFileHandler, ConcurrentRotatingFileHandler


# https://blog.csdn.net/tofu_yi/article/details/118566756
# https://zhuanlan.zhihu.com/p/445411809
logger_collect = logging.getLogger('collect')
logfile = os.path.abspath("logs/main.log")
# Using concurrent_log_handler instead of logging Headler,
# to avoid PermissionError during rotating the log files
# https://github.com/Preston-Landers/concurrent-log-handler
logger_collect.addHandler(ConcurrentTimedRotatingFileHandler(logfile, when='MIDNIGHT', backupCount=10, encoding='utf-8'))
logger_collect.setLevel(getattr(logging, 'DEBUG'))

level_int2name = {
    10: "DEBUG", 20: "INFO", 25: "SUCCESS", 30: "WARNING", 40: "ERROR",
}


def format_time(timestamp):
    """
    Parameters
    ----------
    timestamp

    Returns
    -------

    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


def debug_print(*args):
    """
    Parameters
    ----------
    args

    Returns
    -------

    """
    if settings.DEBUG:
        print(*args)


def write_log(ip, level, msg='', ignore=False, **kwargs):
    try:
        _write_log(ip, level, msg, **kwargs)
    except ValueError:
        if ignore:
            _write_log(ip, "ERROR", "Message is not a string")
        else:
            raise
    except (BaseException, Exception):
        if ignore:
            pass
        else:
            raise


def _write_log(ip, level, msg='', **kwargs):
    """
    level: {
        'CRITICAL',
        'FATAL',
        'ERROR',
        'WARN',
        'WARNING',
        'INFO',
        'DEBUG',
        'NOTSET',
        }
    Parameters
    ----------
    ip
    level:
    msg
    ignore

    Returns
    -------

    """

    if not isinstance(ip, str):
        raise ValueError("The IP address must be a string")
    try:
        str(msg)
    except (BaseException, Exception):
        raise ValueError("Msg must be a string")
    if isinstance(level, int):
        level = level_int2name[level]
    if level.upper() not in logging._nameToLevel.keys():
        raise ValueError(f"Invalid log level: {level}, valid levels are: {list(logging._nameToLevel.keys())}")

    return getattr(logger_collect, level.lower())(
        f"{format_time(time.time())}|{ip}|{level.upper()}|{msg}|{''.join([f'{k}={v}' for k,v in kwargs.items()])}")


