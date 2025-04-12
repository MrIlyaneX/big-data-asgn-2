#!./bin/bash

echo "Running prepare_data.sh"

source /opt/venv/bin/activate

# Python of the driver (/opt/venv)
export PYSPARK_DRIVER_PYTHON=$(which python) 
unset PYSPARK_PYTHON


# Idea to have downloaded file if /app folder
# Auto-download requres use of kaggle-api, I could not use it easily in the script
# and ordinary download-liks turned out to be temporary
ZIPPED_PARQUET_FILE="a.parquet.zip"
PARQUET_FILE="a.parquet"

if [ ! -f "$PARQUET_FILE" ]; then
    echo "Unzipping $ZIPPED_PARQUET_FILE"
    unzip "$ZIPPED_PARQUET_FILE"
else
    echo "$PARQUET_FILE was found"
fi

# clear data folder for future parquet file unpacking
if [ -d "data" ]; then
    rm -rf data
    mkdir data
else
    mkdir data
fi

hdfs dfs -test -d /index/data && hdfs dfs -rm -r -skipTrash /index/data

# Changed configs so no memory issues arise (had error of java heap)
hdfs dfs -put -f a.parquet / && \
    spark-submit \
    --master yarn \
    --deploy-mode client \
    --executor-memory 2g \
    --driver-memory 2g \
    prepare_data.py

echo "Putting data to hdfs" && \
hdfs dfs -put data / && \
hdfs dfs -ls /data && \
hdfs dfs -ls /index/data && \
echo "done data preparation!"

deactivate