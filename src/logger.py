import sys
import functools
import logging
import traceback
import sublime
from src.settings import PyRockSettings
from src.constants import PyRockConstants


def get_plugin_debug_level(default='error'):
    level = PyRockSettings.LOG_LEVEL or default
    return getattr(logging, level.upper())


class Logger:
    """Sublime Console Logger that takes plugin settings."""

    def __init__(self, name):
        self.name = str(name)

    @property
    def level(self):
        return get_plugin_debug_level()

    def _print(self, msg):
        print(': '.join([f"{PyRockConstants.PACKAGE_NAME};{self.name}", str(msg)]))

    def log(self, level, msg, **kwargs):
        """ thread-safe logging """
        if kwargs.pop('exc_info', False):
            kwargs['exc_info'] = sys.exc_info()
        log = functools.partial(self._log, level, msg, **kwargs)
        sublime.set_timeout(log, 0)

    def _log(self, level, msg, **kwargs):
        """
        :param level: logging level value
        :param msg: message that logger should prints out
        :param kwargs: dictionary of additional parameters
        """
        if self.level <= level:
            self._print(msg)
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


def get_logger(name):
    """
    log example:
        ERROR 2019-07-03 18:53:35,365 expense_aggregation_service.server: error message
        request_id: 7ca3989edb2a6d9018cfa98d6548a010
    if any other field is interesting, then add to above ContextFilter and %(variable_name)s
    :param name:
    :return:
    """
    logger = logging.getLogger(name)
    logger.level = logging.__dict__[get_plugin_debug_level().upper()]
    handler = logging.StreamHandler()

    handler.setFormatter(
        logging.Formatter(
            "%(levelname)s %(asctime)s %(filename)s:%(lineno)s - %(name)s - %(funcName)s: %(message)s"
            "%Y-%m-%d %H:%M:%S"
        )
    )

    logger.addHandler(handler)
    return logger
