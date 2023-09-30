import sublime
from unittest import mock
from tests.base import PyRockTestBase
from pyrock.py_rock import ImportAutoIndexerCommand

class TestPyRock(PyRockTestBase):
    def setUp(self):
        super().setUp()

    @mock.patch("PyRock.src.commands.re_index_imports.ReIndexImportsCommand.run")
    @mock.patch("PyRock.src.commands.import_symbol.ImportSymbolCommand.run")
    def test_py_rock_action_import_symbol(
        self,
        mock_import_symbol_run,
        mock_re_index_run
    ):
        self.view.run_command("py_rock", args={"action": "import_symbol", "test": True})
        mock_import_symbol_run.assert_called_once()
        mock_re_index_run.assert_not_called()

        mock_import_symbol_run.reset_mock()
        mock_re_index_run.reset_mock()

        self.view.run_command("py_rock", args={"action": "re_index_imports", "test": True})
        mock_import_symbol_run.assert_not_called()
        mock_re_index_run.assert_called_once_with(sublime.active_window())

    @mock.patch("sublime.set_timeout_async")
    def test_auto_indexer_command(self, mocked_set_timeout_async):
        auto_indexer = ImportAutoIndexerCommand()
        auto_indexer.run()
        mocked_set_timeout_async.assert_called()
