import typer
from .helpers import (
    #get_key, set_key,
    get_json,
    set_json,
    cur,
    append_lines
) #replace_lines, cur, append_lines, dec, eval_string_dec, eval_string_float, get_pending, get_matches
from .ledger import ledger_load, ledger_bean, new_bean
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
    confirm_toolbar,
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
from datetime import date, datetime

def print_bill(bill, spacing=20):
    return f"({int(bill['due']):02d}) {bill['tag']}{' '*(spacing - len(bill['tag']))} | {cur(bill['amount'])}"

def bean_bills(
    ledger: Annotated[Path, typer.Argument(
        help="The beancount ledger file to parse",
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True)],
    output: Annotated[Path, typer.Option(
        "--output", "-o",
        help="The output file to write to instead of stdout",
        show_default=False, exists=False)]=None,
    month: Annotated[str, typer.Option(
        "--month", "-m",
        help="Specify the billing month in the format YYYY-MM",
        callback=month_callback)]=date.today().strftime('%Y-%m'),
    version: Annotated[bool, typer.Option(
        "--version", "-v",
        help="Show version info and exit",
        callback=version_callback, is_eager=True)]=False,
    config: Annotated[Path, typer.Option(
        "--config", "-C",
        help="Specify the configuration file to use",
        exists=False)]="bills.json",
    edit: Annotated[bool, typer.Option(
        "--edit", "-e",
        help="Edit config file by adding/editing/removing bill entries")]=False,
    operating_currency: Annotated[bool, typer.Option(
        "--operating-currency", "-c",
        help="Skip the currency prompt when inserting and use the ledger's operating_currency")]=False,
    default_currency: Annotated[str, typer.Option(
        "--default-currency", "-d",
        help="Use the specified currency when inserting transactions")]='USD'
):
    """
    Review and keep track of bill payments in a beancount ledger
    """

    bills = get_json(config, default=[], overwrite_invalid=False)
    if bills is None:
        err_console.print("\n[error]Invalid config JSON[/]\n")
        raise typer.Exit()
    if not len(bills):
        console.print("\n[warning]No bills in config file. Please add some bills[/]")
        raise typer.Exit()

    spacing = 0
    for bill in bills:
        spacing = max(spacing, len(bill['tag']))

    ledger_data = ledger_load(err_console, ledger)
    account_completer = FuzzyCompleter(WordCompleter(ledger_data.accounts, sentence=True))
    currency = ledger_data.currency if operating_currency else default_currency

    console.print(f"LEDGER File: [file]{ledger}[/]")
    console.print(f"CONFIG File: [file]{config}[/]")
    console.print(f"MONTH: [date]{month}[/]")
    console.print(f"CURRENCY: [number]{currency}[/]")
    if output: console.print(f"OUTPUT: [file]{output}[/]")

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
                edit_add_payee = prompt(
                    f"...Bill payee > ",
                    key_bindings=cancel_bindings,
                    bottom_toolbar=cancel_toolbar)
                if edit_add_payee is None:
                    continue
                bills.append({
                    "tag": edit_add_tag,
                    "account": edit_add_account,
                    "liability": edit_add_liability,
                    "amount": edit_add_amount,
                    "due": edit_add_due,
                    "payee": edit_add_payee
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
                edit_edit_payee = prompt(
                    f"...Bill payee > ",
                    key_bindings=cancel_bindings,
                    bottom_toolbar=cancel_toolbar,
                    default=bills[index]['payee'])
                if edit_edit_payee is None:
                    continue
                bills[index] = {
                    "tag": edit_edit_tag,
                    "account": edit_edit_account,
                    "liability": edit_edit_liability,
                    "amount": edit_edit_amount,
                    "due": edit_edit_due,
                    "payee": edit_edit_payee
                }
                bills.sort(key=lambda x: x['tag'])
                bills.sort(key=lambda x: int(x['due']))
                console.print(f"\n[pos]Edited '{edit_edit_tag}'[/]\n")
                continue

            # Save
            if edit_option[0] == 's' or edit_option == '':
                set_json(bills, config)
                console.print("\n[number]Saved configuration[/]")
                break
        raise typer.Exit()

    # Check for unpaid, pending and missing bills
    unpaid = [] # Bills yet unpaid
    pending = [] # Bills paid but not yet reconciled
    missing = [] # Bills not present in ledger
    buffer = []
    console.print(f"\n[warning]Checking bills:[/]\n")

    for i, bill in enumerate(bills):
        console.print(print_bill(bill, spacing))
        linked = []
        for txn in ledger_data.transactions:
            if f"{bill['tag']}-{month}" in txn.entry.links:
                linked.append(txn)
        bill_txn = next((txn for txn in linked if 'bill' in txn.entry.tags), None)
        payment_txn = next((txn for txn in linked if 'payment' in txn.entry.tags), None)
        if bill_txn is None: missing.append(bill)
        elif bill_txn.entry.flag == '!': unpaid.append(bill)
        elif payment_txn is None: pending.append(bill)

    # Add missing bills
    if len(missing):
        console.print(f"\n[warning]Bills not found for [date]{month}[/][/]:\n")
        for bill in missing:
            console.print(print_bill(bill, spacing))
        missing_prompt = prompt(
            f"\n...Would you like to insert missing bills? [Y/n] > ",
            default='y',
            bottom_toolbar=confirm_toolbar,
            validator=ValidOptions(['y', 'n'])).lower()
        if missing_prompt == 'y':
            for bill in missing:
                console.print(f"\n[answer]Inserting bill \'{bill['tag']}\'[/]\n")
                bill_date = datetime.strptime(f"{month}-{bill['due']}", "%Y-%m-%d").date()
                new_bill = new_bean(
                    date=bill_date,
                    flag='!',
                    payee=bill['payee'],
                    tags=['bill'],
                    links=[f"{bill['tag']}-{bill_date.strftime('%Y-%m')}"],
                    postings=[])
                new_bill.add_posting({"account": bill['account'], "amount": float(bill['amount']), "currency": currency})
                new_bill.add_posting({"account": bill['liability'], "amount": -float(bill['amount']), "currency": currency})
                console.print(f"{new_bill}")
                bill_amount = prompt(
                    f"...Update bill amount? > ",
                    key_bindings=cancel_bindings,
                    bottom_toolbar=cancel_toolbar,
                    validator=valid_float,
                    default=bill['amount'])
                if bill_amount is None:
                    continue
                new_bill.update(postings=[])
                new_bill.add_posting({"account": bill['account'], "amount": float(bill_amount), "currency": currency})
                new_bill.add_posting({"account": bill['liability'], "amount": -float(bill_amount), "currency": currency})
                console.print(f"\n{new_bill}")
                buffer.append(new_bill)
                if output:
                    append_lines(err_console, output, new_bill.print())

            console.print(f"[pos]Bills inserted {'-'*64}[/]\n")
            for bill in buffer:
                console.print(bill)

    # Show unpaid bills
    if len(unpaid):
        console.print("\n[warning]Unpaid bills:[/]\n")
        for bill in unpaid:
            console.print(print_bill(bill, spacing))
    else:
        console.print(f"\n[pos]No unpaid bills found for [date]{month}[/]![/]")

    # Show pending bills
    if len(pending):
        console.print("\n[warning]Pending bills:[/]\n")
        for bill in pending:
            console.print(print_bill(bill, spacing))
    else:
        console.print(f"\n[pos]No pending bills found for [date]{month}[/]![/]")

    raise typer.Exit()
