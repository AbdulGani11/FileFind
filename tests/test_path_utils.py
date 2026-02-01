from pathlib import Path
import pytest

def test_is_safe_filename(path_utils):
    # Valid names
    assert path_utils.is_safe_filename("document.pdf")
    assert path_utils.is_safe_filename("New Folder")
    
    # Invalid names (empty)
    assert not path_utils.is_safe_filename("")
    assert not path_utils.is_safe_filename("   ")
    
    # Directory traversal attempts
    assert not path_utils.is_safe_filename("../escaped")
    assert not path_utils.is_safe_filename("..\\escaped")
    
    # Windows invalid characters
    assert not path_utils.is_safe_filename("invalid<")
    assert not path_utils.is_safe_filename("invalid>")
    assert not path_utils.is_safe_filename("invalid:")
    assert not path_utils.is_safe_filename("invalid\"")
    assert not path_utils.is_safe_filename("invalid|")
    assert not path_utils.is_safe_filename("invalid?")
    assert not path_utils.is_safe_filename("invalid*")

    # Windows reserved names
    assert not path_utils.is_safe_filename("CON")
    assert not path_utils.is_safe_filename("con.txt")
    assert not path_utils.is_safe_filename("NUL")
    assert not path_utils.is_safe_filename("COM1")
    assert not path_utils.is_safe_filename("LPT1.log")

    # Names ending with period or space
    assert not path_utils.is_safe_filename("file.")
    assert not path_utils.is_safe_filename("file ")

    # Backslash in name (path traversal)
    assert not path_utils.is_safe_filename("sub\\file")

    # Filename length limits (Windows max = 255 chars)
    assert path_utils.is_safe_filename("a" * 255)  # Exactly 255 chars - valid
    assert not path_utils.is_safe_filename("a" * 256)  # 256 chars - invalid

def test_get_drive_path(path_utils):
    assert path_utils.get_drive_path("c") == Path("C:/")
    assert path_utils.get_drive_path("D") == Path("D:/")

def test_get_item_type(path_utils, tmp_path):
    # Create test items
    d = tmp_path / "folder"
    d.mkdir()
    f = tmp_path / "file.txt"
    f.touch()
    
    assert path_utils.get_item_type(d) == "folder"
    assert path_utils.get_item_type(f) == "file"
