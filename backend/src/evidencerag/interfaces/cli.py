import typer

from evidencerag.adapters.storage.migrate import run_migrations
from evidencerag.settings import Settings

app = typer.Typer(no_args_is_help=True)


@app.callback()
def main() -> None:
    """EvidenceRAG command-line interface."""


@app.command()
def migrate() -> None:
    """Apply pending SQL migrations."""
    for result in run_migrations(Settings().database_url):
        typer.echo(f"{result.status:>8}  {result.version:04d}_{result.name}")
