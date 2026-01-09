import typer
from .bean_import import bean_import
from .download import download
from .version import version

app = typer.Typer(no_args_is_help=True)
app.command(name="import")(bean_import)
app.command(name="download")(download)
app.command(name="version")(version)

if __name__ == "__main__":
    app()
