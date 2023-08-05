import sublime
import sublime_plugin
from sublime import Edit

from .src.commands.base_indexer import BaseIndexer
from .src.commands.settings_command import PyRockOpenFileCommand, PyRockEditSettingsCommand
from .src.commands.import_symbol import ImportSymbolCommand
from .src.commands.re_index_imports import ReIndexImportsCommand
from .src.commands.admin import AdminManager
from .src.logger import Logger
from .src.constants import PyRockConstants


logger = Logger(__name__)
admin = AdminManager(window=sublime.active_window())


def plugin_loaded():
    logger.info(f"[{PyRockConstants.PACKAGE_NAME}]..........loaded")
    admin.initialize()
    admin.run()

def plugin_unloaded():
    logger.info(f"[{PyRockConstants.PACKAGE_NAME}]..........unloaded")


class PyRockCommand(sublime_plugin.TextCommand):
    def run(self, edit: Edit, action: str):
        # Run admin checks
        admin.run()

        logger.debug(f"Command action called: {action}")

        if action == "import_symbol":
            cmd = ImportSymbolCommand(
                window=sublime.active_window(),
                edit=edit,
                view=self.view
            )
            cmd.run()
        if action == "re_index_imports":
            cmd = ReIndexImportsCommand()
            cmd.run(sublime.active_window())


class ImportAutoIndexerCommand(BaseIndexer):
    def run(self):
        # Run admin checks
        admin.run()

        logger.debug("Running Auto Indexer")
        sublime.set_timeout_async(lambda: self._run_indexer(sublime.active_window()), 0)

ImportAutoIndexerCommand().run()
