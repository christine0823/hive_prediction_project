#!/bin/bash

ROOT=~/hive_prediction

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
	#echo $queryid

	if [ "$job_state" == "SUCCEEDED" ] && [ "$queryid" != "$last_queryid" ]; then
		queryid=$(echo $line | jq .queryid | tr -d '\"' | tr -d ' ')
		total_time=$(echo $line | jq .total_time | tr -d '\"')
		job_num=$(grep $queryid $1 | wc -l)
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
				bash jsonFilter1.sh "line_out" >> $2
                		#bash mergeProfile.sh $PROFILE_LOG $job_type >> $2
			else
				echo "fail" >> $2
				break
			fi
			echo "" >>$2
		done
		if [ $i -ne $((job_num+1)) ]; then
			echo $i
			echo "Check!!"
		fi 
		last_queryid=$queryid
	fi
done < "$1"


sed -i "s/-Xmx//g" $2
sed -i "s/m//g" $2

#bash firsh_label.sh $2
