import sys
from collections import defaultdict
import json

# For doc-stats
N = 0
doc_len = defaultdict()
doc_len_global = 0

# for term-stats
terms = defaultdict(set)
stats = defaultdict(dict)


for line in sys.stdin:
    term_1, term_2, term_3 = line.strip().split("\t", 2)

    if term_1 == "!doc": 
        doc, doc_size = term_2, term_3
        N += 1
        doc_len[doc] = doc_size
        doc_len_global += int(doc_size)
        print(f"!doc\t{doc}\t{doc_size}")
    else:
        term, tf, doc = term_1, term_2, term_3
        terms[term].add(doc)
        stats[term][doc] = tf

for term in stats:
    tf_dict = stats[term]
    doc_list = list(terms[term])
    
    print(f"{term}\t{json.dumps(tf_dict)}\t{json.dumps(doc_list)}")


print(f"!stats\tN\t{N}")
print(f"!stats\tavg\t{doc_len_global / N}")
