from collections import defaultdict

import numpy as np

from network import Node, Network


def simulate_transactions(node1, node2, num=3):
    """ simulating nodes using the tokens """
    print('simulating {} transactions'.format(num))
    return [node1.make_transaction(node2, float(np.random.randint(10)))
            for _ in range(num)]


if __name__ == '__main__':
    OVERDRAFT_LIMIT = -10

    net = Network(
        [Node('node'), Node('other')],
        overdraft_limit=OVERDRAFT_LIMIT
    )

    balances = defaultdict(int)
    for _ in range(3):
        #  simulate a few transactions between nodes
        new_transactions = simulate_transactions(net[0], net[1])

        #  check the transactions are valid
        balances, transactions = net.validate_transactions(
            balances, new_transactions)

        new_proof = net.proof_of_work()
        #  randomly select a miner
        miner = net[np.random.randint(len(net))]

        #  miner adds the block to it's chain
        miner.add_next_block(new_transactions, proof=new_proof)

        #  update other nodes in the network
        net.consensus()

        print('balances {}'.format(balances))
        print('')

    print('finished')
