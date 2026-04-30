from rich.console import Console
from rich.table import Table


console = Console()
error_console = Console(stderr=True)


def print_stage(step, total, title):
    console.rule(f"Stage {step}/{total}: {title}")


def print_summary(title, rows):
    table = Table(title=title)
    table.add_column("Metric")
    table.add_column("Value", justify="right")

    for label, value in rows:
        table.add_row(label, str(value))

    console.print(table)
