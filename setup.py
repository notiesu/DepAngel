"""Setup
steps: obtain standard libraries"""

import sysconfig
import os
import pkgutil
import json
import site
import sys

STD_LIB_PATH = sysconfig.get_paths()["stdlib"]
SITE_PACK_PATH = sysconfig.get_paths()["purelib"]

def walk_directory(directory: str, entries: dict[str, str]) -> None:
        """Recursively walk through a directory and return a list of files."""
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    name = os.path.splitext(file)[0]
                    entries[name] = "module"
            for dir in dirs:
                if os.path.isfile(os.path.join(root, dir, "__init__.py")):
                    entries[dir] = "package"

def get_std_libs():
    """Get a list of standard libraries."""
    
    stdlib_path = sysconfig.get_paths()["stdlib"]
    entries = {}

    walk_directory(stdlib_path, entries)
    #Check for builtins
    for item in sys.builtin_module_names:
        entries[item] = "builtin"
    return entries

if __name__ == "__main__":
    # Get the list of standard libraries/external packages
    std_libs = get_std_libs()
    site_pkgs = site.getsitepackages()
    site_libs = {}
    for site_pkg in site_pkgs:
        for pkg in pkgutil.iter_modules([site_pkg]):
            if pkg.ispkg:
                site_libs[pkg.name] = "package"
            else:
                site_libs[pkg.name] = "module"

    with open("src/std_libs.json", "w") as f:
        # Write the list of standard libraries to a JSON file
        json.dump(std_libs, f, indent=4)
    with open("src/site_libs.json", "w") as f:
        # Write the list of external packages to a JSON file
        json.dump(site_libs, f, indent=4)
    # Print the list of standard libraries
    
#update static file with list of standard libraries -

# from tree_sitter import Language
# import os

# # Paths
# BUILD_DIR = "build"
# LIB_NAME = "my-languages.so"
# LIB_PATH = os.path.join(BUILD_DIR, LIB_NAME)
# GRAMMAR_DIRS = ["tree-sitter-python"]

# # Make sure build directory exists
# os.makedirs(BUILD_DIR, exist_ok=True)

# # Build the shared library
# Language.build_library(
#     LIB_PATH,
#     GRAMMAR_DIRS
# )

# print(f"✅ Built: {LIB_PATH}")
