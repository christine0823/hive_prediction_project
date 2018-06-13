#/bin/bash

RANGE=$1

begin=1
end=$RANGE
space=1
random=$(od -vAn -N4 -tu4  /dev/urandom)
result=$(echo "$random%(($end-$begin)/$space+1)*$space+$begin" | bc)

echo $result
