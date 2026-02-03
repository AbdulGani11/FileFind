import sys
import importlib.util
from pathlib import Path
import pytest

# Helper to import the module
def import_file_commander():
    # UPDATED: Changed filename to FileFind.py
    file_path = Path(__file__).parent.parent / "FileFind.py"
    
    # UPDATED: Changed internal name to FileFind
    spec = importlib.util.spec_from_file_location("FileFind", file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["FileFind"] = module
    spec.loader.exec_module(module)
    return module

fc = import_file_commander()

@pytest.fixture
def mock_file_structure(tmp_path):
    """Create a temporary file structure for testing."""
    root = tmp_path / "test_root"
    root.mkdir()
    
    # Create some files
    (root / "doc1.txt").write_text("content")
    (root / "image.jpg").write_text("content")
    (root / "folder1").mkdir()
    (root / "folder1" / "doc2.pdf").write_text("content")
    
    return root

@pytest.fixture
def path_utils():
    return fc.PathUtils

@pytest.fixture
def trie():
    return fc.Trie()

@pytest.fixture
def search_index():
    return fc.FileSearchIndex()