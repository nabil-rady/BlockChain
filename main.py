import socket
import time
from threading import Thread
from random import randrange
import math

from lib.classes import Transaction, Wallet, Block, BlockChain, Node
from crypto_utils import hash_block_with_nonce, generate_key_pair, sign_transaction, hash_block
from commands import add_transaction_command
from GLOBAL_CONSTANTS import Constants

def change_n(current_block:Block, prev_block:Block):
    time_difference = (current_block.ts - prev_block.ts).total_seconds()
    x = Constants.n
    if time_difference > 1:
        x /= math.ceil(time_difference)
        x = int(x)
    else:
        x += 1
    c = Constants()
    c.update(x)
    # print(Constants.n)


if __name__ == '__main__':   
    # w1 = Wallet(10.5)
    # w2 = Wallet(0)
    # t1 = w1.pay(w2, 5)
    # t2 = w2.pay(w1, 3)
    # t3 = w1.pay(w1, 2)
    # t4 = Transaction(w1.public_key, w2.public_key, 0.5)
    # b = Block([t1, t2, t3])
    # print(hash_block_with_nonce(b, b.nonce.val))    
    # print(b.verify())
    # print(b.nonce)
    # bc.add_block([t1, t2])
    # bc.add_block([t3, t4])
    # print(bc)
    # t = Thread(target=change_n)
    # t.start()
    nodes = []
    bc = BlockChain()

    for i in range(100):
        x = randrange(100)
        if x <= 25: # Attacker
            n = Node(True)
            if len(nodes) > 1:
                transaction1 = n.wallet.pay(nodes[-1].wallet, 2)
                transaction2 = n.wallet.pay(nodes[-2].wallet, 1) 
                n.wallet.sign(transaction1)
                n.wallet.sign(transaction2)
                b1 = None
                b2 = None 
                if len(bc.chain) > 1:
                    # Make 2 blocks, and fork
                    prev_hash = hash_block(bc.chain[-2])
                    b1 = Block([transaction1], prev_hash)
                    b2 = Block([transaction2], hash_block(b1))
                    bc.add_block(b1)
                    bc.add_block(b2)
                else:
                    continue
            nodes.append(n)
        else: # Normal client
            n = Node()
            if len(nodes) > 1:
                transaction1 = n.wallet.pay(nodes[-1].wallet, 2)
                transaction2 = n.wallet.pay(nodes[-2].wallet, 1) 
                n.wallet.sign(transaction1)
                n.wallet.sign(transaction2)
                b = None 
                if len(bc.chain) > 0:
                    # Manage forks
                    last_blocks = bc.last_block()
                    if len(last_blocks) == 1: # No forks
                        prev_hash = last_blocks[0]
                        b = Block([transaction1, transaction2], prev_hash)
                        change_n(b, Block.blocks[prev_hash])
                    else: # Fork exists
                        branch_len = {}
                        for block_hash in last_blocks: # calc the length of each chain
                            prev_hash = Block.blocks[block_hash].prev_hash
                            prev = 1
                            while prev_hash:
                                prev_hash = Block.blocks[prev_hash].prev_hash
                                prev += 1
                            branch_len[block_hash] = prev
                        longest_chain_last_block_hash = None
                        for l in branch_len:
                            if not longest_chain_last_block_hash:
                                longest_chain_last_block_hash = l
                            elif branch_len[longest_chain_last_block_hash] < branch_len[l]:
                                longest_chain_last_block_hash = l
                            prev_hash = longest_chain_last_block_hash # append to the longest chain
                            b = Block([transaction1, transaction2], prev_hash)
                            change_n(b, Block.blocks[prev_hash])
                else:
                    b = Block([transaction1, transaction2])
                bc.add_block(b)
            nodes.append(n)

    print(bc)
    print(f'{Node.attack_nodes} attacks')
