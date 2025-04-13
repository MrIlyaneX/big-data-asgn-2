from pathvalidate import sanitize_filename
from pyspark.sql import SparkSession


def main():
    spark = SparkSession.builder \
    .appName('data preparation') \
    .master("local") \
    .config("spark.sql.parquet.enableVectorizedReader", "true") \
    .config("spark.executor.memory", "2g") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()


    df = spark.read.parquet("/a.parquet")
    n = 1000
    df = df.select(['id', 'title', 'text']).sample(fraction=100 * n / df.count(), seed=0).limit(n)


    def create_doc(row):
        filename = "data/" + sanitize_filename(str(row['id']) + "_" + row['title']).replace(" ", "_") + ".txt"
        with open(filename, "w") as f:
            f.write(row['text'])


    df.foreach(create_doc)

    rdd = df.rdd.map(lambda row: f"{row['id']}\t{row['title']}\t{row['text']}")
    rdd.saveAsTextFile("/index/data")
    dd.collect()

if __name__ == "__main__":
    main()
