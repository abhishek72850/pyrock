import sys
import inspect
import functools
import logging
import traceback
import sublime
from datetime import datetime
from .settings import PyRockSettings


def get_plugin_debug_level(default='error'):
    level = PyRockSettings().LOG_LEVEL.value or default
    return level


class Logger:
    """Sublime Console Logger that takes plugin settings."""

    def __init__(self, name):
        self.name = str(name)

    @property
    def level(self):
        return logging.__dict__[get_plugin_debug_level().upper()]

    def _print(self, msg, level, lineno):
        created_at = datetime.today().strftime("%Y-%m-%dT%H:%M:%S.%f")
        levelname = logging.getLevelName(level)
        log_msg = f"{created_at}:{levelname}:{self.name}[{lineno}]:{str(msg)}"
        print(log_msg)

    def log(self, level, msg, **kwargs):
        """ thread-safe logging """
        callerframerecord = inspect.stack()[2]
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)

        if kwargs.pop('exc_info', False):
            kwargs['exc_info'] = sys.exc_info()
        log = functools.partial(self._log, level, msg, info.lineno, **kwargs)
        sublime.set_timeout(log, 0)

    def _log(self, level, msg, lineno, **kwargs):
        """
        :param level: logging level value
        :param msg: message that logger should prints out
        :param kwargs: dictionary of additional parameters
        """
        if self.level <= level:
            self._print(msg, level, lineno)
            if level == logging.ERROR:
                exc_info = kwargs.get('exc_info')
                if exc_info:
                    traceback.print_exception(*exc_info)

    def debug(self, msg):
        self.log(logging.DEBUG, msg)

    def info(self, msg):
        self.log(logging.INFO, msg)

    def error(self, msg, exc_info=False):
        self.log(logging.ERROR, msg, exc_info=exc_info)

    def exception(self, msg):
        self.error(msg, exc_info=True)

    def warning(self, msg):
        self.log(logging.WARN, msg)
