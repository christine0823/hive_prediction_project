#/bin/bash


LOG_DIR=/mnt/yarn/logs/userlogs/
jobID=$1


appID=$(echo $jobID | sed 's/job/application/g')
echo "cat $LOG_DIR$appID/*"
output=$(cat $LOG_DIR$appID/*)

