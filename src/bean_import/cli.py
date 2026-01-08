import typer
from .bean_import import bean_import
from .download import download

app = typer.Typer()
app.command(name="import")(bean_import)
app.command(name="download")(download)

if __name__ == "__main__":
    app()
