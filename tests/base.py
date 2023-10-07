import sublime
from unittesting import DeferrableTestCase


class PyRockTestBase(DeferrableTestCase):
    def setUp(self):
        self.view = sublime.active_window().new_file(
            syntax='Packages/Python/Python.sublime-syntax'
        )
        self.window = self.view.window()
        self.sublime_settings = sublime.load_settings("Preferences.sublime-settings")
        self.sublime_settings.set("close_windows_when_empty", False)

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

