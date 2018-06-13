#/bin/bash

SETTING=$1
workload='hive_setting'

function insertConf() {
	echo $line
}

if [ -f ${SETTING}.ori ]; then
	cp ${SETTING}.ori ${SETTING}
fi



while IFS='' read -r line || [[ -n "$line" ]]; do
	insertConf "$line"
done < "${workload}.para" >> $SETTING
