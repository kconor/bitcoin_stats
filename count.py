#!/usr/bin/env python
import psycopg2
from psycopg2.extras import NamedTupleCursor

from Counts import Counts
import decode_script
from Txn import Txn


def run():
    num_hashes = 1000000
    out = open("stats.txt", "w")
    #conn_str = "dbname=abe2 user=yuewang"
    conn_str = "dbname=postgres"
    script_counts = Counts(70)
    with psycopg2.connect(conn_str, cursor_factory=NamedTupleCursor) as conn:
        from Hashes import fetch_hashes
        hashes = fetch_hashes(num_hashes, conn)
        for i,hash in enumerate(hashes):
            abe_txn = Txn(hash, conn)
            script_counts.add('txn_count')
            for txin in abe_txn.tx_in:
                script_counts.add(decode_script.decode_script(txin.script_bytea))
            for txout in abe_txn.tx_out:
                script_counts.add(decode_script.decode_script(txout.script_bytea))
            if i > 0 and i % 10000 == 0:
                out.write(script_counts.mkString())
                out.flush()
    out.write(script_counts.mkString())
    out.close()

if __name__ == '__main__':
    run()
