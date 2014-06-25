"""
    bad hash:
    this 1688 outputs in abe, ~38k outputs in rpc
    \\x430596f1a1c84db57fd4e1dc4f7c59bd65cc47822595376b56a34e7459566661

    two of three escrow address:
    3M8XGFBKwkf7miBzpkU3x2DoWwAVrD1mhk
"""


hashes = [
    '\\xfff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4',
    '\\x6632b2656832f20a411b53ac6f7923404193308b6c09e3dd4e5a0f9fac4c33d6',
    '\\x44eaf56722d9ce7120bccb83a355f038baee72486e964f2b4ac57ac8e32cb1b4',
    '\\x6c01458a6460139d1c104e0a454bfcf5fd77a03a74c8448f8a103920692372fb',
    '\\x6a765ebefb7a72a20f929dcd4773835f914d0bd57e0f18a7f400a21d575e38be',
    '\\x5a51fe08099039b5659713ea1525208c018caa3bc223f1fef5dec57f96abf39e',
    '\\x9c48d9d1483504f423550dc64fac8146a47ebeadc7e39927113cf9c1892566f8',
    '\\x2c391c461530773f2268175f1d74a517b21f1d996403e445374b43fcd1bf385f',
    '\\x7cfc9bf4b91f65faa785eb74939349196a97e5f5654a86b0debe1d61af425a71',
    '\\x2c4c4e7b6c7d9f780a32a2ee85a9e9a1e5be818b85b0d98bac397d69cf59142a',
    '\\x820a3b3cc7d4b74b2ce980670720d7c45e571cbeb451dcd11e39d042f2b331d8',
    '\\x9b0c8d25d31626cabdd4e5dd6587fb592d67d0d5fd5a85974a9096ef0a99e717'
]


def fetch_hashes(N, conn, max_tx_id):
    with conn.cursor() as curs:
        if max_tx_id:
            sql = "SELECT tx_id, tx_hash "\
                  "FROM tx "\
                  "WHERE tx_id < %d "\
                  "ORDER BY tx_id DESC "\
                  "LIMIT %d" % (max_tx_id, N)
        else:
            sql = "SELECT tx_id, tx_hash "\
                  "FROM tx "\
                  "ORDER BY tx_id DESC "\
                  "LIMIT %d" % N
        curs.execute(sql)
        rs = curs.fetchall()
        return rs
