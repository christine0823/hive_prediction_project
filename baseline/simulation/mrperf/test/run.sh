DAG=$1
DATASET=$2
JOBLEN=$3


for jobN in $(seq 1 $JOBLEN);
do
	echo $jobN
	chunkCount=$(python ../../mrperf/test/simulation/simulate.py --i ../../mrperf/test/simulation/simulate$DAG.csv --d $DATASET --n $jobN --l $JOBLEN --o ../../mrperf/test/hadoop.para)
	echo "chunk :"$chunkCount
	bash simulation.sh $chunkCount $DATASET"-"$jobN 1
done
