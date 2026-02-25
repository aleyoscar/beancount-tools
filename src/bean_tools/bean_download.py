import typer, os, base64, requests, json
from .prompts import confirm_toolbar, ValidOptions, date_callback, version_callback, console, err_console
from .helpers import get_timestamp
from typing_extensions import Annotated
from pathlib import Path
from dotenv import dotenv_values
from prompt_toolkit import prompt
from datetime import datetime

def aggregator_callback(aggregator_str: str):
    if aggregator_str != 'simplefin':
        raise typer.BadParameter("Invalid aggregator, currently supported aggregators are 'simplefin'.")
    return aggregator_str

def get_access_url():
    """
    Retreive access url from a SimpleFIN setup token

    Returns:
        access_url: The access url string
    """
    access_url = ''
    get_access_response = prompt(
        f"...No '.env' found with an access url. Would you like to create one?",
        default='y',
        bottom_toolbar=confirm_toolbar,
        validator=ValidOptions(['y', 'n'])
    ).lower()
    if get_access_response == 'n':
        return ''
    setup_token = prompt(
        '...Please enter your SimpleFIN setup token: ',
        key_bindings=cancel_bindings
    )
    if setup_token:
        decoded_token = base64.b64decode(setup_token, validate=True)
        claim_url = decoded_token.decode('utf-8')
        response = requests.posts(claim_url)
        access_url = response.text
        console.print(f"Access url: [string]{access_url}[/]")
        save_env = prompt(
            "...Would you like to save the access url to a .env file?",
            default="y",
            bottom_toolbar=confirm_toolbar,
            validator=ValidOptions(['y', 'n'])
        ).lower()
        if save_env == 'y':
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(f"ACCESS_URL={access_url}\n")
            console.print(f"Saved access url to [file].env[/]")
    return access_url

def bean_download(
    aggregator: Annotated[str, typer.Argument(help="Specify the aggregator to use", callback=aggregator_callback)]="simplefin",
    output: Annotated[Path, typer.Option("--output", "-o", help="The output file to use for the downloaded transactions", exists=False)]="data.json",
    start_date: Annotated[str, typer.Option("--start-date", "-s", help="Retreive transactions on or after this date in the format YYYY-MM-DD", callback=date_callback)]="",
    end_date: Annotated[str, typer.Option("--end-date", "-e", help="Retreive transactions before (but not including) this date in the format YYYY-MM-DD", callback=date_callback)]="",
    pending: Annotated[bool, typer.Option("--pending", "-p", help="Include pending transactions")]=False,
    version: Annotated[bool, typer.Option("--version", "-v", help="Show version info and exit", callback=version_callback, is_eager=True)]=False
):
    """
    Download transactions from an aggregator. Currently supported aggregators are: SimpleFIN
    """

    if aggregator == 'simplefin':
        access_url = ''
        if not os.path.exists('.env'):
            access_url = get_access_url()
        else:
            env_vars = dotenv_values('.env')
            if not 'ACCESS_URL' in env_vars:
                access_url = get_access_url()
            else: access_url = env_vars['ACCESS_URL']
            if not access_url:
                err_console.print(f"[error]Could not get a valid access url. Exiting[/]")
                raise typer.Exit()
            scheme, rest = access_url.split('//', 1)
            auth, rest = rest.split('@', 1)
            parameters = []
            parameters_str = ''
            if start_date: parameters.append(f"start-date={get_timestamp(start_date)}")
            if end_date: parameters.append(f"end-date={get_timestamp(end_date)}")
            if pending: parameters.append(f"pending=1")
            if len(parameters): parameters_str = f"?{'&'.join(parameters)}"
            url = f"{scheme}//{rest}/accounts{parameters_str}"
            username, password = auth.split(':', 1)
            response = requests.get(url, auth=(username, password))
            data = response.json()
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            if data['errors'] and len(data['errors']):
                console.print(f"SimpleFIN error messages:\n")
                err_count = 1
                for err in data['errors']:
                    console.print(f"  {err_count}) [warning]{err}[/]")
                    err_count += 1
            console.print(f"\nSaved SimpleFIN data to [file]{output}[/]")
