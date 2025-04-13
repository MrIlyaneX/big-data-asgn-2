import sys
import re
from collections import Counter


def main():
    for line in sys.stdin:
        # for some reason 5 lines of 'input text words' raise java values errors
        try:
            doc_id, file_name, file_content = line.split("\t", 2)
            doc_id, file_name, file_content = (
                doc_id.strip(),
                file_name.strip(),
                file_content.strip(),
            )
        except ValueError as e:
            pass 

        terms = re.findall(r"\w+", file_content.lower())
        tf = Counter(terms)

        print(f"!doc\t{doc_id}\t{len(terms)}")
        for term in tf:
            print(f"{term}\t{tf[term]}\t{doc_id}")

if __name__ == "__main__":
    main()