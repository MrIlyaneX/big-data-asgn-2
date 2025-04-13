from cassandra.cluster import Cluster

cluster = Cluster(["cassandra-server"])
session = cluster.connect()

session.execute("""
    CREATE KEYSPACE IF NOT EXISTS search_engine
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
""")

session.set_keyspace("search_engine")

session.execute("""
    DROP TABLE IF EXISTS term_vocab;
""")

session.execute("""
    DROP TABLE IF EXISTS global_doc_stats;
""")

session.execute("""
    CREATE TABLE IF NOT EXISTS term_vocab (
        term text,
        doc_id text,
        tf counter,
        PRIMARY KEY (term, doc_id)
    )
""")


session.execute("""
    CREATE TABLE IF NOT EXISTS global_doc_stats (
        key text,
        value float,
        PRIMARY KEY(key)
    )
""")

session.shutdown()