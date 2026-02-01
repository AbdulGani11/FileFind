# FileFind

[![CI](https://github.com/AbdulGani11/file-commander/actions/workflows/ci.yml/badge.svg)](https://github.com/AbdulGani11/file-commander/actions)
![Platform Windows](https://img.shields.io/badge/platform-Windows-blue.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**File search tool for Windows.** Uses Trie data structures and multi-strategy algorithms for O(m) search complexity where m = query length.

---

## Key Features

*   **Multi-Strategy Search**: Combines 4 search algorithms (exact match, Trie prefix, word index, substring).
*   **Trie Data Structure**: O(m) prefix matching where m = query length. Search time depends only on query length, not collection size.
*   **Smart Indexing**: Targeted C: drive indexing (user folders only) and complete indexing for other drives.
*   **Relevance Ranking**: Results sorted by exact match, prefix match, filename length, and common directory location.
*   **Security Validation**: Blocks directory traversal attacks, Windows reserved names, and invalid characters.
*   **CI/CD Tested**: Automated testing on Python 3.10, 3.11, and 3.12 with GitHub Actions.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/AbdulGani11/file-commander.git
    cd file-commander
    ```

2.  **Set up environment:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the app:
```bash
python file-commander.py
```

### What can it do?
Interactive menu with two options:
1.  **Search**: Find files with multi-strategy search. Open or rename with undo support.
2.  **Statistics**: View indexed file counts and performance metrics.

### How It Works

1.  **Smart Indexing**: On first search, indexes your drives using a smart strategy:
    *   C: drive - Only indexes common user folders (Desktop, Documents, Downloads, Pictures, Videos)
    *   Other drives - Complete indexing of all accessible files
2.  **Multi-Strategy Search**: When you search, runs 4 parallel algorithms:
    *   Exact match for direct filename hits
    *   Trie prefix matching for autocomplete-style results
    *   Word index for multi-word queries
    *   Substring search as fallback
3.  **Relevance Ranking**: Results sorted by exact matches first, then prefix matches, then by filename length and directory frequency
4.  **File Operations**: Select results to open with default app or rename with undo support

## Development & Testing

**Run Tests:**
```bash
pytest
```

**Test Results:**
```
7 passed in 0.07s ✅

Test Coverage:
✓ Filename validation (security, length limits, reserved names)
✓ Drive path detection and conversion
✓ File/folder type identification
✓ Trie insert and prefix search
✓ Case-insensitive search
✓ Search index operations
✓ Relevance-based ranking
```

**Auto-Checks (CI):**
GitHub Actions automatically runs tests on Python 3.10, 3.11, and 3.12 for every push.

## Technical Details (For Developers)

*   **Language**: Python 3.10+ (with Type Hints)
*   **Data Structure**: Prefix Trie & Inverted Index
*   **UI Library**: Rich
*   **Testing**: Pytest & GitHub Actions

## License

MIT License © 2025 Abdul Gani
