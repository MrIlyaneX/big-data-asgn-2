import sys
from collections import defaultdict
import json


def main():
    # For doc-stats
    N = 0
    doc_len = defaultdict()
    doc_len_global = 0

    # for term-stats
    terms = defaultdict(set)
    stats = defaultdict(dict)

    for line in sys.stdin:
        term_type, term_2, term_3, term_4 = line.strip().split("\t", 3)

        if term_type == "!doc":
            doc, doc_size, doc_name = term_2, term_3, term_4
            N += 1
            doc_len[doc] = doc_size
            doc_len_global += int(doc_size)
            print(f"!doc\t{doc}\t{doc_size}\t{doc_name}")
        else:
            term, tf, doc = term_2, term_3, term_4
            terms[term].add(doc)
            stats[term][doc] = tf

    for term in stats:
        tf_dict = stats[term]
        doc_list = list(terms[term])

        print(f"!term\t{term}\t{json.dumps(tf_dict)}\t{json.dumps(doc_list)}")

    print(f"!stats\tN\t{N}\tend")
    print(f"!stats\tavg\t{doc_len_global / N}\tend")


if __name__ == "__main__":
    main()
