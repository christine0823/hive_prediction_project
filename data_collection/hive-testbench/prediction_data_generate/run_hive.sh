#/bin/bash

function echoProgress() {
	echo -e "\E[0;94m$1\E[0m"
}
# $1 : query
# $2 : scale
sqlid=$1
ROOT_DIR=~/hive-testbench/prediction_data_generate
QUERY_DIR=$ROOT_DIR/../sample-queries-tpch
LOG_OUTPUT="$ROOT_DIR/logs/query${sqlid}.log"
DB_SCALE_RANGE=4
QUERY_RANGE=21
SETTING=$ROOT_DIR/testbench.settings
SQL_FILE=$ROOT_DIR/execute.hql
PLAN_FILE=$ROOT_DIR/explain.hql
LOG_FILE=$ROOT_DIR/hive.log
PlAN_DIR=$ROOT_DIR/logs/plan
PLOG_FILE=$ROOT_DIR/plan.log

declare -a SCALES
SCALES[1]=5
SCALES[2]=10
SCALES[3]=25
SCALES[4]=50
#SCALES[5]=100
#SCALES[6]=2

rm $SQL_FILE
rm $PLAN_FILE

echoProgress "Set Database"
	index=$(bash genRandom.sh $DB_SCALE_RANGE)
	#index=$2
	db_scale=${SCALES[$index]}
	echo "Database: tpch_flat_orc_$db_scale"
        echo "use tpch_flat_orc_$db_scale;" >> $SQL_FILE
        echo "use tpch_flat_orc_$db_scale;" >> $PLAN_FILE
if [ $?=="0" ] ; then echo "Done"; fi

echoProgress "Choose Query"
        #sqlid=$(bash genRandom.sh $QUERY_RANGE)
	sqlid=$1
	workload=$QUERY_DIR/tpch_query${sqlid}.sql
        echo "Workload: $workload"
	echo "source $workload;" >> $SQL_FILE
if [ $?=="0" ] ; then echo "Done"; fi

echoProgress "Generate configurations"
        bash genConf_hive.sh 
if [ $?=="0" ] ; then echo "Done"; fi

echoProgress "Set configurations"
       bash setConf_hive.sh ${SETTING}
if [ $?=="0" ] ; then echo "Done"; fi

echoProgress "Explaining..."
	sql=$(cat $workload)
        echo "explain $sql" >> $PLAN_FILE
        echo "hive -i $SETTING -f $PLAN_FILE"
        hive -i $SETTING -f $PLAN_FILE > $PLOG_FILE 2>&1
	
if [ $?=="0" ] ; then echo "Done"; fi

echoProgress "Translating..."
        out=$(grep -A50 "STAGE DEPENDENCIES:" $PLOG_FILE)
        dependency=$(printf '%s\n' "$out" | while IFS= read -r line; do
                if [ "$line" = "STAGE PLANS:" ]
                then
                        break
                fi
                line=$(echo $line | grep -v 'consists')
                line=$(echo $line | grep -v 'backup')
                line=$(echo $line | grep 'Stage-[0-9]\+ ')
                line=$(echo $line | sed 's/Stage-//g')
                line=$(echo $line | sed 's/depends on stages:/<-/g')
                if [ "$line" != "STAGE DEPENDENCIES:" ] && [ "$line" != "" ]
                then
                        printf '%s|' "$line"
                fi
        done)
        echo $dependency
if [ $?=="0" ] ; then echo "Done"; fi

echoProgress "Running..."
	echo "hive -i $SETTING -f $SQL_FILE"
	hive -i $SETTING -f $SQL_FILE > $LOG_FILE 2>&1
if [ $?=="0" ] ; then echo "Done"; fi

echoProgress "Get job ID"
	queryid=$(cat $LOG_FILE | grep "Query" | awk -F' ' '{printf("%s ",$4)}' | sed 's/,//g')
        jobid=$(cat $LOG_FILE | grep "Starting Job =" | awk -F' ' '{printf("%s ",$4)}' | sed 's/,//g')
	echo "Query ID: $queryid"
	echo "Job ID: $jobid"
if [ $?=="0" ] ; then echo "Done"; fi

echoProgress "Compute time"
	exetime=$(tail -n 1 $LOG_FILE | awk -F' ' '{printf("%s ",$3)}' | sed 's/ //g')
	echo "Total time: $exetime"
if [ $?=="0" ] ; then echo "Done"; fi

for i in $jobid ; do

	echoProgress "Get Hadoop log ($i)"	
		hadoop_log=$(bash getLog.sh $i)
	if [ $?=="0" ] ; then echo "Done"; fi
	stage=$(echo $hadoop_log | jq .job.name | grep -o "Stage-[0-9]\+" | grep -o "[0-9]\{,2\}")
	str="Stage-"$stage

	maptype=$(grep -A1000 "STAGE PLANS:" $PLOG_FILE | grep -A50 $str | grep -A1 -m 1 "Map Operator Tree:"|awk '{print $1}'|tail -n 1)	
	reducetype=$(grep -A1000 "STAGE PLANS:" $PLOG_FILE | grep -A50 $str | grep -A1 -m 1 "Reduce Operator Tree:"|awk '{print $1}'|tail -n 1)
	
	if [ "$reducetype" = "" ];then
		reducetype="None"
	fi
	
	jobtype=$maptype"_"$reducetype

	echo "Stage: "$stage
	echo "Type: "$jobtype
	data=$hadoop_log$(echo "{\"queryid\": \""$queryid"\"}")$(echo "{\"sqlid\": \""$sqlid"\"}")$(echo "{\"total_time\": \""$exetime"\"}")$(echo "{\"scale\": \""$db_scale"\"}")$(echo "{\"stage\": \""$stage"\"}")$(echo "{\"type\": \""$jobtype"\"}")$(echo "{\"plan\": \""$dependency"\"}")
	echo $data | jq -s add | jq -c . >> $LOG_OUTPUT
done
