import hashlib
import secrets
from typing import Iterable
from crypto_utils import check_nonce, generate_key_pair, sign_transaction, verify_transaction

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

    def apply(self) -> None:
        if not self.verify():
            raise Exception('Invalid transaction')
        if  not Wallet.wallets[self.input].amount > self.amount:        
            raise Exception('Invalid payment')
        Wallet.wallets[self.output].amount += self.amount
        Wallet.wallets[self.input].amount -= self.amount

    def __repr__(self) -> str:
        return f'{self.input} sent {self.amount} to {self.input}'

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
        self.nonce = Nonce(self)
        self.next = None
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

class Wallet:
    wallets = {}
    def __init__(self, amount: float):
        self.public_key, self._private_key= generate_key_pair()
        self.amount = amount
        Wallet.wallets[self.public_key] = self

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