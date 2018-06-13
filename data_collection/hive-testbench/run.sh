#!/bin/bash

for i in {1,2,4,8,16,32,64,128}; do
        #hive --hiveconf mapreduce.job.reduces=$i --hiveconf mapreduce.reduce.shuffle.parallelcopies=50 --hiveconf hive.input.format=org.apache.hadoop.hive.ql.io.HiveInputFormat -f sample-queries-tpch/$1 --database tpch_flat_orc_$2;
        hive --hiveconf mapreduce.job.reduces=$i -f sample-queries-tpch/$1 --database tpch_flat_orc_$2;
done


