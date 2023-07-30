import sublime
import sublime_plugin


class PyRockCommand(sublime_plugin.Command):
    def run(self, action: str):
        sublime.run_command(action)
