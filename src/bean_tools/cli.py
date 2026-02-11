import typer
from .bean_import import bean_import
from .bean_download import bean_download
from .bean_version import bean_version
from .bean_bills import bean_bills
from .bean_inquiry import bean_inquiry

app = typer.Typer(no_args_is_help=True)
app.command(name="bills")(bean_bills)
app.command(name="download")(bean_download)
app.command(name="import")(bean_import)
app.command(name="inquiry")(bean_inquiry)
app.command(name="version")(bean_version)

if __name__ == "__main__":
    app()
