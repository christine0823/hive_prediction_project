
MRPerf/MapTask instproc schedule {hnode} {
	$self def-schedule $hnode
	#$self remote-schedule $hnode
}

MRPerf/MapTask instproc add-counter {name} {
	global ns
	[$self set counters] set $name [expr [$ns now] * 1000]
}

MRPerf/MapTask instproc add1-counter {counter name} {
	global ns
	$counter set $name [expr [$ns now] * 1000]
}

MRPerf/MapTask instproc write-counters {} {
	global stats
	set c [$self set counters]

	set counters "File Systems.Local bytes read:[$self set output_size],File Systems.Local bytes written:[expr 2*[$self set output_size]],File Systems.HDFS bytes read:[$self set input_size],Performance Counters.INIT:[$c set init],Performance Counters.MAP_START:[$c set map_start],Performance Counters.MAP_FINISH:[$c set map_finish]"

	for {set i 0} {$i < [$self set spill]} {incr i} {
		set p [$c set processes($i)]
		set counters [format "%s%s%s%s" "$counters,Performance Counters.$i" "_SORT_START:[$p set sort_start],Performance Counters.$i" "_SORT_FINISH:[$p set sort_finish],Performance Counters.$i" "_SPILL_FINISH:[$p set spill_finish]" ]
	}

	if {[$self set has_merge] == 1} {
		set counters "$counters,Performance Counters.MERGE_START:[$c set merge_start],Performance Counters.MERGE_FINISH:[$c set merge_finish]"
	}

	puts $stats "Task TASKID=\"$self\" TASK_TYPE=\"MAP\" TASK_STATUS=\"SUCCESS\" FINISH_TIME=\"[$self set finish_time]\" COUNTERS=\"$counters\""
}

MRPerf/NodeApp instproc jvm-start {task} {
	global jvm_start_cost
	#puts "jvm-start $task"
	set n [$task worker]

	$self inserts "$task add-counter init"

	#puts "****** jvm $jvm_start_cost ****************"
	$self insertd [expr 1.0*$jvm_start_cost] $n
}


MRPerf/NodeApp instproc spill {task size} {
	global sort_cycles_per_byte 

	#puts "spill $task $size"

	# spill to the same disk? or different disks?
	# wanggy 2008.7.24: assume a single-disk-per-node model
	set node [$task worker]
	set disk [$node choosedisk]

	set p [new MRPerf/Empty]
	[$task set counters] set processes([$task set spill]) $p
	$task set spill [expr [$task set spill] + 1]

	$task set output_size [expr [$task set output_size] + $size]

	$self inserts "$task add1-counter $p sort_start"
	$self insertd [expr 1.0*$size * $sort_cycles_per_byte] $node
	$self inserts "$task add1-counter $p sort_finish"
	$self iowrite $size $disk
	$self inserts "$task add1-counter $p spill_finish"
}

MRPerf/NodeApp instproc readsize {task offset size} {
	#puts "readsize $task $offset $size"
	set disk [$task disk]
	$self ioread $size $disk
}

MRPerf/NodeApp instproc merge {task} {
	#puts "merge $task"

	set node [$task worker]
	set disk [$node choosedisk]

	set length [$task set output_size]

	$task set has_merge 1

	set c [$task set counters]
	$self inserts "$task add1-counter $c merge_start"
	$self ioread $length $disk
	$self iowrite $length $disk
	$self inserts "$task add1-counter $c merge_finish"
}

MRPerf/NodeApp instproc compute {task offset size} {
	#puts "compute $task $offset $size"
	global cycles_per_byte
	set n [$task worker]
	$self insertd [expr 1.0* $size * $cycles_per_byte] $n
}

MRPerf/NodeApp instproc wrap-up {task} {
	global wrap_up_cost
	set n [$task worker]
	$self insertd $wrap_up_cost $n
}

MRPerf/MapTask instproc mark_ghost {} {
	if {[$self info vars ghost] != ""} {
		return
	}
	$self set ghost 1

	global no_maptasks_to_start finished_maptasks
	$self cpp_fail
	incr no_maptasks_to_start

	lremove finished_maptasks $self
}

MRPerf/MapTask instproc fail {} {
	global ns stats no_maptasks_to_start
	puts "[$ns now]: map $self fail"
	puts $stats "MapAttempt TASKID=\"$self\" TASK_STATUS=\"KILLED\" FINISH_TIME=\"[expr [$ns now]*1000]\" HOSTNAME=\"[[$self worker] hostname]\""

	if {[$self info vars alive_timer] != ""} {
		$ns cancel [$self set alive_timer]
	}
	$ns cancel [[$self set expire_timer] set eid]
	$self cpp_fail
	incr no_maptasks_to_start
	set nrm [[$self worker] set running_maptasks]
	[$self worker] set running_maptasks [expr $nrm-1]
}

MRPerf/NodeApp instproc start_maptask { node } {
	global stats max_mappers timers

	if {[$node set running_maptasks] >= $max_mappers} {
		#puts "$node already has [$node set running_maptasks] map tasks running!"
		return 0
	}

	set taskstr [new MRPerf/MapTask]
	$taskstr set counters [new MRPerf/Empty]
	$taskstr set spill 0
	$taskstr set has_merge 0
	$taskstr set output_size 0
	set result [$taskstr schedule $node]
	if {$result != "" } {
		set app2 [$self new-connection $node]
		$app2 snd "map task $taskstr"
		puts $stats "Task TASKID=\"$taskstr\" TASK_TYPE=\"MAP\" START_TIME=\"[$self now]\" SPLITS=\"[[[$taskstr disk] host] hostname]\""
		#$node set uncounted [expr [$node set uncounted] + 1]
		$node set running_maptasks [expr [$node set running_maptasks]+1]
		$taskstr set expire_timer [new MRPerf/Timer $timers(task_dead) "$taskstr fail"]

		upvar #0 no_maptasks_to_start m
		set m [expr $m-1]
		#puts "$m map tasks to start"
		return 1
	}
	return 0

}

MRPerf/NodeApp instproc send_alive {task} {
	global ns timers
	$self snd "alive $task"
	$task set alive_timer [$ns after $timers(alive) "$self send_alive $task"]
}

