CHUCH=$1
OUTPUT=$2
N=$3

function insertConf() {
        echo $line
}

rm time/${OUTPUT}.out

echo "set parameter"
cp parameters.ori.tcl parameters_test.tcl

while IFS='' read -r line || [[ -n "$line" ]]; do
        insertConf "$line"
done < "hadoop.para" >> parameters_test.tcl

echo "clean"
make dist-clean
echo "topo"
./conv.py -t topology1.xml -m random.xml -j job1.xml
echo "gen"
./gen.py -t topology1.xml -g data/metadata$1.xml -m random.xml
echo "make"

for i in $(seq 1 $N); do
	ns hsim.tcl;
done > tmp 2>&1

#cat tmp
# Run $SAMPLES times for average
echo $(cat tmp | grep Total | cut -d' ' -f3| awk '{ total += $1 } END { print total/NR }') > time/${OUTPUT}.out

cat time/${OUTPUT}.out
