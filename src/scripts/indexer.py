import os
import sys
import json
import pkgutil
import inspect
import json
from collections import defaultdict
import importlib
from typing import List, Dict, Tuple, Set
from types import FunctionType, ModuleType
import logging
from pathlib import Path


logger = logging.getLogger(__name__)
path = Path(__file__)


class Indexer:
    def __init__(self):
        self.import_path_count: int = 0
        self.imports_map = defaultdict(lambda: defaultdict(lambda: []))
    
    def parse_serialized_settings(self):
        settings_path = os.path.join(path.parent.parent, 'serialized_settings.json')
        with open(settings_path, 'r') as f:
            self.settings = json.load(f)

    def save_imports_to_cache(self):
        base_directory_path: str = self.settings["INDEX_CACHE_DIRECTORY"]

        if not os.path.exists(base_directory_path):
            os.mkdir(base_directory_path)

        file_path: str = os.path.join(base_directory_path, self.settings["IMPORT_INDEX_FILE_NAME"])

        logger.debug(f"Saving imports index at: {file_path}")

        with open(file_path, 'w') as f:
            json.dump(self.imports_map, f)

    def _store_in_map(self, import_path: str):
        entity: str = import_path.split('.')[-1]
        first_letter: str = entity[0]
        last_letter: str = entity[-1]

        if first_letter not in self.imports_map:
            self.imports_map[first_letter] = {}

        if last_letter in self.imports_map[first_letter]:
            self.imports_map[first_letter][last_letter].append(import_path)
        else:
            self.imports_map[first_letter][last_letter] = [import_path]
        
        self.import_path_count += 1

    def get_class_members(self, module) -> List[Tuple[str, object]]:
        try:
            return inspect.getmembers(module, inspect.isclass)
        except Exception:
            return []

    def get_function_members(self, module) -> List[Tuple[str, FunctionType]]:
        try:
            return inspect.getmembers(module, inspect.isfunction)
        except Exception:
            return []

    def get_module_members(self, module) -> List[Tuple[str, ModuleType]]:
        try:
            return inspect.getmembers(module, inspect.ismodule)
        except Exception:
            return []

    def _index_module_class_and_function_members(
        self,
        parent_module_path: str,
        module: ModuleType,
    ):
        module_classes: List[Tuple[str, object]] = self.get_class_members(module)
        for class_name, class_obj in module_classes:
            class_path = f"{parent_module_path}.{class_name}"
            self._store_in_map(class_path)
    
        module_functions: List[Tuple[str, FunctionType]] = self.get_function_members(module)
        for function_name, function_obj in module_functions:
            function_path = f"{parent_module_path}.{function_name}"
            self._store_in_map(function_path)

    def _index_sub_module_members(
        self,
        parent_module_name: str,
        sub_modules: List[Tuple[str, ModuleType]],
    ):
        # Import depth, default 4
        if len(parent_module_name.split('.')) >= self.settings["IMPORT_SCAN_DEPTH"]:
            return []

        for module_name, module_obj in sub_modules:
            module_path = f"{parent_module_name}.{module_name}"
            
            self._index_module_class_and_function_members(
                module_path,
                module_obj
            )

            self._store_in_map(module_path)

            self._index_sub_module_members(
                f"{parent_module_name}.{module_name}",
                self.get_module_members(module_obj)
            )

    def run(self):
        self.parse_serialized_settings()

        system_module_name_list: Set[str] = {
            module[1] for module in pkgutil.iter_modules(
                path=sys.path
            )
        }

        total_modules = len(system_module_name_list)

        for index, module_name in enumerate(system_module_name_list):
            if "sublime" in module_name or "xkcd" in module_name or "antigravity" in module_name:
                continue

            self._store_in_map(module_name)

            sys.stdout = sys.stderr = os.devnull
            try:
                module: ModuleType = importlib.import_module(module_name)
            except Exception as e:
                module = None
            sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__

            if module is None:
                continue

            self._index_module_class_and_function_members(
                module_name,
                module
            )

            sub_modules: List[Tuple[str, ModuleType]] = self.get_module_members(module)
            self._index_sub_module_members(module_name, sub_modules)

            progress = int((index/total_modules) * 100)

            try:
                print(progress, flush=True)
            except BrokenPipeError:
                if progress < 90:
                    continue
                logger.debug("Broken pipe caught")
        
        logger.debug(f"Imported path count: {self.import_path_count}")

        self.save_imports_to_cache()

if __name__ == '__main__':
    Indexer().run()
