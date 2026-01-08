import json, os, re
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

class Transaction:
    def __init__(self, id="", date=datetime.today(), payee="", amount=0.0):
        self.id = id
        self.date = date.strftime('%Y-%m-%d')
        self.payee = payee

        self.amount = float(amount)
        self.abs_amount = abs(self.amount)
        self.year = int(self.date.split('-')[0])

    def __str__(self):
        return f'{self.date} {self.payee} {cur(self.amount)}'

    def print(self, theme=False):
        if theme: return f'[date]{self.date}[/] [string]{self.payee}[/] [number]{cur(self.amount)}[/]'
        else: return self.__str__

def cur(num): return '{:.2f}'.format(float(num))

def dec(num, dec='0.01'): return Decimal(num).quantize(Decimal(dec), rounding=ROUND_HALF_UP)

def get_timestamp(str):
    return int((datetime.strptime(str, "%Y-%m-%d") - datetime(1970, 1, 1)).total_seconds())

def get_key(json_path, key):
    data = get_json(json_path)
    if key in data: return data[key]
    else: return None

def set_key(json_path, key, value):
    data = get_json(json_path)
    data[key] = value
    set_json(data, json_path)

def set_json(data, json_path):
    with open(json_path, 'w', encoding='utf-8', newline='\n') as file:
        json.dump(data, file, indent=4, sort_keys=True, ensure_ascii=False)

def get_json(json_path):
    data = {}
    if not os.path.exists(json_path):
        set_json(data, json_path)
    with open(json_path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            # If file is empty or invalid, initialize with empty dict
            set_json(data, json_path)
    return data

def get_json_values(json_path):
    return list(get_json(json_path).values())

def replace_lines(console, file_path, new_data, line_start, line_count=1):
    new_data_arr = [l + '\n' for l in new_data.split('\n')]
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        new_lines = lines[:line_start - 1] + new_data_arr + lines[line_start + line_count - 1:]
        with open(file_path, 'w', encoding='utf-8', newline='\n') as file:
            file.writelines(new_lines)
        return True
    except Exception as e:
        console.print(f"[error]<<ERROR>> Error replacing lines: {str(e)}[/]")
        return False

def append_lines(console, file_path, new_data):
    try:
        with open(file_path, 'a', encoding='utf-8', newline='\n') as file:
            file.write(f"\n{new_data}")
        return True
    except Exception as e:
        console.print(f"[error]<<ERROR>> Error inserting lines: {str(e)}[/]")
        return False

def del_spaces(text):
    return re.sub(' +', ' ', text)

def set_from_sets(arr):
    return sorted(set().union(*arr))

def eval_string_dec(console, text):
    try:
        result = eval(text, {"__builtins__": {}}, {})
        return dec(result)
    except ZeroDivisionError:
        console.print(f"[error]Division by zero is not allowed[/]")
    except Exception as e:
        console.print(f"[error]<<ERROR> Error evaluating expression: {str(e)}[/]")

def eval_string_float(console, text):
    try:
        return float(eval_string_dec(console, text))
    except Exception as e:
        console.print(f"[error]<<ERROR> Error converting expression to float: {str(e)}[/]")

def get_pending(txns, beans, acct):
    pending = []
    for txn in txns:
        found = False
        for bean in beans:
            for post in bean.entry.postings:
                if 'rec' in post.meta and post.meta['rec'] == txn.id:
                    found = True
                    break
        if not found:
            pending.append(txn)
    return pending

def get_matches(txn, beans, acct):
    matches = []
    for bean in beans:
        for post in bean.entry.postings:
            if post.account == acct and 'rec' not in post.meta and abs(post.units.number) == dec(txn.abs_amount):
                matches.append(bean)
    return matches
