#/bin/bash

if [ "$1" = "" ]; then
        echo "usage: sh getLog.sh JobID"
        exit 0;
fi

#LOG_DIR=/home/hadoop/hadoop-log
HISTORY_SERVER_HOST=$(hostname)
HISTORY_SERVER_PORT=19888
HISTORY_SERVER=${HISTORY_SERVER_HOST}:${HISTORY_SERVER_PORT}
jobid=$1

conf=$(
	curl -s ${HISTORY_SERVER}/ws/v1/history/mapreduce/jobs/${jobid}/conf |
	jq -r '.conf.property[] | {(.name): .value}' |
	jq -s add |
	jq '. | {conf: .}'
)
#echo $conf

#counters=$(
#	curl -s ${HISTORY_SERVER}/ws/v1/history/mapreduce/jobs/${jobid}/counters |
#	jq . |
#	grep "reduceCounterValue" -A 3
#)
#counters=$(
#	echo $counters |
#	sed 's/--/\n/g' |
#	awk -F' ' '{print "{"$0"}"}' |
#	jq -r '. | {(.name + ".map"): .mapCounterValue, (.name + ".reduce"): .reduceCounterValue, (.name + ".total"): .totalCounterValue}' |
#	jq -s add |
#	jq '. | {counters: .}'
#)
#echo $counters

#task_counters=$(
#	curl -s ${HISTORY_SERVER}/ws/v1/history/mapreduce/jobs/${jobid}/tasks|
#        jq .tasks| jq '. | select(.task[].state = "SUCCEEDED")' |
#        jq '.task[] | {"type" : .type, "startTime" : .startTime, "finishTime" : .finishTime}' |
#	jq -s . |
#	jq '. | {task_counters: .}'
#)
#echo $task_counters

job_status=$(
	curl -s ${HISTORY_SERVER}/ws/v1/history/mapreduce/jobs/${jobid}
)
#echo $job_status

result=$(echo $job_status $conf | jq -s add)
echo $result
#echo $result >> ${LOG_DIR}/hadoop.log
