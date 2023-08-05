import os
import sublime
from sublime import Window
from ..settings import PyRockSettings
from ..constants import PyRockConstants
from ..logger import Logger
from pathlib import Path
import subprocess
import json
import time


logger = Logger(__name__)
path = Path(__file__)


class BaseIndexer:
    def _generate_serialized_settings(self):
        settings = {
            "IMPORT_SCAN_DEPTH": PyRockSettings().IMPORT_SCAN_DEPTH.value,
            "INDEX_CACHE_DIRECTORY": PyRockConstants.INDEX_CACHE_DIRECTORY,
            "IMPORT_INDEX_FILE_NAME": PyRockConstants.IMPORT_INDEX_FILE_NAME
        }

        settings_path = os.path.join(path.parent.parent, 'serialized_settings.json')

        with open(settings_path, "w") as f:
            json.dump(settings, f)

    def _get_indexer_script_path(self):
        return os.path.join(path.parent.parent, 'scripts', 'indexer.py')
    
    def _is_indexing_needed(self) -> bool:
        file_path = os.path.join(PyRockConstants.INDEX_CACHE_DIRECTORY, PyRockConstants.IMPORT_INDEX_FILE_NAME)
        return os.path.exists(file_path)
    
    def _run_import_indexer(self, window: Window, indexer_command: str):
        process = subprocess.Popen(
            indexer_command,
            shell=True,
            stdout=subprocess.PIPE,
        )

        start_time = time.perf_counter()

        # Progress tracker
        for line in iter(process.stdout.readline, ""):
            progress = line.decode('utf-8').strip()
            # Kill process after 20 sec
            if (time.perf_counter() - start_time) > 20:
                logger.warning(f"Indexing stopped due to timeout at {progress}%")
                process.terminate()
                break
            logger.debug(f"Indexing imports...{progress}%")
            window.status_message(f"Indexing imports...{progress}%")
            if "99" in str(line) or progress == "":
                break
    
    def _run_indexer(self, window: Window, force=False):
        if self._is_indexing_needed() and not force:
            logger.debug("Indexing not needed")
            window.status_message("Indexing not needed")
            return

        self._generate_serialized_settings()

        window.set_status_bar_visible(True)

        window.status_message("Indexing imports...")

        unix_env_bash = """
            set -e
            source "{venv_path}"
            python -u "{indexer_script_path}"
            deactivate
        """
        unix_without_env_bash = """
            set -e
            python -u "{indexer_script_path}"
        """

        windows_env_bash = """
            "{venv_path}"
            python -u "{indexer_script_path}"
            deactivate
        """
        windows_without_env_bash = """
            python -u "{indexer_script_path}"
            deactivate
        """

        if sublime.platform() in [
            PyRockConstants.PLATFORM_LINUX,
            PyRockConstants.PLATFORM_OSX
        ]:
            if PyRockSettings().PYTHON_VIRTUAL_ENV_PATH.value:
                import_command = unix_env_bash.format(
                    venv_path=PyRockSettings().PYTHON_VIRTUAL_ENV_PATH.value,
                    indexer_script_path=self._get_indexer_script_path()
                )
            else:
                import_command = unix_without_env_bash.format(
                    indexer_script_path=self._get_indexer_script_path()
                )
        else:
            if PyRockSettings().PYTHON_VIRTUAL_ENV_PATH.value:
                import_command = windows_env_bash.format(
                    venv_path=PyRockSettings().PYTHON_VIRTUAL_ENV_PATH.value,
                    indexer_script_path=self._get_indexer_script_path()
                )
            else:
                import_command = windows_without_env_bash.format(
                    indexer_script_path=self._get_indexer_script_path()
                )
        
        logger.debug(f"Import shell command using: {import_command}")
        self._run_import_indexer(window, import_command)

        window.status_message("Finished imports...")
