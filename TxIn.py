"""
This is modified from 
https://github.com/hackscience/bitrans
"""
from TxOut import TxOut
from util import fromunsigned
from util import bytestream
from util import fromvarlen


class TxIn(object):
    def __init__(self, tuple, txn):
        self.txout_id = tuple.txout_id
        self.index = int(tuple.txin_pos)
        self.script_bytea = tuple.txin_scriptsig
        self.script_length = len(self.script_bytea) / 2
        self.sequence = int(tuple.txin_sequence)
        self.tx_out = TxOut(tuple)

        if not self.txout_id:
            self.is_coinbase = True
        else:
            self.is_coinbase = False

    def prev_out(self):
        return self.tx_out
