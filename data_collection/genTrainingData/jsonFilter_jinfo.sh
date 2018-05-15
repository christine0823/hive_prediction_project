#!/bin/bash

if [ "$1" = "" ]; then
        echo "usage: sh jsonFilter.sh file"
        exit 0;
fi

data=$(cat $1)

function jsonFilter() {

        for i in $@ ; do
		cmd=$cmd".\"$i\","
	done
        jq -r "[${cmd:0:-1}] | @csv"
}

info="
job_name
instance_count
instance_type
"

counters="
RECORDS_IN.total
"

job="
startTime
finishTime
"

conf="
mapreduce.job.reduces
hive.map.aggr
hive.fetch.task.conversion
hive.auto.convert.join.noconditionaltask
hive.auto.convert.sortmerge.join
hive.groupby.skewindata
hive.auto.convert.join
hive.vectorized.execution.enabled
hive.exec.mode.local.auto
hive.optimize.correlation
mapreduce.map.memory.mb
mapreduce.reduce.memory.mb
yarn.app.mapreduce.am.resource.mb
mapred.child.java.opts
"
declare -a RECORDS
RECORDS[5]=4000000
RECORDS[10]=8000000
RECORDS[25]=20000000
RECORDS[50]=40000000

output=""
scale=$(echo $data | jq .scale | tr -d '\"')
total_records=${RECORDS[$scale]}

records=$(echo $data | jq .counters | jsonFilter $counters | tr -d '\"')
jobtype=$(echo $data | jq .type | tr -d '\"')

output=$output$jobtype","
output=$output$records","
output=$output$total_records","
output=$output$(echo $data | jq .conf  | jsonFilter $conf | tr -d '\"')

#echo ${output:0:-1}
echo -n ${output}
