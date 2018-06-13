#/bin/bash

LOGS=$1
COMMENT=$2

function getValue() {
	tmp1=$(echo ${LOGS} | jq ''{"$1"': '"$2"}'')
	result=$result$tmp1
	
}

result=""

getValue hdfs_bytes_read ".counters[\"HDFS_BYTES_READ.total\"]"
getValue instance_type ".instance[0].metadata[\"flavor.name\"]"
getValue instance_count ".instance | length"
getValue job_name ".job.name"
getValue job_state ".job.state"

result=$result$(echo "{\"comment\": \""$COMMENT"\"}")
echo $result | jq -s add
