import importlib
import os
from types import ModuleType
from typing import Optional

def import_sub_module(module_path) -> Optional[ModuleType]:
  """
    :module_path -> In form of "Plugin.foo.bar"
  """
  try:
    print(f"Reloading: {module_path}")
    return importlib.import_module(module_path)
  except ModuleNotFoundError:
    print(f"Unable to import {module_path}")
    return None

def walk_sub_modules(plugin_name, base_path):
  for dir, _, files in os.walk(base_path):
    parent_module_imported = False
    # If its a root directory
    if plugin_name == os.path.basename(dir):
      parent_module_path = plugin_name
    else:
      # This gives result as Plugin.foo.bar
      parent_module_path = f"{plugin_name}{'.'.join(str(dir).split(plugin_name)[-1].split(os.path.sep))}"
    for file in files:
      file_name, extension = os.path.splitext(file)
      if extension == '.py':
        # Importing once only
        if not parent_module_imported:
          # Only trying to import parent once we know it has .py file
          import_sub_module(parent_module_path)
          parent_module_imported = True
        # Importing .py file
        import_sub_module(f"{parent_module_path}.{file_name}")

def reload():
  plugin = None
  try:
    plugin = importlib.import_module("PyRock")
  except ModuleNotFoundError:
    plugin = importlib.import_module("pyrock")
  
  if not plugin:
    return
  walk_sub_modules("PyRock", plugin.__path__[0])
