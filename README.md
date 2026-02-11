# bean-tools

> v2.1.0

A set of Beancount CLI tools

- [import](#import)
- [download](#download)
- [bills](#bills)

```
Usage: bean-tools [OPTIONS] COMMAND [ARGS]...

╭─ Commands ──────────────────────────────────────────────────────────────────╮
│ import     Parse transactions for review and editing for a beancount LEDGER │
│            and output transaction entries to stdout                         │
│ download   Download transactions from an aggregator. Currently supported    │
│            aggregators are: SimpleFIN                                       │
│ version    Show version info and exit                                       │
│ bills      Review and keep track of bill payments in a beancount ledger     │
╰─────────────────────────────────────────────────────────────────────────────╯
```

## import

```
Usage: bean-tools import [OPTIONS] LEDGER

Parse transactions for review and editing for a beancount LEDGER and output
transaction entries to stdout

╭─ Arguments ─────────────────────────────────────────────────────────────────╮
│ *    ledger      FILE  The beancount ledger file to base the parser from    │
│                        [default: None]                                      │
│                        [required]                                           │
╰─────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────╮
│ --ofx                 -x      FILE  The ofx file to parse [default: None]   │
│ --simplefin           -s      FILE  The simplefin file to parse             │
│                                     [default: None]                         │
│ --output              -o      PATH  The output file to write to instead of  │
│                                     stdout                                  │
│ --period              -d      TEXT  Specify a year, month or day period to  │
│                                     parse transactions from in the format   │
│                                     YYYY, YYYY-MM or YYYY-MM-DD             │
│ --account             -a      TEXT  Specify the account transactions belong │
│                                     to                                      │
│ --payees              -p      PATH  The payee file to use for name          │
│                                     substitutions                           │
│                                     [default: payees.json]                  │
│ --operating-currency  -c            Skip the currency prompt when inserting │
│                                     and use the ledger's operating_currency │
│ --flag                -f      TEXT  Specify the default flag to set for     │
│                                     transactions                            │
│                                     [default: *]                            │
│ --version             -v            Show version info and exit              │
│ --help                              Show this message and exit.             │
╰─────────────────────────────────────────────────────────────────────────────╯
```

## download

```
Usage: bean-tools download [OPTIONS] [AGGREGATOR]

Download transactions from an aggregator. Currently supported aggregators
are: SimpleFIN

╭─ Arguments ─────────────────────────────────────────────────────────────────╮
│   aggregator      [AGGREGATOR]  Specify the aggregator to use               │
│                                 [default: simplefin]                        │
╰─────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────╮
│ --output      -o      PATH  The output file to use for the downloaded       │
│                             transactions                                    │
│                             [default: data.json]                            │
│ --start-date  -s      TEXT  Retreive transactions on or after this date in  │
│                             the format YYYY-MM-DD                           │
│ --end-date    -e      TEXT  Retreive transactions before (but not           │
│                             including) this date in the format YYYY-MM-DD   │
│ --pending     -p            Include pending transactions                    │
│ --version     -v            Show version info and exit                      │
│ --help                      Show this message and exit.                     │
╰─────────────────────────────────────────────────────────────────────────────╯
```

## bills

```
Usage: bean-tools bills [OPTIONS] LEDGER

Review and keep track of bill payments in a beancount ledger

╭─ Arguments ─────────────────────────────────────────────────────────────────╮
│ *    ledger      FILE  The beancount ledger file to parse [default: None]   │
│                        [required]                                           │
╰─────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────╮
│ --output              -o      PATH  The output file to write to instead of  │
│                                     stdout                                  │
│ --list                -l            List the current bills in the config    │
│ --month               -m      TEXT  Specify the billing month in the format │
│                                     YYYY-MM                                 │
│                                     [default: 2026-02]                      │
│ --version             -v            Show version info and exit              │
│ --config              -C      PATH  Specify the configuration file to use   │
│                                     [default: bills.json]                   │
│ --edit                -e            Edit config file by                     │
│                                     adding/editing/removing bill entries    │
│ --operating-currency  -c            Skip the currency prompt when inserting │
│                                     and use the ledger's operating_currency │
│ --default-currency    -d      TEXT  Use the specified currency when         │
│                                     inserting transactions                  │
│                                     [default: USD]                          │
│ --set-bill            -b      TEXT  Set a specific bill                     │
│ --pay-bill            -p      TEXT  Pay a specific bill                     │
│ --help                              Show this message and exit.             │
╰─────────────────────────────────────────────────────────────────────────────╯
```

## Notes

gen-chglog command:

```
python gen-chglog.py {version} -r README.md -r src/bean_tools/__init__.py -r pyproject.toml
# Undo commit and build to include with commit
poetry build
```
