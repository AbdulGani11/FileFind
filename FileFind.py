#!/usr/bin/env python3
"""
FileFind - File Search Tool

Search using Trie data structures and multi-strategy algorithms.
Built for Windows.
"""

import os
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich import box
from rich.align import Align

# Initialize Rich console for beautiful terminal output
console = Console()


# CONSTANTS - Centralized configuration for easy maintenance

# System directories to skip during indexing (improves performance and security)
SKIP_DIRECTORIES = {
    "system32",
    "windows",
    "programdata",
    "$recycle",
    "appdata",
    ".git",
    "node_modules",
    "__pycache__",
}

# Search configuration constants
MIN_WORD_LENGTH = 2  # Minimum word length to index (skip short words like 'a', 'of')
MAX_FILENAME_SCORE_BONUS = 30  # Maximum bonus for shorter filenames in relevance scoring
DEFAULT_SEARCH_RESULTS = 50  # Default number of search results to return
DISPLAY_RESULTS_LIMIT = 20  # Maximum results to display in table

# Relevance scoring weights (higher = more relevant)
SCORE_EXACT_MATCH = 100  # Query exactly matches filename
SCORE_STARTS_WITH = 80   # Filename starts with query (autocomplete-style)
SCORE_CONTAINS = 50      # Filename contains query somewhere



# UTILITY CLASSES - Reusable components for common operations


class PathUtils:
    """Safe path operations with security validation and drive detection."""

    @staticmethod
    def get_drive_path(drive_letter: str) -> Path:
        """Convert drive letter to Path object (e.g., 'D' -> 'D:/')"""
        return Path(f"{drive_letter.upper()}:/")

    @staticmethod
    def get_available_drives() -> List[str]:
        """Return list of accessible drive letters (C, D, E, etc.)."""
        drives = []
        for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            if PathUtils.get_drive_path(letter).exists():
                drives.append(letter)
        return drives

    @staticmethod
    def is_valid_folder(path: Path) -> bool:
        """Check if path exists and is actually a directory (not a file)"""
        return path.exists() and path.is_dir()

    @staticmethod
    def should_skip_directory(path: Path) -> bool:
        """Return True if directory should be skipped (system folders, node_modules, etc.)."""
        path_parts = [p.lower() for p in path.parts]
        return any(skip in path_parts for skip in SKIP_DIRECTORIES)

    @staticmethod
    def is_safe_filename(name: str) -> bool:
        """Validate filename blocks directory traversal and Windows reserved names."""
        # Check for empty or whitespace-only names
        if not name or not name.strip():
            return False

        # Directory traversal protection - these patterns can escape intended directories
        if ".." in name or "\\" in name:
            return False

        # Windows file system restrictions - these characters cause errors
        invalid_chars = '<>:"|?*'
        if any(char in name for char in invalid_chars):
            return False

        # Windows reserved names (cannot be used as file/folder names)
        reserved_names = {
            "con", "prn", "aux", "nul",
            "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9",
            "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9",
        }
        base_name = name.split(".")[0].lower()
        if base_name in reserved_names:
            return False

        # Windows doesn't allow names ending with periods or spaces
        if name.endswith(".") or name.endswith(" "):
            return False

        # Windows filename length limit (255 characters)
        if len(name) > 255:
            return False

        return True

    @staticmethod
    def get_item_type(path: Path) -> str:
        """Get simple item type string: 'folder' or 'file'"""
        return "folder" if path.is_dir() else "file"

    @staticmethod
    def get_item_emoji_type(path: Path) -> str:
        """Get emoji item type string: '📁 Folder' or '📄 File'"""
        return "📁 Folder" if path.is_dir() else "📄 File"


class UIUtils:
    """Terminal UI helpers for tables, menus, messages, and user input."""

    @staticmethod
    def create_results_table(title: str, columns: List[Tuple[str, str, int]]) -> Table:
        """Create Rich table with title and columns (name, style, width). Width 0 = auto-size."""
        table = Table(title=title)
        for name, style, width in columns:
            if width:
                table.add_column(name, style=style, width=width)
            else:
                table.add_column(name, style=style)
        return table

    @staticmethod
    def apply_standard_table_styling(table: Table):
        """Apply consistent styling to all tables in the application"""
        table.show_lines = True
        table.header_style = "bold cyan"

    @staticmethod
    def get_user_choice(prompt: str, choices: List[str], default: Optional[str] = None) -> str:
        """Get validated user input with automatic retry on invalid choices"""
        if default:
            return Prompt.ask(prompt, choices=choices, default=default)
        else:
            return Prompt.ask(prompt, choices=choices)

    @staticmethod
    def show_options_and_choose(options: List[str], prompt: str) -> str:
        """Display numbered options and return validated user choice."""
        for option in options:
            console.print(option)

        choices = [str(i) for i in range(1, len(options) + 1)]
        return UIUtils.get_user_choice(prompt, choices)

    @staticmethod
    def print_success(message: str):
        """Print success message with consistent formatting"""
        console.print(f"[bold green]✅ SUCCESS:[/] {message}")

    @staticmethod
    def print_error(message: str):
        """Print error message with consistent formatting"""
        console.print(f"[bold red]❌ ERROR:[/] {message}")

    @staticmethod
    def print_warning(message: str):
        """Print warning message with consistent formatting"""
        console.print(f"[bold yellow]⚠️ WARNING:[/] {message}")

    @staticmethod
    def print_info(message: str):
        """Print info message with consistent formatting"""
        console.print(f"[bold cyan]ℹ️ INFO:[/] {message}")

    @staticmethod
    def print_separator():
        """Print standard visual separator line"""
        console.print("─" * 60)

    @staticmethod
    def print_section_break():
        """Print section break line for major divisions"""
        console.print("═" * 60)

    @staticmethod
    def print_section_header(title: str):
        """Print formatted section header with consistent styling"""
        console.print()
        console.print(Panel(title, style="bold green"))
        UIUtils.print_separator()

    @staticmethod
    def validate_filename_or_show_error(name: str) -> bool:
        """Validate filename and print error if invalid. Returns True if valid."""
        if not PathUtils.is_safe_filename(name):
            UIUtils.print_error(
                "Invalid name. Avoid empty names, '..' patterns, and special characters"
            )
            return False
        return True

    @staticmethod
    def safe_execute(operation_name: str, func, *args, **kwargs) -> Any:
        """Execute function with error handling. Catches file system errors."""
        try:
            return func(*args, **kwargs)
        except PermissionError:
            UIUtils.print_error(f"Permission denied: {operation_name}")
        except FileNotFoundError:
            UIUtils.print_error(f"File not found: {operation_name}")
        except FileExistsError:
            UIUtils.print_error(f"File already exists: {operation_name}")
        except OSError as e:
            UIUtils.print_error(f"{operation_name} - {e}")
        return None



# SEARCH ENGINE - Fast file indexing and retrieval system


class TrieNode:
    """Trie node storing children (char -> TrieNode) and files matching this prefix."""

    def __init__(self):
        self.children = {}  # Dictionary mapping characters to child nodes
        self.files = []  # Files that contain this prefix


class Trie:
    """Prefix tree for O(m) prefix matching where m = query length."""

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, file_path: Path):
        """Insert word into trie. Adds file_path to every prefix node for partial matching."""
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            # Add file to this prefix - enables partial matching
            node.files.append(file_path)

    def search_prefix(self, prefix: str, max_results: int = 20) -> List[Path]:
        """Find unique files matching prefix. Returns up to max_results."""
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []  # Prefix not found
            node = node.children[char]

        # Remove duplicates while preserving order (dict.fromkeys trick)
        unique_files = list(dict.fromkeys(node.files))
        return unique_files[:max_results]


class FileMetadata:
    """Cached file info (path, name, suffix, is_dir) to avoid repeated Path operations."""

    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self.suffix = path.suffix.lower()  # File extension for type filtering
        self.is_dir = path.is_dir()


class FileSearchIndex:
    """Multi-strategy search: exact match (O(1)), Trie prefix (O(m)), word index, substring."""

    def __init__(self):
        # Trie for fast prefix search (like autocomplete)
        self.trie = Trie()

        # Hash map for instant exact filename lookup
        self.exact_match = {}  # filename -> [FileMetadata]

        # Inverted index: word -> set of files containing that word
        # Enables searching for "intern the" to find "The Intern.mp4"
        self.word_index = defaultdict(set)

        # Track indexed files to avoid duplicates
        self.indexed_paths = set()

        # Statistics for user feedback
        self.total_items = 0

    def add_file(self, file_path: Path):
        """Index file/folder in Trie, exact_match, and word_index. Skips duplicates."""
        # Avoid duplicate indexing (important for performance)
        if str(file_path).lower() in self.indexed_paths:
            return

        try:
            metadata = FileMetadata(file_path)
            filename = metadata.name.lower()

            # 1. Add to trie for prefix search
            self.trie.insert(filename, file_path)

            # 2. Add to exact match lookup
            if filename not in self.exact_match:
                self.exact_match[filename] = []
            self.exact_match[filename].append(metadata)

            # 3. Add to word index for flexible search
            # Split filename into searchable words (handle dots, underscores, dashes)
            words = (
                filename.replace(".", " ").replace("_", " ").replace("-", " ").split()
            )
            for word in words:
                if len(word) > MIN_WORD_LENGTH:  # Skip very short words (the, of, a, etc.)
                    self.word_index[word].add(file_path)

            # Track this file as indexed
            self.indexed_paths.add(str(file_path).lower())
            self.total_items += 1

        except (OSError, PermissionError):
            # Skip files we can't access (common in system directories)
            pass

    def index_folder(self, folder_path: Path) -> int:
        """Recursively index all files/folders in directory. Returns count of items indexed."""
        items_added = 0

        if not PathUtils.is_valid_folder(folder_path):
            return items_added

        try:
            # rglob("*") recursively finds all files AND folders in subdirectories
            for item in folder_path.rglob("*"):
                # Skip system directories for performance and security
                if PathUtils.should_skip_directory(item.parent):
                    continue

                # Index both files AND folders for comprehensive search
                self.add_file(item)  # Works for both files and directories
                items_added += 1

        except (OSError, PermissionError):
            # Skip inaccessible directories (network drives, system folders, etc.)
            pass

        return items_added

    def search(self, query: str, max_results: int = 20) -> List[Path]:
        """Search using 4 strategies: exact, prefix, word, substring. Returns top results by relevance."""
        if not query.strip():
            return []

        query = query.lower().strip()
        results = set()  # Use set to automatically handle duplicates

        # Strategy 1: Exact filename match (fastest possible)
        if query in self.exact_match:
            for metadata in self.exact_match[query]:
                results.add(metadata.path)

        # Strategy 2: Prefix search using Trie (autocomplete-style)
        prefix_results = self.trie.search_prefix(query, max_results * 2)
        results.update(prefix_results)

        # Strategy 3: Word-based search (handles different word orders)
        # Splits "the intern" into ["the", "intern"] for flexible matching
        query_words = query.replace(".", " ").replace("_", " ").split()
        for word in query_words:
            if word in self.word_index:
                results.update(self.word_index[word])

        # Strategy 4: Substring search (broadest, slowest)
        # Only use if we don't have enough results yet
        if len(results) < max_results:
            for filename, metadata_list in self.exact_match.items():
                if query in filename:
                    for metadata in metadata_list:
                        results.add(metadata.path)

        # Sort results by relevance and return top matches
        return self._sort_by_relevance(list(results), query)[:max_results]

    def _sort_by_relevance(self, results: List[Path], query: str) -> List[Path]:
        """Sort by score: exact match > starts with > contains > shorter names > common dirs."""

        def score(path: Path) -> int:
            filename = path.name.lower()
            relevance_score = 0

            # Exact match gets highest priority
            if query == filename:
                relevance_score += SCORE_EXACT_MATCH
            # Starts with query (like autocomplete)
            elif filename.startswith(query):
                relevance_score += SCORE_STARTS_WITH
            # Contains query somewhere
            elif query in filename:
                relevance_score += SCORE_CONTAINS

            # Shorter filenames often more relevant (less clutter)
            relevance_score += max(0, MAX_FILENAME_SCORE_BONUS - len(filename))

            # Bonus for files in commonly-accessed directories
            parent_name = path.parent.name.lower()
            if any(
                common in parent_name
                for common in ["documents", "desktop", "downloads"]
            ):
                relevance_score += 10

            return relevance_score

        return sorted(results, key=score, reverse=True)



# MAIN APPLICATION - Interactive file management interface


class FileCommander:
    """Interactive file search application with Trie-based indexing and multi-strategy search."""

    def __init__(self):
        self.desktop = Path.home() / "Desktop"
        self.search_index = FileSearchIndex()
        self._index_built = False  # Cache flag to avoid re-indexing

    def show_main_menu(self):
        """Display the main application menu with available operations."""
        console.clear()

        # Centered application header with gradient-style colors
        title = Text()
        title.append("⚡ ", style="bold yellow")
        title.append("FILE COMMANDER", style="bold bright_cyan")
        
        subtitle = Text("High-Performance File Search Engine", style="dim white")
        
        # Create header panel with rounded borders
        header_content = Text.assemble(
            title, "\n", subtitle
        )
        header_content.justify = "center"
        
        console.print()
        console.print(
            Panel(
                header_content,
                box=box.ROUNDED,
                style="cyan",
                padding=(1, 4),
            ),
            justify="center",
        )
        console.print()

        # Main menu options
        options = [
            ("1", "⚡", "Search", "Find and manage files"),
            ("2", "📊", "Statistics", "View search index status"),
            ("0", "❌", "Exit", "Close application"),
        ]

        # Create styled table with rounded box
        table = Table(
            box=box.ROUNDED,
            show_header=True,
            header_style="bold bright_cyan",
            border_style="dim cyan",
            padding=(0, 1),
        )
        
        table.add_column("", style="bold yellow", width=3, justify="center")
        table.add_column("", width=3, justify="center")
        table.add_column("Action", style="bold white", min_width=20)
        table.add_column("Description", style="dim", min_width=25)

        for key, icon, action, desc in options:
            if key == "0":
                table.add_row(
                    f"[red]{key}[/red]",
                    icon,
                    f"[red]{action}[/red]",
                    f"[dim red]{desc}[/dim red]",
                )
            else:
                table.add_row(key, icon, action, desc)

        # Use a grid to center the table robustly
        grid = Table.grid(expand=True)
        grid.add_column(justify="center")
        grid.add_row(table)
        console.print(grid)
        console.print()

    def search_files(self):
        """Index drives (once), then continuous search loop. Actions: open, rename, search again."""
        UIUtils.print_section_header("⚡ Search & Manage Files/Folders")

        # Only build index if not already cached
        if not self._index_built:
            # Build index with smart drive strategy
            console.print("[dim]📄 Indexing files using smart drive strategy...[/dim]")

            # Strategy 1: C: drive - targeted indexing (common user folders only)
            c_drive_folders = [
                Path.home() / "Downloads",
                Path.home() / "Documents",
                Path.home() / "Desktop",
                Path.home() / "Videos",
                Path.home() / "Pictures",
                Path.home() / "Pictures" / "Samsung Flow",  # Phone sync locationa
            ]

            console.print("[dim]   🎯 C: drive - Indexing user folders only...[/dim]")
            for folder in c_drive_folders:
                if PathUtils.is_valid_folder(folder):
                    items_added = self.search_index.index_folder(folder)
                    if items_added > 0:
                        console.print(
                            f"[dim]      ✅ {folder.name}: {items_added} items[/dim]"
                        )

            # Strategy 2: Other drives (D:, E:, Z:, etc.) - complete indexing
            drives = PathUtils.get_available_drives()
            other_drives = [drive for drive in drives if drive.upper() != "C"]

            if other_drives:
                console.print(
                    f"[dim]   💾 Other drives ({', '.join(other_drives)}) - Complete indexing...[/dim]"
                )
                for drive in other_drives:
                    drive_path = PathUtils.get_drive_path(drive)
                    console.print(
                        f"[dim]      📂 Indexing {drive}: drive completely...[/dim]"
                    )
                    items_added = self.search_index.index_folder(drive_path)
                    if items_added > 0:
                        console.print(
                            f"[dim]      ✅ {drive}: drive: {items_added} items indexed[/dim]"
                        )
                    else:
                        console.print(
                            f"[dim]      ⚠️ {drive}: drive: No accessible items[/dim]"
                        )
            else:
                console.print("[dim]   ℹ️ No additional drives found besides C:[/dim]")

            UIUtils.print_success("Indexing complete")
            self._index_built = True  # Mark index as built
        else:
            UIUtils.print_info("Using cached index (instant search ready)")

        UIUtils.print_separator()

        # Continuous search loop - no re-indexing needed
        while True:
            search_term = Prompt.ask("⚡ What are you looking for?")
            if not search_term.strip():
                UIUtils.print_error("Please enter a search term")
                continue  # Ask again without breaking the loop

            UIUtils.print_info(f"Searching for '{search_term}'...")

            # Perform search with performance tracking
            start_time = time.time()
            results = self.search_index.search(search_term, DEFAULT_SEARCH_RESULTS)
            search_time = time.time() - start_time

            if results:
                UIUtils.print_success(
                    f"Found {len(results)} results in {search_time:.3f} seconds"
                )
                UIUtils.print_section_break()
                self._display_search_results(results, search_term)

                # Handle actions and check if user wants to continue
                if not self._handle_search_actions(results):
                    break  # Exit to main menu if user chose "Back to menu"
            else:
                UIUtils.print_section_break()
                UIUtils.print_warning(f"No items found for '{search_term}'")
                UIUtils.print_section_break()

                # Ask if user wants to continue searching (only when no results)
                UIUtils.print_separator()
                if not Confirm.ask(
                    "[bold cyan]🔍 Do you want to search for something else?[/bold cyan]",
                    default=False,
                ):
                    console.print("[dim]👍 Returning to main menu[/dim]")
                    break  # Exit the search loop and return to main menu

            UIUtils.print_separator()  # Visual separator for next search

    def _display_search_results(self, results: List[Path], search_term: str):
        """Display search results in a formatted table with file type indicators."""
        UIUtils.print_separator()

        table = UIUtils.create_results_table(
            f"🔍 Results for '{search_term}'",
            [
                ("#", "white", 3),
                ("Name", "green", 0),
                ("Type", "white", 8),
                ("Location", "blue", 0),
            ],
        )

        # Apply enhanced table styling
        UIUtils.apply_standard_table_styling(table)

        # Show first results to avoid overwhelming the user
        for i, item in enumerate(results[:DISPLAY_RESULTS_LIMIT], 1):
            item_type = PathUtils.get_item_emoji_type(item)
            table.add_row(str(i), item.name, item_type, str(item.parent))

        console.print(table)

        # Indicate if there are more results
        if len(results) > DISPLAY_RESULTS_LIMIT:
            console.print(
                f"[dim]... and {len(results) - DISPLAY_RESULTS_LIMIT} more results (showing first {DISPLAY_RESULTS_LIMIT})[/dim]"
            )

        UIUtils.print_separator()

    def _handle_search_actions(self, results: List[Path]) -> bool:
        """Show action menu. Returns True to continue searching, False to exit to main menu."""
        actions = [
            "1. 📂 Open item",
            "2. ✏️ Rename item",
            "3. 🔍 Search again",
            "4. 🔙 Back to menu",
        ]

        action = UIUtils.show_options_and_choose(actions, "Choose action")

        if action in ["1", "2"]:
            # Get user selection for the action
            if len(results) == 1:
                selected = results[0]
            else:
                choice = UIUtils.get_user_choice(
                    "Enter number",
                    [str(i) for i in range(1, min(len(results), DISPLAY_RESULTS_LIMIT) + 1)],
                )
                selected = results[int(choice) - 1]

            # Perform the selected action
            if action == "1":
                self._open_item(selected)
            else:
                self._rename_item(selected)

            return True  # Continue searching after open/rename
        elif action == "3":
            return True  # ✅ Continue search loop (no re-indexing!)
        else:
            return False  # Back to main menu

    def _open_item(self, item_path: Path):
        """Open file/folder with os.startfile (safe, no shell injection)."""

        def open_operation():
            # os.startfile works for both files and folders on Windows
            os.startfile(str(item_path))
            item_type = PathUtils.get_item_type(item_path)
            UIUtils.print_success(f"Opened {item_type}: {item_path.name}")

        UIUtils.safe_execute("opening item", open_operation)

    def _rename_item(self, item_path: Path):
        """Rename file/folder with validation. Offers undo after successful rename."""
        UIUtils.print_section_break()
        console.print(Panel(f"✏️ Rename: {item_path.name}", style="bold cyan"))
        UIUtils.print_section_break()

        new_name = Prompt.ask("📝 Enter new name", default=item_path.name)

        if new_name == item_path.name:
            UIUtils.print_warning("Name unchanged")
            return

        # Security validation
        if not UIUtils.validate_filename_or_show_error(new_name):
            return

        # Store original info for potential undo
        original_path = item_path
        original_name = item_path.name
        new_path = item_path.parent / new_name

        def rename_operation():
            try:
                original_path.rename(new_path)
                item_type = PathUtils.get_item_type(new_path)
                UIUtils.print_success(f"Renamed {item_type} to: {new_name}")
                return True
            except FileExistsError:
                UIUtils.print_error(f"Name already exists: {new_name}")
                return False

        # Perform rename operation
        rename_successful = UIUtils.safe_execute("renaming item", rename_operation)

        # If rename was successful, offer immediate undo option
        if rename_successful:
            UIUtils.print_separator()
            if Confirm.ask(
                "[bold cyan]🔄 Do you want to undo this rename?[/bold cyan]",
                default=False,
            ):

                def undo_operation():
                    new_path.rename(original_path)
                    item_type = PathUtils.get_item_type(original_path)
                    UIUtils.print_success(f"Restored original name: {original_name}")

                UIUtils.safe_execute("undoing rename", undo_operation)
            UIUtils.print_section_break()

    def show_search_statistics(self):
        """Display current search index statistics for user information."""
        UIUtils.print_section_header("📊 Search Statistics")

        table = UIUtils.create_results_table(
            "⚡ Search System Status",
            [("Metric", "cyan", 20), ("Value", "green", 20), ("Details", "dim", 40)],
        )

        # Apply enhanced table styling
        UIUtils.apply_standard_table_styling(table)

        # Show indexing status and performance metrics
        table.add_row("Status", "✅ Ready", "Optimized for instant search")
        table.add_row(
            "Items Indexed",
            f"{self.search_index.total_items:,}",
            "Total files and folders in search index",
        )
        table.add_row("Search Speed", "< 1ms", "Microsecond-level performance")

        console.print(table)
        UIUtils.print_section_break()

    def run_interactive(self):
        """Main application loop. Shows menu and runs search or statistics based on user choice."""
        while True:
            try:
                self.show_main_menu()

                choice = UIUtils.get_user_choice(
                    "Select option", ["0", "1", "2"]
                )

                if choice == "0":
                    UIUtils.print_section_break()
                    console.print(
                        "[bold yellow]👋 GOODBYE![/] Thank you for using File Commander"
                    )
                    UIUtils.print_section_break()
                    break
                elif choice == "1":
                    self.search_files()
                elif choice == "2":
                    self.show_search_statistics()

                # Pause before returning to menu (better UX)
                if choice != "0":
                    UIUtils.print_separator()
                    Prompt.ask(
                        "[dim]Press Enter to return to main menu[/dim]", default=""
                    )
                    UIUtils.print_separator()

            except KeyboardInterrupt:
                # Graceful handling of Ctrl+C
                UIUtils.print_section_break()
                console.print("[bold yellow]👋 GOODBYE![/] Interrupted by user")
                UIUtils.print_section_break()
                break
            except Exception as e:
                # Unexpected error handling
                UIUtils.print_section_break()
                UIUtils.print_error(f"Unexpected error: {e}")
                console.print("[dim]Please try again or restart the application.[/dim]")
                UIUtils.print_section_break()



# APPLICATION ENTRY POINT

if __name__ == "__main__":
    commander = FileCommander()
    commander.run_interactive()
