from collections import  namedtuple, OrderedDict
import datetime as date
import hashlib


Transaction = namedtuple(
    'transaction',
    ['sender',
     'to',
     'amount',
     'signature'])

Block = namedtuple(
    'block',
    ['index',
     'timestamp',
     'proof',
     'previous_hash',
     'hash',
     'transactions'])


def get_hash(unhashed):
    return hashlib.sha256(str(unhashed).encode('utf-8')).hexdigest()


class BlockChain(list):

    def __init__(self):

        genesis_block = OrderedDict(
            {'index': 1,
             'timestamp': date.datetime.now(),
             'proof': 9,
             'previous_hash': 'hello world',
             'transactions': []}
        )

        self.append(
            Block(
                **genesis_block,
                hash=get_hash(genesis_block))
        )

    def update_transactions(self, new):
        return self[-1].transactions + new

    def next_block(self, new_transactions, proof):
        last_block = self[-1]
        next_block = OrderedDict(
            {'index': len(self) + 1,
             'timestamp': date.datetime.now(),
             'proof': proof,
             'previous_hash': last_block.hash,
             'transactions' : self.update_transactions(new_transactions)}
        )

        self.append(
            Block(**next_block, hash=get_hash(get_hash(next_block)))
        )
