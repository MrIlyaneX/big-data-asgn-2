import math
import re
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, countDistinct


def calculate_bm25_score(
    num_docs: int, df: int, tf: int, doc_len: int, avg_doc_len: float, k1: float = 1, b: float = 0.75
) -> float:
    """
    Calculating the bm25 score

    Args:
        num_docs (int): Number of documents
        df (int): Document frequency of term from user query
        tf (int): Term frequency of term from user query
        doc_len (int): Document length
        avg_doc_len (float): Average document length for corpus
        k1 (float, optional): Parameter of BM25. Defaults to 1.
        b (float, optional): Parameter of BM25. Defaults to 0.75.

    Returns:
        float: Score of BM25
    """
    return math.log((num_docs - df + 0.5) / (df + 0.5) + 1) * (
        (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_len / avg_doc_len)))
    )


def compute_doc_scores_bm25(term_vocab_rdd, df_dict, doc_lengths, num_docs, avg_doc_len):
    """
    Compute document scores based on BM25

    Args:
        term_vocab_rdd: RDD of term vocabulary rows
        df_dict: {term: document frequency}
        doc_lengths: {doc_id: doc_len}
        num_docs: total number of documents
        avg_doc_len: average document length

    Returns:
        RDD of (doc_id, score)
    """
    b_df = term_vocab_rdd.context.broadcast(df_dict)
    b_dl = term_vocab_rdd.context.broadcast(doc_lengths)
    b_N = term_vocab_rdd.context.broadcast(num_docs)
    b_avgdl = term_vocab_rdd.context.broadcast(avg_doc_len)

    return term_vocab_rdd.map(
        lambda row: (
            row.doc_id,
            calculate_bm25_score(
                num_docs=b_N.value,
                df=b_df.value.get(row.term, 0),
                tf=row.tf,
                doc_len=b_dl.value.get(row.doc_id, 0),
                avg_doc_len=b_avgdl.value,
            ),
        )
    ).reduceByKey(lambda a, b: a + b)


def main() -> None:
    """
    Main function for performing ranking & retrieval of documents for user's query
    """
    query = re.findall(r"\w+", " ".join(sys.argv[1:]).lower())
    query_set = set(query)
    terms = list(query_set)
    print(f"Processed query terms: {query}")

    # Loading all stuff
    spark = SparkSession.builder.appName("Ranker").master("local").getOrCreate()

    # get only the data with needed terms - great optimization and cassandra partitions utilizations
    term_vocab_df = (
        spark.read.format("org.apache.spark.sql.cassandra")
        .options(table="term_vocab", keyspace="search_engine")
        .load()
        .filter(col("term").isin(terms))
    ).cache()

    if term_vocab_df.rdd.isEmpty():
        print("No matching terms found in the corpus")
        spark.stop()
        return

    # loading doc - doc_name - doc_len + global-stats for bm25
    global_stats_df = (
        spark.read.format("org.apache.spark.sql.cassandra")
        .options(table="global_doc_stats", keyspace="search_engine")
        .load()
    )

    # extract global stats
    global_stats = (
        global_stats_df.filter(col("category") == "meta").rdd.map(lambda row: (row["key"], row["value"])).collectAsMap()
    )
    N = int(global_stats.get("N", 1))
    avg_doc_len = float(global_stats.get("avgdl", 1.0))

    df_dict = (
        term_vocab_df.groupBy("term")
        .agg(countDistinct("doc_id").alias("df"))
        .rdd.map(lambda row: (row.term, row.df))
        .collectAsMap()
    )

    if not df_dict:
        print("No matching terms found in the corpus")
        spark.stop()
        return

    # Calculate document lengths for relevant ones
    doc_lengths = (
        global_stats_df.filter(col("category") == "doc").rdd.map(lambda row: (row["key"], row["value"])).collectAsMap()
    )

    # Broadcast & computation
    term_vocab_rdd = term_vocab_df.rdd
    doc_scores = compute_doc_scores_bm25(term_vocab_rdd, df_dict, doc_lengths, N, avg_doc_len)

    doc_info = (
        global_stats_df.filter(col("category") == "doc")
        .rdd.map(lambda row: (row["key"], (row["value"], row["doc_name"])))
        .collectAsMap()
    )

    doc_lengths = {doc_id: doc_info[doc_id][0] for doc_id in doc_info}
    doc_titles = {doc_id: doc_info[doc_id][1] for doc_id in doc_info}

    top_docs = doc_scores.takeOrdered(10, key=lambda x: -x[1])
    print(f"\nTop 10 documents by BM25 score for query {query}:")
    for doc_id, score in top_docs:
        title = doc_titles.get(doc_id, "Unknown Title")
        print(f"Score: {score:.4f} | DocID: {doc_id} | Title: {title}")

    spark.stop()


if __name__ == "__main__":
    main()
