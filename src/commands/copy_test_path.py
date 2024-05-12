import sublime
from typing import Optional
from sublime import View
from ..logger import Logger
from .unittest_path_generator import TestPathGenerator
from ..settings import PyRockSettings
from ..utils import is_test_file


logger = Logger(__name__)


class CopyTestPathCommand:
    def __init__(self, view: View, test: bool = False):
        self.view = view
        self.test = test

    def run(self):
        if not is_test_file(self.view.file_name()):
            logger.info("Not a test file, returning")
            return

        selected_view = self.view.sel()[0]
        selected_text: Optional[str] = self.view.substr(selected_view)
        logger.debug(f"Selected test method: {selected_text}")

        test_path = TestPathGenerator.generate(
            selected_view, self.view, PyRockSettings().TEST_CONFIG.TEST_FRAMEWORK
        )
        logger.debug(f"Generated test path: {test_path}")

        if test_path:
            sublime.set_clipboard(test_path)
        else:
            sublime.status_message(
                "Could not generate test path"
            )
            logger.info("Couldn't find path")
