import typer
from .bean_import import bean_import
from .bean_download import bean_download
from .bean_version import bean_version

app = typer.Typer(no_args_is_help=True)
app.command(name="import")(bean_import)
app.command(name="download")(bean_download)
app.command(name="version")(bean_version)

if __name__ == "__main__":
    app()
