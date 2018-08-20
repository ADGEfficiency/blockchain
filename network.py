import binascii
from time import sleep

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import numpy as np

from chain import Transaction, BlockChain


class Node(object):

    def __init__(self, address):
        self.address = address

        key = RSA.generate(1024)

        self.private_key = binascii.hexlify(
            key.exportKey(format='DER')).decode('ascii')

        self.public_key = binascii.hexlify(
            key.publickey().exportKey(format='DER')).decode('ascii')

        self.chain = BlockChain()

    def __repr__(self):
        return 'node: {} len: {}'.format(self.address, len(self.chain))

    def make_transaction(self, to, amount):
        trans = {'sender': self.address,
                 'to': to.address,
                 'amount': str(amount)}

        return Transaction(
            **trans,
            signature=self.sign(trans)
        )

    def sign(self, transaction):
        private_key = RSA.importKey(binascii.unhexlify(self.private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(transaction).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')

    def verify(self, transaction):
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(transaction.signature))

    def add_next_block(self, transactions, proof):
        self.chain.next_block(transactions, proof)


class Network(list):
    """ should never have a BlockChain - only nodes have chains """

    def __init__(
            self,
            nodes,
            overdraft_limit
    ):
        list.__init__(self, nodes)
        self.proof = 9
        self.overdraft_limit = overdraft_limit

    def proof_of_work(self):
        self.proof = self.proof + 0.1
        sleep(self.proof)
        return self.proof

    def consensus(self):
        """ find the node that mined the block """
        chains = [node.chain for node in self]
        new_chain = chains[np.argmax([len(chain) for chain in chains])]

        for node in self:
            node.chain = new_chain

    def validate_transactions(self, balances, new_transactions):
        assert self.check_balances(balances)

        validated = []
        for transaction in new_transactions:
            print('processing to:{} sender:{} amount:{}'.format(
                transaction.to, transaction.sender, transaction.amount))

            amount = float(transaction.amount)
            new_bal = balances[transaction.sender] - amount

            if new_bal < self.overdraft_limit:
                print('rejected - {} overdrawn with bal of {}'.format(
                    transaction.sender, new_bal))

            else:
                print('accepted')
                balances[transaction.sender] -= amount
                balances[transaction.to] += amount
                validated.append(transaction)

        assert self.check_balances(balances)

        return balances, validated

    def check_balances(self, balances):
        """ checks that all balances are over the limit """
        for node, balance in balances.items():
            assert balance >= self.overdraft_limit
        return True
