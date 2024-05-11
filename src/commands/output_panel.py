import collections
import threading

import sublime


class OutputPanel:

    def __init__(
        self, name, word_wrap=False, line_numbers=False, gutter=False,
        scroll_past_end=False
    ):
        self.name = name
        self.window = sublime.active_window()
        self.output_view = self.window.create_output_panel(name)

        settings = self.output_view.settings()
        settings.set("word_wrap", word_wrap)
        settings.set("line_numbers", line_numbers)
        settings.set("gutter", gutter)
        settings.set("scroll_past_end", scroll_past_end)
        # settings.set("color_scheme", "Packages/PyRock/assets/test_output_color_scheme.tmTheme")

        self.output_view.assign_syntax("Packages/PyRock/assets/test_output.sublime-syntax")
        self.output_view.set_read_only(True)
        self.closed = False

        self.text_queue_lock = threading.Lock()
        self.text_queue = collections.deque()

    def write(self, s):
        with self.text_queue_lock:
            self.text_queue.append(s)

    def writeln(self, s):
        self.write(s + "\n")

    def _write(self):
        with self.text_queue_lock:
            text = ''
            while self.text_queue:
                text += self.text_queue.popleft()

        self.output_view.run_command(
            'append',
            {'characters': text, 'force': True}
        )
        self.output_view.show(self.output_view.size())

    def flush(self):
        self._write()

    def show(self):
        self.window.run_command("show_panel", {"panel": "output." + self.name})

    def close(self):
        self.flush()
        self.closed = True
