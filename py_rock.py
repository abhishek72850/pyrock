import sublime
import sublime_plugin
from sublime import Edit
from typing import Optional

# Reloads the submodules
# import importlib
# from .src import reloader
# importlib.reload(reloader)
# reloader.reload()

from .src.commands.base_indexer import BaseIndexer
from .src.commands.import_symbol import ImportSymbolCommand
from .src.commands.re_index_imports import ReIndexImportsCommand
from .src.commands.admin import AdminManager
from .src.logger import Logger
from .src.constants import PyRockConstants
from .src.commands.copy_test_path import CopyTestPathCommand
from .src.commands.annotate_and_test_runner import AnnotateAndTestRunnerCommand


logger = Logger(__name__)
admin = AdminManager(window=sublime.active_window())
test_runner_cmd = AnnotateAndTestRunnerCommand()


def plugin_loaded():
    logger.debug(f"[{PyRockConstants.PACKAGE_NAME}]..........loaded")
    admin.initialize()
    admin.run()

    settings = sublime.load_settings(PyRockConstants.PACKAGE_SETTING_NAME)
    logger.debug(f"[{PyRockConstants.PACKAGE_NAME}] Settings: {settings}")

def plugin_unloaded():
    logger.debug(f"[{PyRockConstants.PACKAGE_NAME}]..........unloaded")


class PyRockCommand(sublime_plugin.TextCommand):
    def run(self, edit: Edit, action: str, test: bool = False):
        # Run admin checks
        admin.run()

        logger.debug(f"Command action called: {action}")

        if action == "import_symbol":
            cmd = ImportSymbolCommand(
                window=sublime.active_window(),
                edit=edit,
                view=self.view,
                test=test,
            )
            cmd.run()
        elif action == "copy_import_symbol":
            cmd = ImportSymbolCommand(
                window=sublime.active_window(),
                edit=edit,
                view=self.view,
                test=test,
            )
            cmd.run(copy=True)
        elif action == "re_index_imports":
            cmd = ReIndexImportsCommand(test=test)
            cmd.run(sublime.active_window())
        elif action == "copy_test_path":
            cmd = CopyTestPathCommand(
                view=self.view,
                test=test,
            )
            cmd.run()
        else:
            logger.debug("Inavlid command recieved")

    def is_enabled(self, action: str, test: bool = False):
        """
            Disable command if view is not python file or syntax is not python
        """
        file_name: Optional[str] = self.view.file_name()
        if (file_name and file_name.endswith(".py")) or self.view.syntax().name == "Python":
            return True
        logger.debug("View is not python file or have a python syntax, disabling commands")
        return False

class ImportAutoIndexerCommand(BaseIndexer):
    def run(self):
        # Run admin checks
        admin.run()

        logger.debug("Running Auto Indexer")
        sublime.set_timeout_async(lambda: self._run_indexer(sublime.active_window()), 0)

ImportAutoIndexerCommand().run()


class PyRockReplaceTextCommand(sublime_plugin.TextCommand):
    """
        The py_rock_replace_text command implementation,
        for some reason on linux the view insert and replace
        method doesn't work, so as a alternative created this command
        to put text in the view.
    """

    def run(self, edit: Edit, start: int, end: int, text: str):
        """Replace the content of a region with new text.

        Arguments:
            edit (Edit):
                The edit object to identify this operation.
            start (int):
                The beginning of the Region to replace.
            end (int):
                The end of the Region to replace.
            text (string):
                The new text to replace the content of the Region with.
        """
        region = sublime.Region(start, end)
        self.view.replace(edit, region, text)


class PyRockAnnotateAndTestRunnerCommand(sublime_plugin.ViewEventListener):
    def on_load_async(self):
        logger.debug("View loaded")
        test_runner_cmd.run(self.view)

    def on_activated_async(self):
        logger.debug("View reloaded")
        test_runner_cmd.run(self.view)

    def on_post_save_async(self):
        logger.debug("View saved")
        test_runner_cmd.run(self.view)
