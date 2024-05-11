from unittest.mock import patch

import sublime
from sublime import FindFlags

from tests.base import PyRockTestBase


class TestImportSymbol(PyRockTestBase):
    def setUp(self):
        super().setUp()

    def setText(self, string):
        self.view.run_command("insert", {"characters": string})

    @patch("PyRock.src.commands.import_symbol.ImportSymbolCommand.load_user_python_imports")
    def test_import_symbol(
        self,
        mocked_load_user_python_imports,
    ):
        mocked_load_user_python_imports.return_value = {
            "c": {
                "h": [
                    "cmath"
                ]
            }
        }

        insert_text = "cmath"
        self.setText(insert_text)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(0, len(insert_text)))

        selected_text = self.view.substr(self.view.sel()[0])
        self.assertEqual(selected_text, "cmath")

        self.view.run_command("py_rock", args={"action": "import_symbol", "test": True})
        expected_import_statement = self.view.substr(
            self.view.find("import cmath", 0, flags=FindFlags.LITERAL)
        )
        self.assertEqual(expected_import_statement, "import cmath")

    @patch("PyRock.src.commands.import_symbol.ImportSymbolCommand.load_user_python_imports")
    def test_multi_line_import(
        self,
        mocked_load_user_python_imports,
    ):
        mocked_load_user_python_imports.return_value = {
            "c": {
                "h": [
                    "cmath"
                ]
            }
        }

        insert_text = "import subprocess\ncmath"
        self.setText(insert_text)
        self.view.sel().clear()

        region_to_select = self.view.find("cmath", 0, flags=FindFlags.LITERAL)
        self.view.sel().add(region_to_select)

        self.view.run_command("py_rock", args={"action": "import_symbol", "test": True})
        expected_import_statement = self.view.substr(
            self.view.find("import cmath", 0, flags=FindFlags.LITERAL)
        )
        self.assertEqual(expected_import_statement, "import cmath")

    def test_import_with_existing_import_statement(self):
        insert_text = "import cmath\ncmath"
        self.setText(insert_text)
        self.view.sel().clear()

        region_to_select = self.view.find("cmath", 0, flags=FindFlags.LITERAL)
        self.view.sel().add(region_to_select)

        self.view.run_command("py_rock", args={"action": "import_symbol", "test": True})
        expected_import_statement_regions = self.view.find_all(
            "import cmath", flags=FindFlags.LITERAL
        )
        self.assertEqual(len(expected_import_statement_regions), 1)

    @patch("PyRock.src.commands.import_symbol.ImportSymbolCommand.load_user_python_imports")
    def test_add_module_import_in_existing_import(
        self,
        mocked_load_user_python_imports,
    ):
        mocked_load_user_python_imports.return_value = {
            "l": {
                "0": [
                    "cmath.log10"
                ]
            }
        }

        insert_text = "from cmath import sin\nlog10"
        self.setText(insert_text)
        self.view.sel().clear()

        region_to_select = self.view.find("log10", 0, flags=FindFlags.LITERAL)
        self.view.sel().add(region_to_select)

        self.view.run_command("py_rock", args={"action": "import_symbol", "test": True})
        expected_import_statement = self.view.substr(
            self.view.find(
                "from cmath import sin, log10", 0, flags=FindFlags.LITERAL
            )
        )
        self.assertEqual(expected_import_statement, "from cmath import sin, log10")

    @patch("PyRock.src.commands.import_symbol.ImportSymbolCommand.load_user_python_imports")
    def test_copy_import_symbol(
        self,
        mocked_load_user_python_imports,
    ):
        mocked_load_user_python_imports.return_value = {
            "c": {
                "h": [
                    "cmath"
                ]
            }
        }

        insert_text = "cmath"
        self.setText(insert_text)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(0, len(insert_text)))

        selected_text = self.view.substr(self.view.sel()[0])
        self.assertEqual(selected_text, "cmath")

        self.view.run_command(
            "py_rock", args={"action": "copy_import_symbol", "test": True}
        )

        expected_import_statement = sublime.get_clipboard()
        self.assertEqual(expected_import_statement, "import cmath")
