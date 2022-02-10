from random import randrange
import math

from lib.classes import Block, BlockChain, Node
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

if __name__ == '__main__':
    nodes = []
    bc = BlockChain()

    for i in range(100):
        x = randrange(100)
        if x <= 15: # Attacker
            n = Node(True)
            if len(nodes) > 1:
                transaction1 = n.wallet.pay(nodes[-1].wallet, 2)
                transaction2 = n.wallet.pay(nodes[-2].wallet, 1) 
                n.wallet.sign(transaction1)
                n.wallet.sign(transaction2)
                b1 = None
                b2 = None 
                if len(bc.chain) > 1:
                    prev_hash = Node.attacker_last_block_hash
                    b = None
                    if prev_hash: # append to the attacker branch
                        if prev_hash == Node.client_last_block_hash:
                            prev_hash = Block.blocks[Node.client_last_block_hash].prev_hash
                        b = Block([transaction1, transaction2], prev_hash)
                    else: # fork the chain
                        prev_hash = Block.blocks[Node.client_last_block_hash].prev_hash
                        if prev_hash:
                            b = Block([transaction1, transaction2], prev_hash)
                        else:
                            continue
                    change_n(b, Block.blocks[prev_hash])
                    bc.add_block(b, True)
                    n.block_added_to_chain(b)
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
                    prev_hash = Node.client_last_block_hash
                    b = Block([transaction1, transaction2], prev_hash)
                    change_n(b, Block.blocks[prev_hash])
                else:
                    b = Block([transaction1, transaction2])
                bc.add_block(b)
                n.block_added_to_chain(b)
            nodes.append(n)

    print(f'The network has {Node.attack_nodes} attacking nodes.')
    print(bc)
