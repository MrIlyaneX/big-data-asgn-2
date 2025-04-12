#!/bin/bash
echo "This script include commands to run mapreduce jobs using hadoop streaming to index documents"


PIPE_1_INPUT="/index/data/part-*"

hdfs dfs -test -d /tmp/index && hdfs dfs -rm -r -skipTrash /tmp/index 

hdfs dfs -ls /index/data

# Pipeline 1 - creating statistics
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files /app/mapreduce/mapper1.py,/app/mapreduce/reducer1.py \
  -archives /app/.venv.tar.gz#.venv \
  -D mapreduce.reduce.memory.mb=2048 \
  -D mapreduce.framework.name=yarn \
  -D mapreduce.reduce.java.opts=-Xmx1800m \
  -mapper ".venv/bin/python mapper1.py" \
  -reducer ".venv/bin/python reducer1.py 2> reducer.log" \
  -input "$PIPE_1_INPUT" \
  -output /tmp/index/pipe1 \
  -numReduceTasks 1

hdfs dfs -ls /tmp/index/pipe1
hdfs dfs -cat /tmp/index/pipe1/part-*

# pipeline 2 - transfer statistics to cassandra
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files /app/mapreduce/mapper2.py,/app/mapreduce/reducer2.py \
  -archives /app/.venv.tar.gz#.venv \
  -D mapreduce.reduce.memory.mb=2048 \
  -D mapreduce.framework.name=yarn \
  -mapper ".venv/bin/python mapper2.py" \
  -reducer ".venv/bin/python reducer2.py" \
  -input /tmp/index/pipe1/part-* \
  -output /tmp/index/pipe2 \
  -numReduceTasks 1


echo "Input file is :"
echo $1


hdfs dfs -ls /
