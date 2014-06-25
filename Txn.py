"""
This is modified from 
https://github.com/hackscience/bitrans
"""
from util import fromunsigned
from util import bytestream
from util import fromvarlen
from TxOut import TxOut
from TxIn import TxIn

class Txn(object):
    def __init__(self, hash, curs):
        #named params are really slow...
        txin=True
        txout=False

        self.curs = curs
        self.tx_in = []
        self.tx_out = []
        #get tx_id, version, and lock time from hash
        sql = self.curs.mogrify("SELECT tx_id, tx_version, tx_locktime "\
                           "FROM tx WHERE tx_hash=%s", (hash,))
        self.curs.execute(sql)
        rs = self.curs.fetchall()
        try:
            tx_id = rs[0].tx_id
        except:
            print(sql)
        self.version = int(rs[0].tx_version)
        self.lock_time = int(rs[0].tx_locktime)
        #load tx_in from tx_id and each prev output
        if txin:
            sql = "SELECT txin.tx_id, txin.txin_pos, txin.txin_scriptsig, "\
                  "txin.txin_sequence, txin.txout_id, txout.txout_value, "\
                  "txout.txout_scriptpubkey, tx.tx_hash as prev_hash "\
                  "FROM txin, txout, tx "\
                  "WHERE txin.txout_id=txout.txout_id "\
                        "and txin.tx_id=%s "\
                        "and tx.tx_id=txout.tx_id" % tx_id
            self.curs.execute(sql)
            rs = self.curs.fetchall()
            for tuple in rs:
                self.tx_in.append(TxIn(tuple, self))
        #load the outputs of the tansaction
        if txout:
            sql = "SELECT txout.tx_id, txout.txout_value, txout.txout_scriptpubkey "\
                  "FROM txout "\
                  "WHERE txout.tx_id=%s" % tx_id
            self.curs.execute(sql)
            rs = self.curs.fetchall()
            for tuple in rs:
                self.tx_out.append(TxOut(tuple))

    @property
    def tx_out_count(self):
        return len(self.tx_out)

    @property
    def tx_in_count(self):
        return len(self.tx_in)
