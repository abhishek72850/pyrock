import os
from typing import List, Dict, Optional
import sublime
from sublime import SymbolLocation, Region
from sublime import SymbolSource, SymbolType, KindId, FindFlags
import re
import json
from ..logger import Logger
from pathlib import Path
from ..constants import PyRockConstants


logger = Logger(__name__)
path = Path(__file__)


class ImportSymbolCommand:
    def __init__(self, window, edit, view, test: bool = False):
        self.window = window
        self.sublime_edit = edit
        self.view = view
        self.test = test

    def _update_existing_import_statement_region(
        self,
        existing_import_region: Region,
        selected_symbol: str,
        selected_option: str,
    ):
        # Convert region to string
        import_statement_text = self.view.substr(existing_import_region)
        logger.debug(f"Existing import statement text {import_statement_text}")

        updated_import_text: Optional[str] = None

        # If symbol already not in import statement
        if re.search(r'\b(%s)\b' % selected_symbol, import_statement_text) is None:
            # Single line import without braces
            single_line_without_braces_regex = re.compile(r"^(?:%s\s)([^)(]+)$" % selected_option)
            # Single line import with braces
            single_line_with_braces_regex = re.compile(r"^(?:%s\s)(\(([^)(\n]+)*\))$" % selected_option)
            # Multi line import with braces
            multi_line_with_braces_regex = re.compile(
                r"^(?:%s\s)(\(([^)(]+)*\))$" % selected_option, re.MULTILINE
            )

            if single_line_without_braces_regex.search(import_statement_text):
                updated_import_text = f"{import_statement_text}, {selected_symbol}"
            elif single_line_with_braces_regex.search(import_statement_text):
                updated_import_text = f"{import_statement_text[:-1]}, {selected_symbol})"
            elif multi_line_with_braces_regex.search(import_statement_text):
                if "\t" in import_statement_text:
                    # If tab is used for indentation
                    replace_text = f",\n\t{selected_symbol},\n)"
                elif "    " in import_statement_text:
                    # If 4 space is used for indentation
                    replace_text = f",\n    {selected_symbol},\n)"
                else:
                    replace_text = f",\n{selected_symbol},\n)"

                # Substitute with ending comma, new line and braces
                updated_import_text = re.sub(r"(,)?(\n)?\)", replace_text, import_statement_text)

        logger.debug(f"Updated import statement text: {updated_import_text}")

        if updated_import_text:
            self.view.run_command(
                "py_rock_replace_text",
                {
                    "start": existing_import_region.begin(),
                    "end": existing_import_region.end(),
                    "text": updated_import_text
                }
            )
    
    def _insert_new_import_statement_region(
        self,
        selected_import_option: str,
    ):
        # Match to all the imports
        match_all_imports_regex = r"^(?:(from\s.+)?import\s)((\(([^)(]+)*\))|(.+))$"
        # Find region
        matched_regions: List[Region] = self.view.find_all(pattern=match_all_imports_regex, flags=FindFlags.IGNORECASE)
        logger.debug(f"Matched regions list {matched_regions}")

        if matched_regions:
            # Convert region to string
            last_matched_region = self.view.substr(matched_regions[-1])
            logger.debug(f"Last matched regions {last_matched_region}")

            added_import = f"{last_matched_region}\n{selected_import_option}"

            logger.debug(f"Added import {added_import}")

            self.view.run_command(
                "py_rock_replace_text",
                {
                    "start": matched_regions[-1].begin(),
                    "end": matched_regions[-1].end(),
                    "text": added_import
                }
            )
        else:
            logger.debug("No import statement found, adding to the top")
            self.view.run_command(
                "py_rock_replace_text",
                {
                    "start": 0,
                    "end": 0,
                    "text": selected_import_option
                }
            )
    
    def _add_import_to_view(self, index: int):
        if index < 0:
            logger.debug("Not selected any item, returning")
            return

        logger.debug(f"Select {index} from popup menu")
        import_option_list: List[str] = list(self.import_statements.keys())
        selected_option = self.import_statements[import_option_list[index]]["from_part"]
        selected_symbol = self.import_statements[import_option_list[index]]["symbol"]

        logger.debug(f"Selected option {selected_option} and symbol {selected_symbol}")

        if self.copy:
            logger.debug(f"Copying import statement {import_option_list[index]}")
            sublime.set_clipboard(import_option_list[index])
            return

        # Match import statement region like
        # 1. from foo.bar import foo
        # 2. from foo.bar import (
        #        foo
        #    )
        regex = r"^(?:%s\s)((\(([^)(]+)*\))|(.+))$" % selected_option
        existing_import_region: Region = self.view.find(pattern=regex, start_pt=0, flags=FindFlags.IGNORECASE)

        if existing_import_region:
            logger.debug(f"Found existing import region: {existing_import_region}")
            self. _update_existing_import_statement_region(
                existing_import_region,
                selected_symbol,
                selected_option,
            )
        else:
            self._insert_new_import_statement_region(
                import_option_list[index]
            )


    def load_user_python_imports(self) -> Optional[Dict[str, Dict]]:
        import time
        file_path = os.path.join(
            PyRockConstants.INDEX_CACHE_DIRECTORY,
            PyRockConstants.IMPORT_INDEX_FILE_NAME
        )

        import_map: Dict[str, Dict] = {}
        start_time = time.perf_counter()
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                import_map = json.load(f)
        else:
            logger.debug("No user python import index found")
            return None

        logger.debug(f"Time taken to load index: {time.perf_counter() - start_time}")

        return import_map

    def generate_imports_from_sublime_result(
        self,
        selected_text: str,
        symbol_locations: List[SymbolLocation]
    ) -> Dict[str, Dict]:
        import_statements: Dict[str, Dict] = {}

        for symbol_location in symbol_locations:
            if symbol_location.display_name.endswith(".py"):
                import_statements[
                    f"from {symbol_location.display_name.replace('.py', '').replace('/', '.')} import {selected_text}"
                ] = {
                    "from_part": f"from {symbol_location.display_name.replace('.py', '').replace('/', '.')} import",
                    "symbol": selected_text,
                }
        return import_statements

    def generate_imports_from_user_python_imports(
        self,
        selected_text: str,
        user_python_import_map: Dict[str, Dict]
    ) -> Dict[str, Dict]:
        import_statements: Dict[str, Dict] = {}

        if user_python_import_map.get(selected_text[0], {}).get(selected_text[-1]):
            import_paths = user_python_import_map[selected_text[0]][selected_text[-1]]

            for import_path in import_paths:
                path_split = import_path.split('.')
                if path_split[-1] == selected_text:
                    if len(path_split) > 1:
                        import_statements[f"from {'.'.join(path_split[:-1])} import {selected_text}"] = {
                            "from_part": f"from {'.'.join(path_split[:-1])} import",
                            "symbol": selected_text,
                        }
                    else:
                        import_statements[f"import {selected_text}"] = {
                            "from_part": f"import {selected_text}",
                            "symbol": selected_text,
                        }
        return import_statements

    def run(self, copy: bool = False):
        self.copy = copy
        selected_view = self.view.sel()[0]
        selected_text: Optional[str] = self.view.substr(selected_view)

        logger.debug(f"Selected text {selected_text}")

        if len(selected_text) < 2:
            logger.info("Select at least 2 characters")
            sublime.status_message(
                "Select at least 2 characters"
            )
            return

        user_python_import_map: Optional[Dict[str, Dict]] = self.load_user_python_imports()

        symbol_locations: List[SymbolLocation] = self.view.window().symbol_locations(
            sym=selected_text,
            source=SymbolSource.INDEX,
            type=SymbolType.DEFINITION,
            kind_id=KindId.AMBIGUOUS,
            kind_letter=''
        )
        logger.debug(f"Sublime importer result {symbol_locations}")

        self.import_statements: Dict[str, Dict] = {}

        if selected_text:
            self.import_statements = self.generate_imports_from_sublime_result(
                selected_text,
                symbol_locations
            )

        if user_python_import_map and selected_text:
            self.import_statements.update(
                self.generate_imports_from_user_python_imports(
                    selected_text,
                    user_python_import_map
                )
            )

        self.import_statements = dict(
            sorted(
                self.import_statements.items(),
                # put imports first, then sort by depth, then by name
                key=lambda k: (
                    not k[0].startswith("import "),
                    k[0].count("."),
                    k[0],
                ),
            )
        )

        self.view.erase_status(PyRockConstants.PACKAGE_NAME)
        self.view.set_status(
            PyRockConstants.PACKAGE_NAME,
            f"Found {len(self.import_statements)} imports"
        )

        if len(self.import_statements) > 0:
            if self.test:
                self._add_import_to_view(index=0)
            else:
                self.view.show_popup_menu(
                    items=list(self.import_statements.keys()),
                    on_done=self._add_import_to_view,
                    flags=0
                )
