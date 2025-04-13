import sys
import json
from cassandra.cluster import Cluster


def main():
    cluster = Cluster(["cassandra-server"])
    session = cluster.connect("search_engine")

    update_tf_stmt = session.prepare("""
        UPDATE term_vocab SET tf = tf + ? WHERE term = ? AND doc_id = ?
    """)

    insert_stat_stmt = session.prepare("""
        INSERT INTO global_doc_stats (key, value) VALUES (?, ?)
    """)

    for line in sys.stdin:
        input_terms = line.strip().split("\t", 2)

        if "!doc" in input_terms:
            _, doc, doc_size = input_terms
            session.execute(insert_stat_stmt, (doc, float(doc_size)))

        elif "!stats" in input_terms:
            _, key, stats = input_terms
            session.execute(insert_stat_stmt, (key, float(stats)))

        else:
            term, tf_dict, doc_list = input_terms
            try:
                tf_dict = json.loads(tf_dict)
            except json.JSONDecodeError:
                continue

            for doc_id, tf in tf_dict.items():
                session.execute(update_tf_stmt, (int(tf), term, doc_id))

    session.shutdown()


if __name__ == "__main__":
    main()