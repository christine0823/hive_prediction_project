#!/bin/bash

bash tpch-setup.sh 5 hdfs://hdfs:9000/Hive
sleep 1
bash tpch-setup.sh 10 hdfs://hdfs:9000/Hive
sleep 1
bash tpch-setup.sh 25 hdfs://hdfs:9000/Hive
sleep 1
bash tpch-setup.sh 50 hdfs://hdfs:9000/Hive
sleep 1

#bash run.sh tpch_query1.sql 50
#sleep 10
#bash run.sh tpch_query1_v1.sql 50 
