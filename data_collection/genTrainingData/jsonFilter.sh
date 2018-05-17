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
hive.merge.size.per.task
mapreduce.job.reduces
mapreduce.job.jvm.numtasks
hive.map.aggr
hive.fetch.task.conversion
hive.auto.convert.join.noconditionaltask
hive.auto.convert.sortmerge.join
hive.groupby.skewindata
hive.auto.convert.join
hive.mapjoin.smalltable.filesize
hive.exec.compress.output
hive.exec.compress.intermediate
hive.metastore.server.max.threads
hive.mapred.reduce.tasks.speculative.execution
hive.vectorized.execution.enabled
hive.exec.mode.local.auto
hive.optimize.correlation
mapreduce.tasktracker.map.tasks.maximum
mapreduce.tasktracker.reduce.tasks.maximum
mapreduce.task.io.sort.mb
mapreduce.task.io.sort.factor
mapreduce.reduce.shuffle.parallelcopies
mapreduce.reduce.shuffle.input.buffer.percent
mapreduce.reduce.shuffle.merge.percent
mapreduce.reduce.shuffle.memory.limit.percent
mapreduce.map.sort.spill.percent
mapreduce.reduce.input.buffer.percent
mapreduce.reduce.merge.inmem.threshold
mapreduce.job.reduce.slowstart.completedmaps
mapreduce.jobtracker.handler.count
mapreduce.tasktracker.http.threads
mapreduce.map.cpu.vcores
mapreduce.reduce.cpu.vcores
mapreduce.map.memory.mb
mapreduce.reduce.memory.mb
yarn.app.mapreduce.am.resource.mb
yarn.app.mapreduce.am.resource.cpu-vcores
mapreduce.map.output.compress
mapreduce.output.fileoutputformat.compress
mapreduce.output.fileoutputformat.compress.type
mapred.child.java.opts
"
declare -a RECORDS
RECORDS[5]=4000000
RECORDS[10]=8000000
RECORDS[25]=20000000
RECORDS[50]=40000000

output=""
output=$output$(echo $data | jq '.job.finishTime - .job.startTime')","
record=$(echo $data | jq .counters | jsonFilter $counters | tr -d '\"')
jobtype=$(echo $data | jq .type | tr -d '\"')
scale=$(echo $data | jq .scale | tr -d '\"')
dataset=${RECORDS[$scale]}

output=$output$jobtype","
output=$output$record","
output=$output$dataset","
output=$output$(echo $data | jq .conf  | jsonFilter $conf | tr -d '\"')

#echo ${output:0:-1}
echo -n ${output}
