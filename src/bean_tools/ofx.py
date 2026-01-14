from .helpers import cur, dec, Transaction
from ofxparse import OfxParser
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

class Account:
    def __init__(self, data):
        self.account_id = data.account.account_id
        self.account_type = data.account.account_type
        self.institution = data.account.institution.organization if data.account.institution else 'Unknown'
        self.transactions = [Transaction(id=t.id, date=t.date, payee=t.payee, amount=t.amount) for t in data.account.statement.transactions]

def ofx_load(console, ofx_path):
    try:
        # Open and parse the OFX file
        with open(ofx_path, 'r') as file:
            ofx = OfxParser.parse(file)

        return Account(ofx)

    except FileNotFoundError:
        console.print(f"[error]Error: File {ofx_path} not found.[/]")
        return None
    except Exception as e:
        console.print(f"[error]Error parsing OFX file: {str(e)}[/]")
        return None
