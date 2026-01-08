import requests, os, sys, base64, binascii, datetime, json, typer
from .helpers import Transaction, get_json
from .prompts import cancel_toolbar, cancel_bindings, ValidOptions
from dotenv import dotenv_values
from prompt_toolkit import prompt, HTML
from datetime import datetime

class Account:
    def __init__(self, data):
        self.account_id = data['id']
        self.account_type = data['name']
        self.institution = data['org']['name'] if data['org']['name'] else 'Unknown'
        self.transactions = [Transaction(
            id=t['id'],
            date=datetime.fromtimestamp(t['posted']),
            payee=t['payee'],
            amount=t['amount']
        ) for t in data['transactions']]

def simplefin_load(console, simplefin_path):
    data = get_json(simplefin_path)
    if 'accounts' in data and len(data['accounts']):
        console.print(f"...SimpleFIN accounts available:")
        for i, acct in enumerate(data['accounts']):
            console.print(f"   [{i}] {acct['org']['name']} - {acct['name']}")
        account_choice = prompt(
            f"\n...Select account to parse > ",
            bottom_toolbar = cancel_toolbar,
            key_bindings = cancel_bindings,
            validator=ValidOptions([str(n) for n in range(len(data['accounts']))]),
            default="0"
        )
        if account_choice and data['accounts'][int(account_choice)]:
            return Account(data['accounts'][int(account_choice)])
    return None
