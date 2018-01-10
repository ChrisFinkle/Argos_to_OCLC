import sys
import os
from cx_Freeze import setup, Executable

os.environ['TCL_LIBRARY'] = 'C:\\Users\\cfinkle\\AppData\\Local\\Programs\\Python\\Python36\\tcl\\tcl8.6'
os.environ['TK_LIBRARY'] = 'C:\\Users\\cfinkle\\AppData\\Local\\Programs\\Python\\Python36\\tcl\\tk8.6'

include_files = ["C:\\Users\\cfinkle\\AppData\\Local\\Programs\\Python\\Python36\\DLLs\\tcl86t.dll",
				 "C:\\Users\\cfinkle\\AppData\\Local\\Programs\\Python\\Python36\\DLLs\\tk86t.dll"]

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os", "re", "tkinter"],
					 "include_files": include_files}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "OCLCT",
        version = "0.1",
        description = "Transfers data from Argos form to OCLC form",
        options = {"build_exe": build_exe_options},
        executables = [Executable("OCLC_transfer.py", base=base)])