import typer
import re
import sys
from typing_extensions import Annotated
from typing import List
from pathlib import Path
from .prompts import version_callback, format_callback, console, err_console
from .ledger import ledger_load
from enum import Enum
from beanquery import query
from beanquery.query_render import render_text, render_csv

class Placeholder(str, Enum):
    named = "named"
    indexed = "indexed"
    blank = "blank"

def which_type(text):
    if valid_pyname(text):
        return Placeholder.named
    elif valid_int(text):
        return Placeholder.indexed
    elif not text:
        return Placeholder.blank
    else:
        return None

def valid_pyname(name):
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name))

def valid_int(num):
    return bool(re.match(r'^\d+$', num))

def valid_query(line):
    pattern = r'^\s*(\d{4}-\d{2}-\d{2})\s+query\s+"([^"]+)"\s+"([^"]*)"\s*$'
    match = re.match(pattern, line.strip())
    if match:
        return {
            'date': match.group(1),
            'name': match.group(2),
            'query_string': match.group(3)
        }
    return None

def get_placeholders(query_string):
    # Find all placeholders like {0}, {1}, {name}, or {}
    placeholders = []

    # Match all placeholders (e.g., {name}, {0}, {})
    matches = re.findall(r'\{([^}]*)\}', query_string)
    if not len(matches):
        return placeholders, ''
    expected = which_type(matches[0])
    if expected is not None:
        for placeholder in matches:
            if which_type(placeholder) != expected:
                return None
            else:
                placeholders.append(placeholder)
    else:
        return None

    if expected != Placeholder.blank:
        placeholders = list(set(placeholders))

    return placeholders, expected

def parse_params(params, placeholders, placeholders_type, placeholders_string):
    if not params and not placeholders:
        return []
    if (not params and placeholders) or (len(params) != len(placeholders)):
        err_console.print(f"[error]Parameter and placeholder count do not match, needed ({len(placeholders)}): {placeholders_string}[/]")
        return None

    if placeholders_type == Placeholder.named:
        params_dict = {}
        for p in params:
            item = p.split(":", 1)
            if len(item) != 2:
                err_console.print(f"[error]Named parameters must each be split with a ':'[/]")
                return None
            if item[0] not in placeholders:
                err_console.print(f"[error]Parameter key '{item[0]}' does not exist in placeholders: {placeholders_string}[/]")
                return None
            params_dict[item[0]] = item[1]
        if not all(key in params_dict for key in placeholders):
            err_console.print(f"[error]Must provide all placeholder keys: {placeholders_string}[/]")
            return None
        return params_dict

    return params

def run_query(ledger_data, query_string):
    try:
        rtypes, rrows = query.run_query(ledger_data.entries, ledger_data.options, query_string, numberify=True)
        return rtypes, rrows
    except Exception as e:
        err_console.print(f"[error]Error executing query: {str(e)}[/]")
        return None, None

def bean_inquiry(
    ledger: Annotated[Path, typer.Argument(
        help="The beancount ledger file to parse",
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True)],
    name: Annotated[str, typer.Argument(
        help="The name of the query to parse",
        show_default=False)] = "",
    params: Annotated[List[str], typer.Argument(
        help="List of parameters to inject",
        show_default=False)] = None,
    format: Annotated[str, typer.Option(
        "--format", "-f",
        help="Output format: 'text' or 'csv'",
        callback=format_callback)] = 'text',
    check: Annotated[bool, typer.Option(
        "--check", "-c",
        help="Check a query for what parameters are needed",
        show_default=False)] = False,
    list_queries: Annotated[bool, typer.Option(
        "--list", "-l",
        help="List all queries available in ledger",
        show_default=False)] = False,
    output: Annotated[Path, typer.Option(
        "--output", "-o",
        help="The output file to write to instead of stdout",
        show_default=False, exists=False)]=None,
    version: Annotated[bool, typer.Option(
        "--version", "-v",
        help="Show version info and exit",
        callback=version_callback, is_eager=True)] = False
):
    """
    Inject parameters into beancount queries specified in your ledger
    """

    # Load ledger
    if ledger is None:
        err_console.print("[error]No ledger file provided. Please provide a ledger file.[/]")
        raise typer.Exit()
    console.print(f"Loading ledger [file]{ledger}[/]")
    ledger_data = ledger_load(ledger)

    # Check queries
    if ledger_data.queries is None or not len(ledger_data.queries):
        console.print("[warning]No queries found in ledger[/]")
    console.print(f"Found [number]{len(ledger_data.queries)}[/] queries in ledger")

    # List queries
    if list_queries:
        console.print()
        for q in ledger_data.queries:
            console.print(q.name)
        raise typer.Exit()

    # Get query
    if not name:
        err_console.print("[error]Please provide a query name to parse")
        raise typer.Exit()
    query_entry = next((q for q in ledger_data.queries if q.name == name), None)
    if not query_entry:
        err_console.print(f"[error]No query found with the name [string]'{name}'[/]. Valid names are:\n")
        for q in ledger_data.queries:
            console.print(q.name)
        raise typer.Exit()
    console.print(f"[string]{query_entry.name}[/]{query_entry.query_string}")

    # Get placeholders
    placeholders_result = get_placeholders(query_entry.query_string)
    if not placeholders_result:
        err_console.print("[error]Invalid placeholder format. All placeholders must be of the same type. (e.g. named: {name}, indexed: {0}, or empty: {})[/]")
        raise typer.Exit()
    placeholders, placeholders_type = placeholders_result
    placeholders_list = ["{" + p + "}" for p in placeholders]
    placeholders_string = ', '.join(sorted(placeholders_list))
    if check:
        if placeholders_list:
            console.print(f"Required parameters for query [string]'{name}'[/] ({len(placeholders)}): {placeholders_string}")
        else:
            console.print(f"No parameters required for query [string]'{name}'[/]")
        raise typer.Exit()

    # Parse parameters
    parsed_params = parse_params(params, placeholders, placeholders_type, placeholders_string)
    if parsed_params is None:
        raise typer.Exit()

    # Format query with parameters
    query_string = ''
    try:
        if parsed_params:
            if isinstance(parsed_params, (list, tuple)):
                query_string = query_entry.query_string.format(*parsed_params)
            elif isinstance(parsed_params, dict):
                query_string = query_entry.query_string.format(**parsed_params)
            console.print(f"[string]{query_entry.name}[/](injected){query_string}")
        else:
            query_string = query_entry.query_string
    except (KeyError, IndexError, ValueError) as e:
        err_console.print(f"[error]Error formatting query with parameters: {str(e)}[/]")
        raise typer.Exit()

     # Execute query
    rtypes, rrows = run_query(ledger_data, query_string)
    if rtypes is None or rrows is None:
        raise typer.Exit(code=1)

    # Render results
    try:
        console.print()
        if format == 'text':
            if output:
                with output.open('w', encoding='utf-8') as f:
                    render_text(rtypes, rrows, ledger_data.options['dcontext'], file=f)
            else:
                render_text(rtypes, rrows, ledger_data.options['dcontext'], sys.stdout)
        elif format == 'csv':
            if output:
                with output.open('w', encoding='utf-8') as f:
                    render_csv(rtypes, rrows, ledger_data.options['dcontext'], file=f)
            else:
                render_csv(rtypes, rrows, ledger_data.options['dcontext'], sys.stdout)
    except Exception as e:
        err_console.print(f"[error]Error rendering output: {str(e)}[/]")
        raise typer.Exit(code=1)

    if output: console.print(f"Saved to [file]{output}[/]")
