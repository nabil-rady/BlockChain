import hashlib
import rsa
from GLOBAL_CONSTANTS import Constants

def generate_key_pair():
    return rsa.newkeys(512) 

def hash_transaction(t):
    h = hashlib.sha256()
    h.update(t.input.save_pkcs1())
    h.update(t.output.save_pkcs1())
    h.update(str(t.amount).encode())
    return h.hexdigest()

def number_of_zero_bits(hash: str)->int:
    i: int = 0
    zero: int = 0
    while i < len(hash): # 7 => 0111
        if hash[i] == '0':
            zero += 4 
        elif int(hash[i], 16) == 1:
            zero += 3
            break
        elif int(hash[i], 16) < 4 and int(hash[i], 16) >= 2:
            zero += 2
            break
        elif int(hash[i], 16) < 8 and int(hash[i], 16) >= 4:
            zero += 1
            break
        else:
            break
        i += 1
    return zero

def hash_block(b):
    h = hashlib.sha256()
    if b.prev_hash:
        h.update(b.prev_hash.encode())
    for t in b.transactions:
        h.update(t.input.save_pkcs1())
        h.update(t.output.save_pkcs1())
        h.update(str(t.amount).encode())
    return h.hexdigest()

def hash_block_with_nonce(b, nonce: str):
    h = hashlib.sha256()
    if b.prev_hash:
        h.update(b.prev_hash)
    for t in b.transactions:
        h.update(t.input.save_pkcs1())
        h.update(t.output.save_pkcs1())
        h.update(str(t.amount).encode())
    h.update(nonce.encode())
    return h.hexdigest()

def check_nonce(b, nonce: str) -> bool:
    h = hashlib.sha256()
    if b.prev_hash:
        h.update(b.prev_hash.encode())
    for t in b.transactions:
        h.update(t.input.save_pkcs1())
        h.update(t.output.save_pkcs1())
        h.update(str(t.amount).encode())
    h.update(nonce.encode())
    # print(Constants.n)
    return number_of_zero_bits(h.hexdigest()) == Constants.n

def hash256(x: str) -> str:
    h = hashlib.sha256()
    h.update(x.encode())
    return h.hexdigest()

def hash_keys(x: str) -> str:
    h = hashlib.sha256()
    h.update(x)
    return h.hexdigest()

def sign_transaction(transaction, private_key: rsa.PrivateKey):
    return rsa.sign(f'{transaction.serial_number} I paid {transaction.amount} coins'.encode(), private_key, 'SHA-256')

def verify_transaction(transaction, public_key: rsa.PublicKey) -> bool:
    try:
        rsa.verify(f'{transaction.serial_number} I paid {transaction.amount} coins'.encode(), transaction.signatrue, public_key)
        return True
    except rsa.VerificationError:
        return False
    except AttributeError:
        return False
        