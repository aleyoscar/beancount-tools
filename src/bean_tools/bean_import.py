import typer
from .helpers import (
    get_key,
    set_key,
    get_json_values,
    replace_lines,
    cur,
    append_lines,
    dec,
    eval_string_dec,
    eval_string_float,
    get_pending,
    get_matches
)
from .ledger import ledger_load, ledger_bean
from .ofx import ofx_load
from .simplefin import simplefin_load
from .prompts import (
    console,
    err_console,
    style,
    resolve_toolbar,
    cancel_bindings,
    cancel_toolbar,
    confirm_toolbar,
    ValidOptions,
    valid_account,
    edit_toolbar,
    valid_date,
    valid_link_tag,
    is_account,
    postings_toolbar,
    valid_math_float,
    period_callback,
    account_callback,
    flag_callback,
    version_callback
)
from . import __version__
from pathlib import Path
from prompt_toolkit import prompt, HTML
from prompt_toolkit.completion import FuzzyCompleter, WordCompleter
from typing_extensions import Annotated

def get_posting(type, default_amount, default_currency, op_cur, completer, color, default_account=''):
    type = f"<{color}>{type}</{color}>"
    account = prompt(
        HTML(f"...{type} account > "),
        bottom_toolbar=postings_toolbar(cur(default_amount)),
        key_bindings=cancel_bindings,
        validator=valid_account,
        completer=completer,
        default=default_account,
        style=style)
    if not account: return None
    amount = prompt(
        HTML(f"...{type} amount > "),
        bottom_toolbar=postings_toolbar(cur(default_amount)),
        key_bindings=cancel_bindings,
        validator=valid_math_float,
        default=cur(default_amount),
        style=style)
    if not amount: return None
    if not op_cur:
        currency = prompt(
            HTML(f"...{type} currency > "),
            default=default_currency,
            bottom_toolbar=postings_toolbar(cur(default_amount)),
            key_bindings=cancel_bindings,
            style=style)
    else:
        currency = default_currency
    if not currency: return None
    return {"account": account, "amount": amount, "currency": currency}

def bean_import(
    ledger: Annotated[Path, typer.Argument(
        help="The beancount ledger file to base the parser from",
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True)],
    ofx: Annotated[Path, typer.Option(
        "--ofx", "-x",
        help="The ofx file to parse",
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True)]=None,
    simplefin: Annotated[Path, typer.Option(
        "--simplefin", "-s",
        help="The simplefin file to parse",
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True)]=None,
    output: Annotated[Path, typer.Option(
        "--output", "-o",
        help="The output file to write to instead of stdout",
        show_default=False, exists=False)]=None,
    period: Annotated[str, typer.Option(
        "--period", "-d",
        help="Specify a year, month or day period to parse transactions from in the format YYYY, YYYY-MM or YYYY-MM-DD",
        callback=period_callback)]="",
    account: Annotated[str, typer.Option(
        "--account", "-a",
        help="Specify the account transactions belong to",
        callback=account_callback)]="",
    payees: Annotated[Path, typer.Option(
        "--payees", "-p",
        help="The payee file to use for name substitutions",
        exists=False)]="payees.json",
    operating_currency: Annotated[bool, typer.Option(
        "--operating-currency", "-c",
        help="Skip the currency prompt when inserting and use the ledger's operating_currency")]=False,
    flag: Annotated[str, typer.Option(
        "--flag", "-f",
        help="Specify the default flag to set for transactions",
        callback=flag_callback)]="*",
    version: Annotated[bool, typer.Option(
        "--version", "-v",
        help="Show version info and exit",
        callback=version_callback, is_eager=True)]=False,
):
    """
    Parse transactions for review and editing for a beancount LEDGER and output transaction entries to stdout
    """

    console_output = f"LEDGER File: [file]{ledger}[/]\nPAYEES File: [file]{payees}[/]"
    buffer = ''

    if ofx: console_output += f"\nOFX File: [file]{ofx}[/]"
    if simplefin: console_output += f"\nSimpleFIN File: [file]{simplefin}[/]"
    if output: console_output +=  f"\nOUTPUT File: [file]{output}[/]"
    console.print(f"{console_output}")

    txn_data = None

    # Parse file into txn_data
    if ofx:
        txn_data = ofx_load(ofx)
    if simplefin:
        txn_data = simplefin_load(simplefin)

    if txn_data and len(txn_data.transactions):
        console.print(f"Parsed [number]{len(txn_data.transactions)}[/] transactions")
    else:
        err_console.print(f"[error]No transactions found. Please provide a valid file to parse.[/]")
        raise typer.Exit()

    # Parse ledger file into ledger_data
    ledger_data = ledger_load(ledger)
    if ledger_data and len(ledger_data.transactions):
        console.print(f"Parsed [number]{len(ledger_data.transactions)}[/] beans from LEDGER file")
        console.print(f"Default currency: [answer]{ledger_data.currency}[/]")
    else:
        err_console.print(f"[error]No transaction entries found in LEDGER file. Exiting.[/]")
        raise typer.Exit()
    account_completer = FuzzyCompleter(WordCompleter(ledger_data.accounts, sentence=True))
    tags_completer = FuzzyCompleter(WordCompleter(ledger_data.tags))
    links_completer = FuzzyCompleter(WordCompleter(ledger_data.links))

    # Filter transactions by dates specified from cli
    if period:
        filtered = [t for t in txn_data.transactions if t.date.startswith(period)]
        if len(filtered):
            console.print(f"Found [number]{len(filtered)}[/] transactions within period [date]{period}[/]")
        else:
            err_console.print(f"[error]No transactions found within the specified period [date]{period}[/]. Exiting.[/]")
            raise typer.Exit()
    else:
        filtered = txn_data.transactions

    # Check if account specified, else prompt
    if not account:
        account = prompt(
            f"Beancount account transactions belong to > ",
            validator=valid_account,
            completer=account_completer)
    console.print(f"Transaction account: [answer]{account}[/]")

    # Match transactions not in beans into pending
    pending = []
    pending = get_pending(filtered, ledger_data.transactions, account)
    if len(pending):
        console.print(f"Found [number]{len(pending)}[/] transactions not in LEDGER")
    else:
        console.print(f"[warning]No pending transactions found. Exiting.[/]")

    # Parse each pending transaction
    reconcile_count = 0
    insert_count = 0
    pending = sorted(pending, key=lambda x: x.date)
    for txn_count, txn in enumerate(pending):
        console.print(f"Parsing {txn_count+1}/{len(pending)}: {txn.print(theme=True)}")

        # Update ledger data for every transaction
        ledger_data = ledger_load(ledger)
        account_completer = FuzzyCompleter(WordCompleter(ledger_data.accounts, sentence=True))
        tags_completer = FuzzyCompleter(WordCompleter(ledger_data.tags))
        links_completer = FuzzyCompleter(WordCompleter(ledger_data.links))

        # Reconcile, Insert, Skip?
        resolve = prompt(
            f"...Reconcile, Insert or Skip? > ",
            bottom_toolbar=resolve_toolbar,
            validator=ValidOptions(['r', 'reconcile', 'i', 'insert', 's', 'skip', 'q', 'quit'])).lower()

        # Reconcile
        if resolve[0] == "r":
            console.print(f"...Reconciling")
            reconcile_matches = []
            reconcile_matches = get_matches(txn, ledger_data.transactions, account)

            # Matches found
            matches_canceled = False
            if len(reconcile_matches):
                console.print(f"...Found matches:\n")
                for i, match in enumerate(reconcile_matches):
                    post_match = None
                    for post in match.entry.postings:
                        if post.account == account:
                            post_match = post
                            break
                    console.print(f"   [{i}] {match.print_head(theme=True)}")
                    console.print(f"          {post_match.account} {post_match.units.number}")
                if len(reconcile_matches) == 1:
                    match_range = '[0]'
                else:
                    match_range = f'[0-{len(reconcile_matches) - 1}]'
                reconcile_match = prompt(
                    f"\n...Select match {match_range} > ",
                    bottom_toolbar=cancel_toolbar,
                    key_bindings=cancel_bindings,
                    validator=ValidOptions([str(n) for n in range(len(reconcile_matches))]),
                    default="0")
                if reconcile_match:
                    bean_reconcile = reconcile_matches[int(reconcile_match)]
                    bean_linecount = len(bean_reconcile.print().strip().split('\n'))
                    console.print(f"...Reconciling {bean_reconcile.print_head(theme=True)}\n")
                    for post in bean_reconcile.entry.postings:
                        if post.account == account:
                            post.meta.update({'rec': txn.id})
                            break
                    bean_reconcile.replace()
                    console.print(bean_reconcile.print())
                    reconcile_count += 1
                else: matches_canceled = True
            else: matches_canceled = True
            # No matches found
            if matches_canceled:
                reconcile_insert = prompt(
                    f"...No matching transactions found. Would you like to insert instead? [Y/n] > ",
                    default='y',
                    bottom_toolbar=confirm_toolbar,
                    validator=ValidOptions(['y', 'n'])).lower()
                if reconcile_insert == 'y': resolve = 'i'
                else: resolve = 's'

        # Insert
        if resolve[0] == "i":
            console.print(f"...Inserting")

            # Replace payee
            payees_set = sorted(set(get_json_values(payees)).union(ledger_data.payees))
            payee_completer = FuzzyCompleter(WordCompleter(payees_set, sentence=True))
            payee = get_key(payees, txn.payee)

            # Payee not found, replace
            if not payee:
                payee = prompt(
                    f"...Replace '{txn.payee}'? > ",
                    key_bindings=cancel_bindings,
                    bottom_toolbar=cancel_toolbar,
                    completer=payee_completer)

            # Payee entered
            if payee:
                console.print(f"...Replaced [string]{txn.payee}[/] with [answer]{payee}[/]")
                set_key(payees, txn.payee, payee)
                txn.payee = payee

            # Update total transaction amount
            new_amount = txn.abs_amount
            new_amount = prompt(
                f"...Update total amount? > ",
                key_bindings=cancel_bindings,
                bottom_toolbar=cancel_toolbar,
                validator=valid_math_float,
                default=cur(new_amount)
            )
            if new_amount:
                new_amount = eval_string_float(new_amount)

            # Add credit postings until total is equal to transaction amount
            new_bean = ledger_bean(txn, txn_data.account_id, flag)
            new_posting = None
            while new_bean.amount < new_amount:
                console.print(f"\n{new_bean.print()}")
                new_posting = get_posting("Credit", new_amount - new_bean.amount, ledger_data.currency, operating_currency, account_completer, "pos")
                if new_posting is not None:
                    new_posting['amount'] = eval_string_dec(new_posting['amount'])
                    new_bean.add_posting(new_posting)
                else:
                    break

            # Add debit posting
            if new_posting is not None:
                console.print(f"\n{new_bean.print()}")
                new_posting = get_posting("Debit", new_amount * -1, ledger_data.currency, operating_currency, account_completer, "neg", default_account=account)
                if new_posting is not None:
                    new_posting['amount'] = eval_string_dec(new_posting['amount'])
                    new_bean.add_posting(new_posting)

            # Edit final
            edit_cancelled = False
            while True:
                console.print(f"\n{new_bean.print()}")
                edit_option = prompt(
                    f"...Edit transaction? > ",
                    validator=ValidOptions(['d', 'date', 'f', 'flag', 'p', 'payee', 'n', 'narration', 't', 'tags', 'l', 'links', 'o', 'postings', 's', 'save']),
                    bottom_toolbar=edit_toolbar,
                    key_bindings=cancel_bindings)

                if edit_option is None:
                    edit_cancelled = True
                    break

                # Edit date
                if edit_option[0] == 'd':
                    edit_date = prompt(
                        f"...Enter a new date (YYYY-MM-DD) > ",
                        validator=valid_date,
                        key_bindings=cancel_bindings,
                        bottom_toolbar=cancel_toolbar)
                    if edit_date:
                        new_bean.update(date=edit_date)
                    continue

                # Edit flag
                if edit_option[0] == 'f':
                    edit_flag = prompt(
                        f"...Enter a new flag [!/*] > ",
                        validator=ValidOptions(['*', '!']),
                        key_bindings=cancel_bindings,
                        bottom_toolbar=cancel_toolbar)
                    if edit_flag:
                        new_bean.update(flag=edit_flag)
                    continue

                # Edit payee
                if edit_option[0] == 'p':
                    edit_payee = prompt(
                        f"...Enter new payee > ",
                        key_bindings=cancel_bindings,
                        bottom_toolbar=cancel_toolbar,
                        completer=payee_completer)
                    if edit_payee:
                        new_bean.update(payee=edit_payee)
                    continue

                # Edit narration
                if edit_option[0] == 'n':
                    edit_narration = prompt(
                        f"...Enter new narration > ",
                        key_bindings=cancel_bindings,
                        bottom_toolbar=cancel_toolbar)
                    if edit_narration:
                        new_bean.update(narration=edit_narration)
                    continue

                # Edit tags
                if edit_option[0] == 't':
                    edit_tags = prompt(
                        f"...Enter a list of tags separated by spaces > ",
                        key_bindings=cancel_bindings,
                        bottom_toolbar=cancel_toolbar,
                        validator=valid_link_tag,
                        completer=tags_completer,
                        default=" ".join(new_bean.entry.tags))
                    if edit_tags:
                        new_bean.update(tags=set(edit_tags.split()))
                    continue

                # Edit links
                if edit_option[0] == 'l':
                    edit_links = prompt(
                        f"...Enter a list of links separated by spaces > ",
                        key_bindings=cancel_bindings,
                        bottom_toolbar=cancel_toolbar,
                        validator=valid_link_tag,
                        completer=links_completer,
                        default=" ".join(new_bean.entry.links))
                    if edit_links:
                        new_bean.update(links=set(edit_links.split()))
                    continue

                # Edit postings
                if edit_option[0] == 'o':
                    new_bean.update(postings=[])
                    # Update total transaction amount
                    new_amount = prompt(
                        f"...Update total amount? > ",
                        key_bindings=cancel_bindings,
                        bottom_toolbar=cancel_toolbar,
                        validator=valid_math_float,
                        default=cur(new_amount)
                    )
                    if new_amount:
                        new_amount = eval_string_float(new_amount)
                    while new_bean.amount < new_amount:
                        console.print(f"\n{new_bean.print()}")
                        new_posting = get_posting("Credit", new_amount - new_bean.amount, ledger_data.currency, operating_currency, account_completer, "pos")
                        if new_posting is not None:
                            new_posting['amount'] = eval_string_dec(new_posting['amount'])
                            new_bean.add_posting(new_posting)
                    console.print(f"\n{new_bean.print()}")
                    new_posting = get_posting("Debit", new_amount * -1, ledger_data.currency, operating_currency, account_completer, "neg", default_account=account)
                    if new_posting is not None:
                        new_posting['amount'] = eval_string_dec(new_posting['amount'])
                        new_bean.add_posting(new_posting)
                    continue

                # Save and finish
                if edit_option[0] == 's' or edit_option == '':
                    console.print(f"...Finished editing")
                    break

            # Post entry to output (if stdout, save to string)
            if not edit_cancelled:

                # Add rec meta to account
                found_account = False
                for post in new_bean.entry.postings:
                    if post.account == account:
                        found_account = True
                        post.meta.update({'rec': txn.id})
                        break
                if not found_account:
                    no_account_found = prompt(
                        HTML(f"...Transaction account <pos>{account}</pos> not found, continue anyways? [Y/n] > "),
                        default='y',
                        bottom_toolbar=confirm_toolbar,
                        validator=ValidOptions(['y', 'n']),
                        style=style).lower()
                    if no_account_found == 'n':
                        console.print(f"...Skipping")
                        found_account = False
                    else:
                        found_account = True

                if found_account:
                    if output:
                        console_insert = f'[file]{output}[/]'
                        append_lines(output, new_bean.print())
                    else:
                        console_insert = f'[file]buffer[/]'
                        buffer += f"\n{new_bean.print()}"
                    console.print(f"...Inserted {new_bean.print_head(theme=True)} into {console_insert}")
                    console.print(f"\n{new_bean.print()}")
                    insert_count += 1

        # Skip transaction
        if resolve[0] == "s":
            console.print(f"...Skipping")

        # Quit
        if resolve[0] == "q":
            break

    # Finished parsing
    if not output and buffer:
        console.print(f"{buffer}")
    if reconcile_count:
        console.print(f"[string]Reconciled [number]{reconcile_count}[/] transactions[/]")
    if insert_count:
        console.print(f"[string]Inserted [number]{insert_count}[/] transactions[/]")
    skipped = len(pending) - reconcile_count - insert_count
    if skipped:
        console.print(f"[string]Skipped [number]{skipped}[/] transactions[/]")
    console.print(f"[warning]Finished parsing. Exiting[/]")
