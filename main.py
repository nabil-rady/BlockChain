from lib.classes import Transaction, Wallet, Block
from crypto_utils import hash_block_with_nonce

if __name__ == '__main__':   
    w1 = Wallet(10.5)
    w2 = Wallet(0)
    t1 = w1.pay(w2, 5)
    t2 = w2.pay(w1, 3)
    t3 = w1.pay(w1, 2)
    t4 = Transaction(w1.public_key, w2.public_key, 0.5)
    b = Block([t1, t2, t3])
    print(hash_block_with_nonce(b, b.nonce.val))    
    print(b.verify())
    print(b.nonce)
    