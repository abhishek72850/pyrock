from unittest.mock import patch

from tests.base import PyRockTestBase


class TestReIndexImportsCommand(PyRockTestBase):
    def setUp(self):
        super().setUp()

    def setText(self, string):
        self.view.run_command("insert", {"characters": string})

    @patch("sublime.set_timeout_async")
    @patch("sublime.ok_cancel_dialog")
    def test_command(
        self,
        mocked_ok_cancel_dialog,
        mocked_set_timeout_async,
    ):
        mocked_ok_cancel_dialog.return_value = True
        self.view.run_command("py_rock", args={"action": "re_index_imports"})

        mocked_ok_cancel_dialog.assert_called_once_with(
            msg="Are you sure to re-index imports?",
            ok_title='Yes',
            title='Re-Index Imports'
        )

        self.assertEqual(mocked_set_timeout_async.call_count, 1)
