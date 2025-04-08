#!./bin/bash

echo "Running prepare_data.sh"

source .venv/bin/activate


# Python of the driver (/app/.venv/bin/python)
export PYSPARK_DRIVER_PYTHON=$(which python) 


unset PYSPARK_PYTHON

# DOWNLOAD a.parquet or any parquet file before you run this

# Dowloading the parquet file if it does not exists, then unzip it (link taken from kaggle)
# the link is hardcoded to get the a.parquet, but it could be changed
ZIPPED_PARQUET_FILE="a.parquet.zip"
PARQUET_FILE="a.parquet"

if [ ! -f "$ZIPPED_PARQUET_FILE" ]; then
    echo "Downloading $ZIPPED_PARQUET_FILE"
    curl -L -o "$ZIPPED_PARQUET_FILE" "https://storage.googleapis.com/kaggle-data-sets/3521629/6146260/compressed/a.parquet.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20250408%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20250408T075617Z&X-Goog-Expires=259200&X-Goog-SignedHeaders=host&X-Goog-Signature=70a247575102a73cba5373771f704ab4002da6499e610dc298693553f0583d958c781df8e2db70483db6b35b55fedd6b8722c67dee0351da182ac511493521089d6ce390c4b7d1d432a56d49110346c47c73ba2f1c2ac2933903bddccbc25d0e2dd72eb6e4fdd010e3abb9c075703519f9f6d46e56c9efea1f96977e406326d10a4bab603d9506bed5dd67a642c4338d611cc4fcf413c170226d12413e2cbc02da091bb3915d29bcde81713773aa4d4e39102b0fc552e7312498567a4a14974b0b7a5c30cc291c21ce7202f39a0764f0fde982a4aa92f69bae145069d8a8aa80f8e5cc692d646f86c8c68e30e9d14afdde9fabf435d7bc05891336577aeabbc9"
else
    echo "$ZIPPED_PARQUET_FILE was found"
fi

if [ ! -f "$PARQUET_FILE" ]; then
    echo "Unzipping $ZIPPED_PARQUET_FILE"
    unzip "$ZIPPED_PARQUET_FILE"
else
    echo "$PARQUET_FILE was found"
fi

hdfs dfs -put -f a.parquet / && \
    spark-submit prepare_data.py && \
    echo "Putting data to hdfs" && \
    hdfs dfs -put data / && \
    hdfs dfs -ls /data && \
    hdfs dfs -ls /index/data && \
    echo "done data preparation!"
