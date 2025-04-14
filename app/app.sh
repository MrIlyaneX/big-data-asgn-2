#!/bin/bash
# Start ssh server
service ssh restart 

# Starting the services
bash start-services.sh

echo "Creating venv"

#tar -czf /app/.venv.tar.gz /opt/venv

source /opt/venv/bin/activate

# python3 -m venv .venv
# source .venv/bin/activate
# pip install -r requirements.txt  
venv-pack -o .venv.tar.gz

# build cassandra tables
echo "Building Cassandra Tables"
python app.py
deactivate

# Collect data
bash prepare_data.sh

# Run the indexer
bash index.sh data/sample.txt

# Run the ranker
bash search.sh "this is a query!"
