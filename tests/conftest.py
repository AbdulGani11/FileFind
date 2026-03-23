import sys
import importlib.util
from pathlib import Path
import pytest

# Helper to import the module
def import_filefind():
    file_path = Path(__file__).parent.parent / "FileFind.py"
    spec = importlib.util.spec_from_file_location("FileFind", file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["FileFind"] = module
    spec.loader.exec_module(module)
    return module

fc = import_filefind()

@pytest.fixture
def path_utils():
    return fc.PathUtils

@pytest.fixture
def trie():
    return fc.Trie()

@pytest.fixture
def search_index():
    return fc.FileSearchIndex()