import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": [],
                     "excludes": ["tkinter", "email", "tcl", "bz2",
                                  "_hashlib", "_ssl", "_imaging"],
                     "include_files":
                     [],
                     "create_shared_zip": False,
                     "optimize": 1,
                     "includes": ["lxml._elementpath"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="python_game",
      version="0.1",
      description="python game",
      options={"build_exe": build_exe_options},
      executables=[Executable("main.py", base=base,
                   appendScriptToExe=True,
                   appendScriptToLibrary=False)])
