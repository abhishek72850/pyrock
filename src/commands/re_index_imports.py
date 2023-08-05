import sublime
from sublime import Window
from ..commands.base_indexer import BaseIndexer
from ..logger import Logger
from pathlib import Path


logger = Logger(__name__)
path = Path(__file__)


class ReIndexImportsCommand(BaseIndexer):
    def run(self, window: Window):
        result: bool = sublime.ok_cancel_dialog(
            msg="Are you sure to re-index imports?",
            ok_title='Yes',
            title='Re-Index Imports'
        )
        if result:
            sublime.set_timeout_async(lambda: self._run_indexer(window, True), 0)
