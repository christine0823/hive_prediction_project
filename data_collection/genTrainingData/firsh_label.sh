#!/bin/bash

if [ "$1" = "" ]; then
        echo "usage: sh firsh_label.sh IN_FILE"
        exit 0;
fi

#label="0,0,"
#feature=$(head -n 1 $1 | grep -o , | wc -l)
#for ((i=0;i<$(($num_jobs));i++)); do
        #label=$label$(echo -n "0,0,1,0,0,0,0,1,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,")
#done

#sed -i 1"i\\${label:0:-1}" $1

sed -i 's/true/1/g' $2
sed -i 's/false/0/g' $2
sed -i 's/more/1,0,0/g' $2
sed -i 's/minimal/0,1,0/g' $2
sed -i 's/none/0,0,1/g' $2
sed -i 's/RECORD/0/g' $2
sed -i 's/BLOCK/1/g' $2
sed -i "s/-Xmx//g" $1
sed -i "s/m//g" $1
