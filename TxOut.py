"""
This is modified from 
https://github.com/hackscience/bitrans
"""
from util import fromunsigned
from util import fromvarlen


class TxOut(object):
    def __init__(self, tuple):
        self.value = int(tuple.txout_value)
        self.script_bytea = tuple.txout_scriptpubkey
        self.script_length = len(self.script_bytea) / 2
