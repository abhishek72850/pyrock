from typing import List, Dict, Optional
import sublime
from datetime import datetime, date
from sublime import Edit, Window, View
from ..logger import Logger
from pathlib import Path
from ..exceptions import (
    VersionBlocked,
    SublimePackageBlacklisted,
    NonBypassNotification,
    SublimeVersionNotSupported
)
from ..utils import Network


logger = Logger(__name__)
path = Path(__file__)


ADMIN_VERSION = 'a.1.0.0'


class AdminManager:
    def __init__(
        self,
        window: Window,
        edit: Edit = None,
        view: View = None
    ):
        self.window = window
        self.edit = edit
        self.view = view
        self.orders = None
        self.black_list = None
        self.orders_ready = False
        self.black_list_ready = False

        self.cache = {}

    def _fetch_sublime_blacklist(self):
        response: Optional[Dict] = Network.get('https://abhishek72850.github.io/pyrock_blacklist.json')

        if response is not None:
            logger.info("Successfully fetched blacklist")
            self.black_list: Dict = response
            self.black_list_ready = True
            delay = 60 * 60 * 100
        else:
            logger.warning('Unable to fetch blacklist')
            self.black_list_ready = False
            delay = 60 * 100
        # execute timeout every hour or minute
        sublime.set_timeout_async(self._fetch_sublime_blacklist, delay)

    def _fetch_orders(self):
        response: Optional[Dict] = Network.get(
            'https://abhishek72850.github.io/pyrock_orders.json',
        )

        if response is not None:
            logger.info("Successfully fetched orders")
            self.orders: Dict = response
            self.orders_ready = True
            delay = 60 * 60 * 1000
        else:
            logger.warning('Unable to fetch orders')
            self.orders_ready = False
            delay = 60 * 1000
        # execute timeout every hour or minute
        sublime.set_timeout_async(self._fetch_orders, delay)

    def _execute_orders(self):
        if not self.orders_ready:
            logger.warning("Orders are not ready.")
            return

        version_block_list: Optional[List[str]] = self.orders.get('version_block_list')
        if version_block_list and ADMIN_VERSION in version_block_list:
            logger.error(f'This version {ADMIN_VERSION} is blocked by admin.')
            sublime.error_message(
                f'This version {ADMIN_VERSION} is blocked by admin. Please install the latest version.'
            )
            raise VersionBlocked(
                f'This version {ADMIN_VERSION} is blocked by admin.'
            )

        notifications: Optional[List[Dict]] = self.orders.get('notifications')
        if notifications:
            for notification in notifications:
                date_start: date = datetime.strptime(notification['date_start'], '%d/%m/%Y').date()
                date_end_str: Optional[str] = notification.get('date_end')
                if date_end_str:
                    date_end: datetime = datetime.strptime(date_end_str, '%d/%m/%Y').date()
                else:
                    date_end: datetime = datetime.today().date()

                expired: bool = notification['expired']

                if (
                    date_start <= datetime.today().date() <= date_end
                    and not expired
                ):
                    show_dialog = False
                    if not notification["bypass"]:
                        show_dialog = True
                    elif self.cache.get(notification["id"], 0) < notification["daily_frequency"]:
                        show_dialog = True
                        self.cache[notification["id"]] = self.cache.get(notification["id"], 0) + 1

                    if show_dialog:
                        sublime.ok_cancel_dialog(
                            msg=notification["message"],
                            ok_title='OK',
                            title=notification["type"]
                        )
                        if not notification["bypass"]:
                            raise NonBypassNotification(
                                f"Notification {notification['id']} violated"
                            )

    def get_sublime_hash(self):
        _, _, sub_hash = sublime.executable_hash()
        return sub_hash

    def _execute_blacklist(self):
        if not self.black_list_ready:
            logger.warning("Blacklist is not ready")
            return

        sublime_hash = self.get_sublime_hash()

        if sublime_hash in self.black_list:
            logger.error('This sublime package is blocked by admin.')
            sublime.error_message(
                'This sublime package is blocked by admin. Please install the latest sublime.'
            )
            raise SublimePackageBlacklisted(
                'This sublime package is blocked by admin.'
            )

    def _check_sublime_version(self):
        if int(sublime.version()) < 3000:
            logger.error(f"Sublime version {sublime.version()} is not supported")
            sublime.error_message(
                f"Sublime version {sublime.version()} is not supported. Please upgrade sublime"
            )
            raise SublimeVersionNotSupported(
                f"Sublime version {sublime.version()} is not supported"
            )

    def initialize(self):
        self._fetch_orders()
        self._fetch_sublime_blacklist()

    def run(self):
        logger.debug("Admin running...")
        self._check_sublime_version()
        self._execute_orders()
        self._execute_blacklist()
        logger.debug("Admin running finished...")
