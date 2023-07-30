import os
import sys
from subprocess import Popen, PIPE
from typing import List
import sublime
import sublime_plugin
from sublime import Window
from src.commands.base_indexer import BaseIndexer
from src.settings import PyRockSettings
from src.constants import PyRockConstants
from src.logger import get_logger
from pathlib import Path
import subprocess
import json
import time


logger = get_logger(__name__)
path = Path(__file__)


class ReIndexImportsCommand(sublime_plugin.WindowCommand, BaseIndexer): 
    def run(self, window: Window):
        sublime.set_timeout_async(lambda: self._run_indexer(window), 0)
