from lib.classes import Transaction
from GLOBAL_CONSTANTS import clients
import json

def broadcast(data: str)->None:
    data = data.encode()
    data = json.dumps({
        'type': 'Transaction',
        'transaction': data
    })
    for client in clients:
        client.send(data)

def add_transaction_command(t_json: str)->None:
    broadcast(t_json)
