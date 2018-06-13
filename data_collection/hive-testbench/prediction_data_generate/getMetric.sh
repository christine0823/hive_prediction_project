#/bin/bash

if [ "$2" = "" ]; then
        echo "usage: sh getMetric.sh StartTime FinishTime"
        exit 0;
fi

#LOG_DIR=/home/hadoop/log
KEYSTONE_SERVER_HOST=140.114.91.185
KEYSTONE_SERVER_PORT=35357
KEYSTONE_SERVER=${KEYSTONE_SERVER_HOST}:${KEYSTONE_SERVER_PORT}

SAHARA_SERVER_HOST=140.114.91.185
SAHARA_SERVER_PORT=8386
SAHARA_SERVER=${SAHARA_SERVER_HOST}:${SAHARA_SERVER_PORT}

CEILOMETER_SERVER_HOST=140.114.91.185
CEILOMETER_SERVER_PORT=8777
CEILOMETER_SERVER=${CEILOMETER_SERVER_HOST}:${CEILOMETER_SERVER_PORT}

CLUSTER_HOSTNAME="LargeT"
WORKER_HOSTNAME="W-L"

token=$(
	curl -si -X POST -H "Content-Type: application/json" \
	-d '{ "auth": { "identity": { "methods": [ "password" ], "password": { "user": { "domain": { "name": "default" }, "name": "admin", "password": "lsarocks" } } }, "scope": { "project": { "domain": { "name": "default" }, "name": "admin" } } } }' \
	http://${KEYSTONE_SERVER}/v3/auth/tokens |
	grep X-Subject-Token |
	sed 's/X-Subject-Token: //g'
)
#echo "Token: $token"

project_id=$(
	curl -s -X POST -H "Content-Type: application/json" \
	-d '{ "auth": { "identity": { "methods": [ "password" ], "password": { "user": { "domain": { "name": "default" }, "name": "admin", "password": "lsarocks" } } }, "scope": { "project": { "domain": { "name": "default" }, "name": "admin" } } } }' \
	http://${KEYSTONE_SERVER}/v3/auth/tokens |
	jq ".token.project.id" |
	sed 's/"//g'
)
#echo "Project ID: $project_id"

instance_id=$(
	curl -X GET -H X-Auth-Token:$token \
	"http://${SAHARA_SERVER}/v1.1/${project_id}/clusters" |
	jq '.clusters[] | select(.name=="'$CLUSTER_HOSTNAME'") | .node_groups[] | select(.name=="'$WORKER_HOSTNAME'") | .instances[].instance_id' |
	sed 's/"//g'
)
#echo "Instance ID: $instance_id"

start_time=$(TZ='UTC' date --date=@${1:0:-3} +%Y-%m-%dT%T)
end_time=$(TZ='UTC' date --date=@${2:0:-3} +%Y-%m-%dT%T)
#echo "Start time: $start_time"
#echo "Finish time: $end_time"

period=$(((${2:0:-3}-${1:0:-3})/4+1))
#echo "Elasped time: $(((${2:0:-3}-${1:0:-3})))"
#echo "Period: $period"

#curl -X GET -H X-Auth-Token:$token \
#"http://${CEILOMETER_SERVER}/v2/meters" | jq .[].name | sort | uniq

metrics="cpu_util memory.usage disk.read.bytes disk.write.bytes network.incoming.bytes network.outgoing.bytes"

for metric in ${metrics} ; do
	comm=""
	comm=${comm}"curl -X GET -H X-Auth-Token:$token "
	comm=${comm}"http://${CEILOMETER_SERVER}/v2/meters/${metric}/statistics?"
	if [ ${metric:0:4} != "disk" ] && [ ${metric:0:7} != "network" ];then
		comm=${comm}"aggregate.func=stddev&"
	fi
	comm=${comm}"aggregate.func=avg&"
	comm=${comm}"aggregate.func=sum&"
	comm=${comm}"aggregate.func=max&"
	comm=${comm}"aggregate.func=min&"
	comm=${comm}"aggregate.func=count&"
	comm=${comm}"q.field=timestamp&"
	comm=${comm}"q.op=ge&"
	comm=${comm}"q.value=${start_time}&"
	comm=${comm}"q.field=timestamp&"
	comm=${comm}"q.op=lt&"
	comm=${comm}"q.value=${end_time}&"
	comm=${comm}"groupby=project_id&"
	comm=${comm}"groupby=resource_id&"
	comm=${comm}"period=${period}"
	
	#echo "$comm"	
	data=$($comm)

	tmp1=""
	for i in ${instance_id} ; do
		tmp1=$(echo $data | jq '.[] | select(.groupby.resource_id | contains("'$i'"))')$tmp1
	done
	
	#result=$(echo $tmp1 $result | jq -s .)
	result=$result$tmp1
	#echo $result | jq .
done

result=$(echo $result | jq -s .)
result=$(echo $result | jq '.| {metric: .}')
#exit 0

data=$(
	curl -X GET -H X-Auth-Token:$token \
	"http://${CEILOMETER_SERVER}/v2/resources"
)
tmp1=""
for i in ${instance_id} ; do	
	tmp1=$(echo $data | jq '.[] | select(.resource_id=="'$i'") | {metadata: .metadata, resource_id: .resource_id}')$tmp1
done

result=$(echo $tmp1 | jq -s '. | {"instance": .}')$result
result=$(echo $result | jq -s add)
echo $result
