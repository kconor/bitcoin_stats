#!/usr/bin/env python
import psycopg2
from psycopg2.extras import NamedTupleCursor
import multiprocessing
import binascii
import time

from decode_script import decode_script
from Hashes import fetch_hashes
from Counts import Counts
from Txn import Txn

import sys

if sys.version_info[0] < 3:
    print("please use version 3")
    sys.exit()


def fill_hash_queue(N, queue, max_tx_id, conn=psycopg2.connect("dbname=postgres")):
    rs = fetch_hashes(N, conn, max_tx_id)
    for i,tuple in enumerate(rs):
        #use bytes b/c you can't serialize a memoryview
        queue.put((i,bytes(tuple[1])))
    return tuple[0], i+1  #return smallest tx_id and number pushed


class Worker(multiprocessing.Process):
    def __init__(self, hash_queue, counts_queue, txn_types_queue): 
        multiprocessing.Process.__init__(self)#TODO; super()
        self.hash_queue = hash_queue
        self.counts_queue = counts_queue
        self.txn_types_queue = txn_types_queue
        self.conn = psycopg2.connect("dbname=postgres", cursor_factory=NamedTupleCursor)
        self.counts = Counts(100)
        self.num_processed = 0
        self.txn_types = {}


    def run(self):
        while not self.hash_queue.empty():
            try:
                """
                Blocking without a timeout (default) leads to hanging processes
                because hash_queue.empty() will return false when it's already 
                been emptied.  hash_queue.get() will then block indefinitely.  
                Not blocking throws an exception if an item isn't available 
                immediately, however, this can happen even if the queue has 
                thousands of items in it.  This leads to skew in workloads 
                because workers quit before the queue is empty.
                """
                i,hash = self.hash_queue.get(block=True, timeout=1)
                self.do_task(hash)
                self.hash_queue.task_done()
                self.num_processed += 1
            except:
                #break if queue was empty but hash_queue.empty() returned true
                break 
        self.counts_queue.put(self.counts)
        self.txn_types_queue.put(self.txn_types)
        #print('process {:,} processed {:,} hashes' % (self.pid, self.num_processed))


    def do_task(self, hash):
        with self.conn.cursor() as curs:
            txn = Txn(hash, curs) 
            for txin in txn.tx_in:
                decoded_script_sig = decode_script(txin.script_bytea)
                decoded_script_pubkey = decode_script(txin.tx_out.script_bytea)
                decoded = decoded_script_pubkey + " -> " + decoded_script_sig
                if decoded not in self.txn_types:
                    self.txn_types[decoded] = hash
                self.counts.add(decoded)
            self.counts.add('txn count:') #count transactions


class Job(object):
    def __init__(self, file_name, hashes_per_iter, num_workers=multiprocessing.cpu_count()):
        self.file_name = file_name
        self.hashes_per_iter = hashes_per_iter
        self.num_workers = num_workers
        self.hash_queue = multiprocessing.JoinableQueue()
        self.counts_queue = multiprocessing.Queue()
        self.txn_types_queue = multiprocessing.Queue()


    def execute(self, iterations, max_tx_id=None):
        counts = Counts(100)
        txn_types = {}
        for i in range(iterations):
            start_time = time.time()
            new_max_tx_id, new_counts, new_types = self.iter(max_tx_id)
            counts.combine(new_counts)
            txn_types.update(new_types)
            print('processed {:,} hashes in {:.2f} seconds'.format(
                    self.hashes_per_iter, time.time() - start_time))
            if max_tx_id and (max_tx_id - new_max_tx_id) < self.hashes_per_iter:
                print('processed {:,} hashes, should have been {:,}'.format(
                        max_tx_id - new_max_tx_id, self.hashes_per_iter))
            max_tx_id = new_max_tx_id
            self.write(counts, txn_types)


    def iter(self, max_tx_id=None):
        min_tx_id, num_pushed = fill_hash_queue(self.hashes_per_iter, self.hash_queue, max_tx_id)
        print('starting {:,} workers'.format(self.num_workers))
        workers = [Worker(self.hash_queue, self.counts_queue, self.txn_types_queue) 
                        for i in range(self.num_workers)]
        [w.start() for w in workers]
        [w.join() for w in workers]
        print('  workers joined')
        self.hash_queue.join()#block until task_done() called for each item in queue

        #aggregate results
        counts = self.counts_queue.get()
        while not self.counts_queue.empty():
            counts.combine(self.counts_queue.get())

        types = self.txn_types_queue.get()
        while not self.txn_types_queue.empty():
            types.update(self.txn_types_queue.get())

        return min_tx_id, counts, types


    def write(self, counts, types):
        out = open(self.file_name,'w')
        out.write(counts.mkString)
        for k,v in types.items():#types is a {}
            out.write("%s | %s\n" % (k.rjust(100), binascii.hexlify(v).rjust(60)))
        out.close()


if __name__ == '__main__':
    Job('stats.txt', 100000).execute(100)

