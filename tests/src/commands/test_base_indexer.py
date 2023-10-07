import sublime
from unittest import mock
from tests.base import PyRockTestBase
from PyRock.src.commands.base_indexer import BaseIndexer


class TestIndexer(PyRockTestBase):
    def setUp(self):
        super().setUp()

    @mock.patch("PyRock.src.commands.base_indexer.BaseIndexer._run_import_indexer")
    def test_run_indexer(
        self,
        mocked_run_import_indexer,
    ):
        mocked_run_import_indexer.return_value = (True, "")

        base_indexer = BaseIndexer()
        base_indexer._run_indexer(self.window, True)

        import_command = base_indexer._get_import_command()

        mocked_run_import_indexer.assert_called_once_with(self.window, import_command)
