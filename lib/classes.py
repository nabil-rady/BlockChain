import hashlib
import secrets
import json
from typing import Iterable
from crypto_utils import check_nonce, generate_key_pair, sign_transaction, verify_transaction, hash_block, hash_keys
from datetime import datetime

class Transaction:
    transaction_serial_number = 0
    transactions = {}
    
    def __init__(self, input: str, output: str, amount: float) -> None:
        self.input = input  # Public address of payer
        self.output = output  # Public address of receiver
        self.amount = amount
        self.serial_number = Transaction.transaction_serial_number
        Transaction.transaction_serial_number += 1
        self.hash = self.calc_hash()
        Transaction.transactions[self.hash] = self
        
    def calc_hash(self):
        from crypto_utils import hash_transaction
        self.hash = hash_transaction(self)

    def verify(self) -> bool:
        return verify_transaction(self, self.input)

    def set_signature(self, signature: str):
        self.signature = signature

    def apply(self) -> None:
        if not self.verify():
            raise Exception('Invalid transaction')
        if  not Wallet.wallets[self.input].amount > self.amount:        
            raise Exception('Invalid payment')
        Wallet.wallets[self.output].amount += self.amount
        Wallet.wallets[self.input].amount -= self.amount

    def to_json(self):
        return json.dumps({
            'input': self.input,
            'output': self.output,
            'serial_number': self.transaction_serial_number,
            'signature': self.signature.decode(),
        })


    def __repr__(self) -> str:
        return f'{self.input} sent {self.amount} to {self.input}'

def from_json_to_transaction(data: str) -> Transaction:
    data = json.loads(data)
    return Transaction(data['input'], data['output'], data['amount'], data['signature'])

class Nonce:
    def __init__(self, block):
        while True:
            val = secrets.token_hex(16)
            if check_nonce(block, val):
                self.val = val
                break        
    def __repr__(self):
        return self.val
class Block:
    blocks = {}
    genesis_block = True
    def __init__(self, transactions: Iterable[Transaction], prev_hash: hashlib.sha256 = None):
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.is_genesis_block = Block.genesis_block
        Block.genesis_block = False
        Block.blocks[hash_block(self)] = self
        self.nonce = Nonce(self)
        self.next = None
        self.ts = datetime.now()
    def verify(self) -> bool:
        for transaction in self.transactions:
            if not transaction.verify():
                return False
        if not self.is_genesis_block:
            if not self.prev_hash:
                return False
            prev_block = Block.blocks[self.prev_hash]
            if not prev_block.next is self: ## n3mlo ezay
                return False
        return check_nonce(self, self.nonce.val)

class BlockChain:
    is_forked = False
    last_blocks = []
    def __init__(self) -> None:
        self.chain = []
        self.adj_list = {}
    
    def last_block(self) -> Block:
        return BlockChain.last_blocks

    def add_block(self, block:Block) -> None:
        prev_hash = block.prev_hash
        self.chain.append(block)
        if prev_hash:
            try:
                adj_list = self.adj_list[prev_hash]
                self.adj_list[prev_hash].append(hash_block(block))
                BlockChain.is_forked = True
                BlockChain.last_blocks.append(hash_block(block))
            except KeyError:
                self.adj_list[prev_hash] = []
                self.adj_list[prev_hash].append(hash_block(block))
                BlockChain.last_blocks.remove(prev_hash)
                BlockChain.last_blocks.append(hash_block(block))
        else:
            BlockChain.last_blocks.append(hash_block(block))

    def __repr__(self) -> str:
        return f'This chain has {len(self.chain)} blocks'


class Wallet:
    wallets = {}
    public_keys = {}
    def __init__(self, amount: float):
        self.public_key, self._private_key= generate_key_pair()
        self.amount = amount
        Wallet.wallets[self.public_key] = self
        Wallet.public_keys[hash_keys(self.public_key.save_pkcs1())] = self.public_key

    def sign(self, transaction: Transaction) -> None:
        transaction.signatrue = sign_transaction(transaction, self._private_key)

    def pay(self, output, amount: float):
        t = Transaction(self.public_key, output.public_key, amount)
        self.sign(t)
        return t

    def __repr__(self):
        return f'Public Key: {self.public_key.save_pkcs1()}\nPrivate Key: {self.private_key.save_pkcs1()}\nAmount: {self.amount}'

    # def calc_prev_hash(self, b:Block):
    #     hash_block(b)

class Node:
    nodes = 0
    attack_nodes = 0
    def __init__(self, attacker: bool = False):
        self.wallet = Wallet(10)
        self.attacker = attacker
        Node.nodes += 1
        if attacker:
            Node.attack_nodes += 1
