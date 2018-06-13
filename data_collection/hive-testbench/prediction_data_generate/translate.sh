#/bin/bash


function echoProgress() {
        echo -e "\E[0;94m$1\E[0m"
}

ROOT_DIR=~/hive-testbench/profile_data_generate
QUERY_DIR=$ROOT_DIR/../sample-queries-tpch
#LOG_OUTPUT=$ROOT_DIR/profile1.log
DB_SCALE_RANGE=4
QUERY_RANGE=22
SETTING=$ROOT_DIR/testbench.settings
SQL_FILE=$ROOT_DIR/execute.hql
LOG_FILE=$ROOT_DIR/hive.log
PLAN_FILE="$ROOT_DIR/planQ$2.log"

echoProgress "Set Database"
        rm $SQL_FILE
        db_scale=$1
        echo "Database: tpch_flat_orc_$db_scale"
        echo "use tpch_flat_orc_$db_scale;" >> $SQL_FILE
	#echo "Database: tpch_text_$db_scale"
        #echo "use tpch_text_$db_scale;" >> $SQL_FILE
if [ $?=="0" ] ; then echo "Done"; fi

echoProgress "Choose Query"
        #workload=$QUERY_DIR/tpch_query$(bash genRandom.sh $QUERY_RANGE).sql
        workload=$QUERY_DIR/tpch_query$2.sql
        echo "Workload: $workload"
	sql=$(cat $workload)
	echo "explain $sql" >> $SQL_FILE
if [ $?=="0" ] ; then echo "Done"; fi

echoProgress "Running..."
        echo "hive -i $SETTING -f $SQL_FILE"
        hive -i $SETTING -f $SQL_FILE > $LOG_FILE 2>&1
if [ $?=="0" ] ; then echo "Done"; fi

echoProgress "Translating..."
	out=$(grep -A30 "STAGE DEPENDENCIES:" hive.log)
	printf '%s\n' "$out" | while IFS= read -r line; do 
		if [ "$line" = "STAGE PLANS:" ]
		then
    			break
		fi

		printf '%s\n' "$line" 
	done > $PLAN_FILE 
if [ $?=="0" ] ; then echo "Done"; fi
