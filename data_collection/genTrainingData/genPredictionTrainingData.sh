#!/bin/bash

if [ "$2" = "" ]; then
        echo "usage: sh genTrainingData.sh IN_FILE OUT_FILE"
        exit 0;
fi

rm $2
#data_size_list=$(cat $1 | jq .)

last_queryid=""

while IFS='' read -r line || [[ -n "$line" ]]; do

	job_state=$(echo $line | jq .job.state | tr -d '\"')
	queryid=$(echo $line | jq .queryid | tr -d '\"' | tr -d ' ')
	echo $queryid
	
	if [ "$job_state" == "SUCCEEDED" ] && [ "$queryid" != "$last_queryid" ]; then
		queryid=$(echo $line | jq .queryid | tr -d '\"' | tr -d ' ')
		total_time=$(echo $line | jq .total_time | tr -d '\"')
		job_num=$(grep $queryid $1 | wc -l)
		
		check=$(echo $total_time | grep [0-9])
		if [ "$check" == "" ]; then
			last_queryid=$queryid
			continue
		fi
	
		echo $total_time,$job_num >>$2		
		
		grep $queryid $1 > tmp	
		echo "write"
		echo $job_num
	
		for (( i=1; i<=$job_num; i++ ))
		do
			#get the specific line
			line=$(cat tmp | sed -n ${i}p)
			job_state=$(echo $line | jq .job.state | tr -d '\"')
			job_type=$(echo $line | jq .type | tr -d '\"')
 			echo $line > line_out	
			#echo $job_type
			if [ "$job_state" = "SUCCEEDED" ]; then
				bash jsonFilter.sh "line_out" >> $2
			else
				echo "Fail, please delete the samples!" >> $2
				break
			fi
			echo "" >>$2
		done
		last_queryid=$queryid
	fi
done < "$1"


bash firsh_label.sh $2
