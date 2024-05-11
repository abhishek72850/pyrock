import os
import sublime
from unittesting import DeferrableTestCase
from PyRock.src.constants import PyRockConstants


class PyRockTestBase(DeferrableTestCase):
    def setUp(self):
        self.view = sublime.active_window().new_file(
            syntax='Packages/Python/Python.sublime-syntax'
        )
        self.window = self.view.window()
        self.sublime_settings = sublime.load_settings("Preferences.sublime-settings")
        self.sublime_settings.set("close_windows_when_empty", False)
        self.test_file_view = None

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def _open_test_fixture_file(self):
        file_path = os.path.join(
            PyRockConstants.PACKAGE_TEST_FIXTURES_DIR, 'test_fixture.py'
        )

        for win in sublime.windows():
            test_file_view = win.find_open_file(file_path)

            if test_file_view is not None:
                break

        if test_file_view is None:
            test_file_view = sublime.active_window().open_file(
                fname=file_path
            )

            # wait for view to open
            while test_file_view.is_loading():
                pass

        self.test_file_view = test_file_view

