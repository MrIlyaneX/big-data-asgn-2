#!/bin/bash
echo "This script will include commands to search for documents given the query using Spark RDD"

#https://github.com/apache/cassandra-spark-connector/blob/trunk/doc/15_python.md

export PYSPARK_PYTHON=/opt/venv/bin/python
export PYSPARK_DRIVER_PYTHON=/opt/venv/bin/python
spark-submit \
    --master yarn \
    --deploy-mode client \
    --driver-memory 2g \
    --executor-memory 2G \
    --name "Ranker" \
    --archives /app/.venv.tar.gz#.venv \
    --conf spark.executor.memory=2g \
    --conf spark.driver.memory=2g \
    --conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=$PYSPARK_PYTHON \
    --conf spark.executorEnv.PYSPARK_PYTHON=$PYSPARK_PYTHON \
    --conf spark.sql.extensions=com.datastax.spark.connector.CassandraSparkExtensions \
    --packages com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 \
    --conf spark.cassandra.connection.host=cassandra-server \
    query.py "$@"