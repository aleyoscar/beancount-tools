import typer
from .helpers import (
    #get_key, set_key,
    get_json,
    set_json,
    cur
) #replace_lines, cur, append_lines, dec, eval_string_dec, eval_string_float, get_pending, get_matches
from .ledger import ledger_load
# from .ofx import ofx_load
# from .simplefin import simplefin_load
from .prompts import (
    console,
    err_console,
    month_callback,
    version_callback,
    ValidOptions,
    edit_bills_toolbar,
    cancel_bindings,
    cancel_toolbar,
    valid_tag,
    valid_account,
    valid_float,
    valid_day
) #resolve_toolbar, confirm_toolbar, valid_date, valid_link_tag, is_account, postings_toolbar, valid_math_float
from . import __version__
from pathlib import Path
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyCompleter, WordCompleter
from typing_extensions import Annotated
from datetime import date

def print_bill(bill, spacing=20):
    return f"[{int(bill['due']):02d}] {bill['tag']}{' '*(spacing - len(bill['tag']))} | {cur(bill['amount'])}"

def bean_bills(
    ledger: Annotated[Path, typer.Argument(
        help="The beancount ledger file to parse",
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True)],
    # output: Annotated[Path, typer.Option("--output", "-o", help="The output file to write to instead of stdout", show_default=False, exists=False)]=None,
    month: Annotated[str, typer.Option(
        "--month", "-m",
        help="Specify the billing month in the format YYYY-MM",
        callback=month_callback)]=date.today().strftime('%Y-%m'),
    version: Annotated[bool, typer.Option(
        "--version", "-v",
        help="Show version info and exit",
        callback=version_callback, is_eager=True)]=False,
    config: Annotated[Path, typer.Option(
        "--config", "-c",
        help="Specify the configuration file to use",
        exists=False)]="bills.json",
    edit: Annotated[bool, typer.Option(
        "--edit", "-e",
        help="Edit config file by adding/editing/removing bill entries")]=False
):
    """
    Review and keep track of bill payments in a beancount ledger
    """

    console.print(f"LEDGER File: [file]{ledger}[/]\nCONFIG File: [file]{config}[/]\nMONTH: [date]{month}[/]")

    bills = get_json(config, [])
    ledger_data = ledger_load(err_console, ledger)
    account_completer = FuzzyCompleter(WordCompleter(ledger_data.accounts, sentence=True))

    # Edit config file
    if edit:
        console.print(f"\n[warning]Editing bills configuration[/]: [file]{config}[/]\n")
        edit_cancelled = False
        while True:
            for i, bill in enumerate(bills):
                console.print(print_bill(bill, spacing))
            index_prompt = "[0]" if len(bills) == 1 else f"[0-{len(bills)-1}]"
            valid_indexes = [str(n) for n in range(len(bills))]
            if not len(bills):
                console.print(f"\nNo bills in configuration\n")
            edit_option = prompt(
                f"\n...Enter an option > ",
                validator=ValidOptions(['a', 'add', 'd', 'delete', 'e', 'edit', 's', 'save']),
                bottom_toolbar=edit_bills_toolbar,
                key_bindings=cancel_bindings)

            if edit_option is None:
                edit_cancelled = True
                break
            else:
                edit_option = edit_option.lower()

            # Add
            if edit_option[0] == 'a':
                console.print("\n[pos]Adding bill[/]\n")
                edit_add_tag = prompt(
                    f"...Bill tag > ",
                    key_bindings=cancel_bindings,
                    bottom_toolbar=cancel_toolbar,
                    validator=valid_tag)
                if edit_add_tag is None:
                    continue
                edit_add_account = prompt(
                    f"...Bill main account > ",
                    key_bindings=cancel_bindings,
                    bottom_toolbar=cancel_toolbar,
                    validator=valid_account,
                    completer=account_completer)
                if edit_add_account is None:
                    continue
                edit_add_liability = prompt(
                    f"...Bill liability account > ",
                    key_bindings=cancel_bindings,
                    bottom_toolbar=cancel_toolbar,
                    validator=valid_account,
                    completer=account_completer)
                if edit_add_liability is None:
                    continue
                edit_add_amount = prompt(
                    f"...Bill amount > ",
                    key_bindings=cancel_bindings,
                    bottom_toolbar=cancel_toolbar,
                    validator=valid_float)
                if edit_add_amount is None:
                    continue
                edit_add_due = prompt(
                    f"...Bill due day > ",
                    key_bindings=cancel_bindings,
                    bottom_toolbar=cancel_toolbar,
                    validator=valid_day)
                if edit_add_due is None:
                    continue
                bills.append({
                    "tag": edit_add_tag,
                    "account": edit_add_account,
                    "liability": edit_add_liability,
                    "amount": edit_add_amount,
                    "due": edit_add_due
                })
                bills.sort(key=lambda x: x['tag'])
                bills.sort(key=lambda x: int(x['due']))
                console.print(f"\n[pos]Added '{edit_add_tag}'[/]\n")
                continue

            # Delete
            if edit_option[0] == 'd':
                if not len(bills):
                    console.print("\n[warning]No bills to delete[/]\n")
                    continue
                edit_delete = prompt(
                    f"...Select bill to delete {index_prompt}> ",
                    key_bindings=cancel_bindings,
                    bottom_toolbar=cancel_toolbar,
                    validator=ValidOptions(valid_indexes))
                if edit_delete is None:
                    continue
                index = int(edit_delete)
                console.print(f"\n[error]Deleting [{index}] {bills[index]['tag']}[/]\n")
                bills.pop(int(edit_delete))
                continue

            # Edit
            if edit_option[0] == 'e':
                if not len(bills):
                    console.print("\n[warning]No bills to edit[/]\n")
                    continue
                edit_edit = prompt(
                    f"...Select bill to edit {index_prompt}> ",
                    key_bindings=cancel_bindings,
                    bottom_toolbar=cancel_toolbar,
                    validator=ValidOptions(valid_indexes))
                if edit_edit is None:
                    continue
                index = int(edit_edit)
                console.print(f"\n[warning]Editing [{index}] {bills[index]['tag']}[/]\n")
                edit_edit_tag = prompt(
                    f"...Bill tag > ",
                    key_bindings=cancel_bindings,
                    bottom_toolbar=cancel_toolbar,
                    validator=valid_tag,
                    default=bills[index]['tag'])
                if edit_edit_tag is None:
                    continue
                edit_edit_account = prompt(
                    f"...Bill main account > ",
                    key_bindings=cancel_bindings,
                    bottom_toolbar=cancel_toolbar,
                    validator=valid_account,
                    completer=account_completer,
                    default=bills[index]['account'])
                if edit_edit_account is None:
                    continue
                edit_edit_liability = prompt(
                    f"...Bill liability account > ",
                    key_bindings=cancel_bindings,
                    bottom_toolbar=cancel_toolbar,
                    validator=valid_account,
                    completer=account_completer,
                    default=bills[index]['liability'])
                if edit_edit_liability is None:
                    continue
                edit_edit_amount = prompt(
                    f"...Bill amount > ",
                    key_bindings=cancel_bindings,
                    bottom_toolbar=cancel_toolbar,
                    validator=valid_float,
                    default=bills[index]['amount'])
                if edit_edit_amount is None:
                    continue
                edit_edit_due = prompt(
                    f"...Bill due day > ",
                    key_bindings=cancel_bindings,
                    bottom_toolbar=cancel_toolbar,
                    validator=valid_day,
                    default=bills[index]['due'])
                if edit_edit_due is None:
                    continue
                bills[index] = {
                    "tag": edit_edit_tag,
                    "account": edit_edit_account,
                    "liability": edit_edit_liability,
                    "amount": edit_edit_amount,
                    "due": edit_edit_due
                }
                bills.sort(key=lambda x: x['tag'])
                bills.sort(key=lambda x: int(x['due']))
                console.print(f"\n[warning]Edited '{edit_edit_tag}'[/]\n")
                continue

            # Save
            if edit_option[0] == 's' or edit_option == '':
                set_json(bills, config)
                console.print("\n[number]Saved configuration[/]")
                break
        typer.Exit()

    if not len(bills):
        console.print("[warning]No bills in config file. Please add some bills[/]")
        typer.Exit()

    # Check pending bills if no other option selected
    pending = []
    for txn in ledger_data.transactions:
        if 'bill' in txn.entry.tags and month == txn.entry.date.strftime('%Y-%m') and txn.entry.flag == '!':
            for bill in bills:
                for link in txn.entry.links:
                    if bill['tag'] in link:
                        pending.append(txn)
    if not len(pending):
        console.print("\n[pos]No pending bills found![/]")
        typer.Exit()
    else:
        console.print("\n[warning]Pending bills:[/]\n")
        for p in pending:
            console.print(p.print_head())
    typer.Exit()
