#!/bin/bash

sleep 5

# Check if the replica set is already initiated
isInitialized=$(docker exec -it mongo1 mongo --quiet --eval "rs.isMaster().ismaster")

if [ "$isInitialized" == "true" ]; then
  echo "Replica set is already initialized. Skipping rs.initiate()."
else
  echo "Initializing replica set..."

  # Execute the rs.initiate command
  docker exec -it mongo1 mongo --eval "rs.initiate({
    _id: 'myReplicaSet',
    members: [
      { _id: 0, host: 'mongo1' },
      { _id: 1, host: 'mongo2' },
      { _id: 2, host: 'mongo3' }
    ]
  })"
fi