import socket
import json
from lib.classes import Transaction, Wallet, from_json_to_transaction
from crypto_utils import sign_transaction, hash_keys
transactions = {}

def receive(s: socket.socket, data: bytes):
    data = data.encode()
    try:
        data = json.loads(data)
        type_of_data = data['type']
        if type_of_data == "Tarnsaction":
            t = from_json_to_transaction(data['transaction'])
            transactions[t.hash] = t
        # Recursion
        data = s.recv(100000000)
        receive(s, data)
        
    except json.JSONDecodeError:
        return data

s = socket.socket()

s.connect(('127.0.0.1', 1234))

w = Wallet(10)

public_key = w.public_key.save_pkcs1()

print(f'Your Public key is: {hash_keys(public_key)}')

while True:
    command = input('Enter Command\n')
    if command == 'add_transaction': 
        out = input('Enter output address\n')
        amount = input('Enter the amount of coins\n')
        t = Transaction(public_key, Wallet.public_keys[out], amount)
        s.sendall(f'add_transaction {t.to_json()}')
    else:
        print('Unknown command')
    data = s.recv(100000000)
    response = receive(s, data)
    print(response)
