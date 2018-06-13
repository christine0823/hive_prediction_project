#/bin/bash

workload="hive_setting"

function genConf() {
	if [ ${line:0:1} = "#" ]; then
		return 0
	fi
	conf=$(echo $1 | cut -d ' ' -f 1)
	begin=$(echo $1 |cut -d ' ' -f 2)
	end=$(echo $1 |cut -d ' ' -f 3)
	space=$(echo $1 |cut -d ' ' -f 4)
	text=$(echo $1 |cut -d ' ' -f 5)
	random=$(od -vAn -N4 -tu4  /dev/urandom)
	
	if [ "$text" == "" ]; then
		result=$(echo "$random%(($end-$begin)/$space+1)*$space+$begin" | bc)
	fi
	
	if [ "$text" != "" ]; then
                index=$(echo "$random%(($end-$begin)/$space+1)*$space+$begin" | bc)
		
		if [ "$(echo $text | grep BLANK)" != "" ]; then
			result=$(echo "$random%(($end-$begin)/$space+1)*$space+$begin" | bc)
			result=$(echo $text | sed "s/BLANK/$result/g")
		else
			result=$(echo $text |cut -d '/' -f $index)
		fi 
        fi

	echo "set $conf=$result;"
	echo "set $conf=$result;" >> ${workload}.para
}

echo -n "" >  ${workload}.para

while IFS='' read -r line || [[ -n "$line" ]]; do
	genConf "$line"
done < "${workload}.conf"
