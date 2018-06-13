#!/bin/bash
LOG_OUTPUT=hadoop.log
for (( j=63; j <= 283; j++ )); 
do
	if [ $j -lt 100 ]; then i="job_1492752234356_00$j" 
	else i="job_1492752234356_0$j" 
	fi

#	echoProgress "Get Hadoop log ($i)"
                hadoop_log=$(bash getLog.sh $i)
        if [ $?=="0" ] ; then echo "Done"; fi

#        echoProgress "Get Ceilometer log ($i)"
                start_time=$(echo $hadoop_log | jq .job.startTime)
                echo "Start time: $start_time"
                finish_time=$(echo $hadoop_log | jq .job.finishTime)
                echo "Finish time: $finish_time"
                metric_log=$(bash getMetric.sh $start_time $finish_time)
                data=$(echo $hadoop_log $metric_log | jq -s add)
        if [ $?=="0" ] ; then echo "Done"; fi

#        echoProgress "Generate metadata ($i)"
                info=$(bash genInfo.sh "$data" "$COMMENT")
        if [ $?=="0" ] ; then echo "Done"; fi

        data=$(echo $info $data | jq -s add)
        echo $data >> $LOG_OUTPUT	
done
