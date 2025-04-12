#!/bin/bash
# Start ssh server
service ssh restart 

# Starting the services
bash start-services.sh

echo "Using venv at /opt/venv"
source /opt/venv/bin/activate

# Package the virtual env.
venv-pack -p /opt/venv

# build cassandra tables
python init_cassandra.py
deactivate

# Collect data
bash prepare_data.sh

# Run the indexer
bash index.sh data/sample.txt

# Run the ranker
bash search.sh "this is a query!"
