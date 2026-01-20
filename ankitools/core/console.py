import re
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.markup import escape

console = Console()

def print_change_preview(changes: List[Dict[str, str]]) -> None:
    """
    Prints a rich table preview of the changes.
    
    Args:
        changes: List of dicts with 'word', 'old', 'new' keys.
                 'new' is expected to contain <u><b>...</b></u> tags for the cloze.
    """
    if not changes:
        console.print("[yellow]No changes to display.[/yellow]")
        return

    table = Table(title="Proposed Changes")

    table.add_column("Word", style="cyan", no_wrap=True)
    table.add_column("Original", style="white")
    table.add_column("Cloze", style="white")

    for change in changes:
        word = change.get("word", "")
        old = change.get("old", "")
        new = change.get("new", "")

        # 1. Escape the string to handle existing brackets safely
        new_escaped = escape(new)
        
        # 2. Replace <u><b>...</b></u> with rich markup
        # Note: We assume the tags themselves are not escaped by rich (they aren't)
        # and that the content inside was properly escaped in step 1.
        new_rich = re.sub(r'<u><b>(.*?)</b></u>', r'[bold green]\1[/bold green]', new_escaped)
        
        table.add_row(word, old, new_rich)

    console.print(table)
