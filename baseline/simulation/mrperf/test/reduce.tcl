
MRPerf/ReduceTask instproc schedule {hnode} {
	$self def-schedule $hnode
}

MRPerf/ReduceTask instproc add-counter {name} {
	global ns
	[$self set counters] set $name [expr [$ns now] * 1000]
}

MRPerf/ReduceTask instproc add1-counter {counter name} {
	global ns
	$counter set $name [expr [$ns now] * 1000]
}

MRPerf/ReduceTask instproc write-counters {} {
	global stats num_chunks
	set c [$self set counters]

	set counters "File Systems.HDFS bytes written:[$self set output_size],File Systems.Local bytes read:[$self set output_size],File Systems.Local bytes written:[$self set output_size]"

#	for {set i 0} {$i < $num_chunks} {incr i} {
#		set p [$c set copiers($i)]
#		set counters [format "%s%s%s%s" "$counters,Performance Counters.$i" "_COPIER_SCHEDULED:[$p set copier_scheduled],Performance Counters.$i" "_COPIER_RUN:[$p set copier_run],Performance Counters.$i" "_COPIER_FINISH:[$p set copier_finish]" ]
#	}

	puts $stats "Task TASKID=\"$self\" TASK_TYPE=\"REDUCE\" COUNTERS=\"$counters\""
}

MRPerf/NodeApp instproc reduce {rtask} {
	global reduce_cycles_per_byte
	global reduce_filter_ratio
	#puts "reduce $rtask"
	set size [$rtask set input_size]
	#puts "reduce size $size"
	set n [$rtask worker]
	set d [$n choosedisk]
	$self ioread $size $d
	$self insert1d [expr 1.0*$size*$reduce_cycles_per_byte] 1.04 $n
	$rtask set fr [$reduce_filter_ratio value]
	$rtask set output_size [expr $size * [$rtask set fr]]

	return [$rtask set output_size]
}

Class MRPerf/Queue

MRPerf/Queue instproc init {} {
	$self set _list [list]
	$self set space 0
	$self set count 0
}

MRPerf/Queue instproc attach {element} {
	set l [$self set _list]
	lappend l $element
	$self set _list $l
	$self set count [expr [$self set count] + 1]
	#puts [$self set space]
	$self set space [expr [$self set space] + [$element set size]]
	#puts "[$self set space] [$element set size]"
}

MRPerf/Queue instproc total-space {} {
	return [$self set space]
}

MRPerf/Queue instproc count {} {
	return [$self set count]
}

# split $self into two parts: first n elements goes to $newq,
# elements after remains in $self. newq has to be initiated.
MRPerf/Queue instproc split-first {n newq} {
	#puts "[$self set _list]"
	#puts "[$self set count] [$self set space]"

	$newq set _list [lrange [$self set _list] 0 [expr $n-1]]
	$newq set count $n
	set totalsize 0
	foreach element [$newq set _list] {
		#puts "[$element set size]"
		set totalsize [expr $totalsize + [$element set size]]
	}
	$newq set space $totalsize
	#puts "[$newq set _list]"
	#puts "[$newq set count] [$newq set space]"

	$self set _list [lreplace [$self set _list] 0 [expr $n-1]]
	$self set count [expr [$self set count] - $n]
	$self set space [expr [$self set space] - $totalsize]
	#puts "[$self set _list]"
	#puts "[$self set count] [$self set space]"

	return $newq
}

Class MRPerf/MergeFile

MRPerf/MergeFile instproc init {size} {
	$self set size $size
}

MRPerf/Queue instproc read-into-memory {app node} {
	set disk [$node choosedisk]
	set totalsize [$self total-space]
	$app ioread $totalsize $disk
}

# merge everything in inputq into a file, and attach it at the end of $self.
# Then empty inputq, delete objects in it
MRPerf/Queue instproc merge {inputq app node} {
	global merge_cycles
	set totalsize [$inputq total-space]
	set disk [$node choosedisk]
	set ratio [expr [$disk set rbw] / [$disk set wbw]]

	foreach element [$inputq set _list] {
		#delete $element
	}
	$inputq set space 0
	$inputq set count 0

	$app insertd $merge_cycles $node
	$app ioread [expr $totalsize * $ratio] $disk
	$app inserts "$self attach [new MRPerf/MergeFile $totalsize]"
}

MRPerf/ReduceTask instproc do-local-fs-merge {app} {
	global io_factor
	set q2 [$self set local_fs_queue]
	if {[$q2 count] >= 2*$io_factor-1} {
		$app inserts "$self local-fs-merge $app"
	}
}

MRPerf/ReduceTask instproc dump {queue} {
	if {$queue == "q1"} {
		set queue in_mem_queue
	} elseif {$queue == "q2"} {
		set queue local_fs_queue
	}
	set q [$self set $queue]
	puts "$self->$queue: [$q count]"
}

MRPerf/ReduceTask instproc in-mem-merge {app} {
	set q1 [$self set in_mem_queue]
	set q2 [$self set local_fs_queue]
	if {[$q1 set count] < 1} {
		return
	}
	#$app inserts "$app getget \"merge1(rtask=$self)q1\" $q1 count"
	#$app inserts "$app getget \"merge1(rtask=$self)q2\" $q2 count"
	$self set in_mem_queue [new MRPerf/Queue]
	$app inserts "$q2 merge $q1 $app [$self worker]"
	$app inserts "delete $q1"
	#set q1 [$self set in_mem_queue]
	#$app inserts "$app getget \"done 1(rtask=$self)q1\" $q1 count"
	#$app inserts "$app getget \"done 1(rtask=$self)q2\" $q2 count"
	#set q2 [$self set local_fs_queue]
	#$app inserts "$app getget \"d1  l3(rtask=$self)q2\" $q2 count"
}

MRPerf/ReduceTask instproc local-fs-merge {app} {
	global io_factor
	set q2 [$self set local_fs_queue]
	#$self dump q1
	set count [$q2 count]
	if {$count < 2} {
		return
	}
	if {$count < 2*$io_factor-1} {
		set n $count
		if {$count < $io_factor} {
			set n1 $count
		} else {
			set n1 $io_factor
		}
	} else {
		set n [expr 2*$io_factor-1]
		set n1 $io_factor
	}
	set q3 [new MRPerf/Queue]
	$app inserts "$q2 split-first $n $q3"
	set pass [new MRPerf/Queue]
	$app inserts "$q3 split-first $n1 $pass"
	$app inserts "$pass read-into-memory $app [$self worker]"
	if {$n > $n1} {
		# if merge does not finish in only one pass, need a second pass
		$app inserts "$q3 merge $pass $app [$self worker]"
		$app inserts "$q3 read-into-memory $app [$self worker]"
		$app inserts "$q2 merge $q3 $app [$self worker]"
	} else {
		$app inserts "$q2 merge $pass $app [$self worker]"
	}
	delete $pass
	delete $q3
}

MRPerf/ReduceTask instproc final-merge {app} {
	set q2 [$self set local_fs_queue]
	set q1 [$self set in_mem_queue]

	# TODO: now this is what Hadoop does. It can be improved since in mem
	# segments need not be written to disk before all files are merged.
	# A better way to do final merge is to keep in mem segments there, and
	# read in all on disk files, and do a merge on them together.
	$app inserts "$self in-mem-merge $app"
	#$app inserts "$self local-fs-merge $app"
}

MRPerf/NodeApp instproc reduce-merge-sort {rcopier} {
	#global reduce_sort_cycles
	global in_mem_space in_mem_segments
	#puts $rcopier
	set rtask [$rcopier set rtask]
	set size [$rcopier set size]
	#puts "reduce sort $rtask"

	set q1 [$rtask set in_mem_queue]
	$q1 attach $rcopier
	if {[$q1 total-space] >= $in_mem_space || [$q1 count] >= $in_mem_segments} {
		$self inserts "$rtask in-mem-merge $self"
		#$self inserts "$rtask do-local-fs-merge $self"
	}
	#puts $size
	#$self inserts "$rtask getget {before add} sort_done_mappers"
	$self inserts "$rtask addadd sort_done_mappers"
	#puts "$rcopier, [$rcopier set maptask]"
	#$self inserts "$rtask getget {after add} sort_done_mappers"
}

MRPerf/NodeApp instproc hdfs-output {rtask size} {
	#puts "hdfs-output $rtask $size"
	#puts "only implemented 1 replica (only save on local disk)"

	set num_of_replicas 1
	#global num_of_replicas
	if {$num_of_replicas == 1} {
		set n [$rtask worker]
		set disk [$n choosedisk]
		#$self insertd [expr 1.0*$size * [$disk set rbw] / [$disk set wbw]] $disk
		$self iowrite $size $disk
	}
}

MRPerf/NodeApp instproc is-sort-finished {rtask} {
	global num_chunks reduce_sort_cycles
	#global ns
	#puts "[$ns now]:[$rtask set sort_done_mappers], $num_chunks"
	if {[$rtask set sort_done_mappers] == $num_chunks } {
		$rtask final-merge $self
		$self insertd $reduce_sort_cycles [$rtask worker]
		$self inserts "$rtask add-counter sort_finished"
		$self out1 "$rtask on [$rtask worker] === sort finished"

		set output_size [$self reduce $rtask]
		$rtask set output_size $output_size
		$self hdfs-output $rtask $output_size
		$self inserts "[$self set parent] snd \"reduce finish $rtask\""
	}
}

MRPerf/ReduceTask instproc fail {} {
	global ns stats no_reducetasks_to_start started_reducers
	puts "[$ns now]: reduce $self fail"
	puts $stats "ReduceAttempt TASKID=\"$self\" TASK_STATUS=\"KILLED\" FINISH_TIME=\"[expr [$ns now]*1000]\" HOSTNAME=\"[[$self worker] hostname]\""

	if {[$self info vars alive_timer] != ""} {
		$ns cancel [$self set alive_timer]
	}
	$ns cancel [[$self set expire_timer] set eid]
	incr no_reducetasks_to_start
	set nrr [[$self worker] set running_reducetasks]
	[$self worker] set running_reducetasks [expr $nrr-1]

	#puts $started_reducers
	lremove started_reducers [$self set app]

}

MRPerf/NodeApp instproc start_reducetask { node } {
	global no_copiers stats max_reducers num_of_nodes timers
	if {[$node set running_reducetasks] >= $max_reducers} {
		#puts "$node already has [$node set running_reducetasks] reduce tasks running!"
		return 0
	}


	set taskstr [new MRPerf/ReduceTask]
	$taskstr set counters [new MRPerf/Empty]
	$taskstr set input_size 0
	$taskstr set output_size 0
	$taskstr set shfl_done_mappers [list]
	$taskstr set sort_done_mappers 0
	$taskstr set mchain [new MRPerf/Thread/MultiChain $no_copiers]
	#$taskstr set mchain [new MRPerf/Thread/MultiChain $num_of_nodes]
	$taskstr set in_mem_queue [new MRPerf/Queue]
	$taskstr set local_fs_queue [new MRPerf/Queue]
	$taskstr set copier_count 0
	set result [$taskstr schedule $node]
	if {$result != "" } {
		set app2 [$self new-connection $node]
		$app2 snd "reduce task $taskstr"
		puts $stats "Task TASKID=\"$taskstr\" TASK_TYPE=\"REDUCE\" START_TIME=\"[$self now]\" SPLITS=\"\""
		$node set running_reducetasks [expr [$node set running_reducetasks] + 1]
		$taskstr set expire_timer [new MRPerf/Timer $timers(task_dead) "$taskstr fail"]

		upvar #0 no_reducetasks_to_start r
		set r [expr $r-1]
		#puts "reduce tasks to start $r"
		return 1
	}
	return 0
}

MRPerf/ReduceTask instproc shuffle-finish {map app} {
	global ns num_chunks started_reducers
	#puts "[$ns now]: $self reduce copier finish"

	if {[lsearch $started_reducers [$self set app]] == -1} {
		# this reducer has got all intermediate data it needs.
		# extra "reduce data reply" message may be caused by
		# ghost map tasks.
		puts "[$ns now]: ignore reduce data reply message"
		return
	}

	#puts $rcopier
	set l [$self set shfl_done_mappers]
	if {[lsearch $l $map] == -1} {
		lappend l $map
		#puts "added"
	}
	$self set shfl_done_mappers $l

	if {[llength $l] > $num_chunks} {
		puts "error 1"
	} elseif {[llength $l] == $num_chunks} {
		$app inserts "$self add-counter shuffle_finished"
		$app out1 "$self on [$self worker] === shuffle finished"

		lremove started_reducers [$self set app]
		$self unset shfl_done_mappers
	}
}

MRPerf/ReduceTask instproc fetch_map_output {maptask app} {
	global num_of_reducers ns

	# put shuffles in a chain, keep 5 on the fly.
	set part_size [expr [$maptask set output_size]*1.0 / $num_of_reducers]
	set copier [new MRPerf/ReduceCopier $maptask $self $part_size $app]

	set c [new MRPerf/Empty]
	[$self set counters] set copiers([$self set copier_count]) $c
	$copier set count [$self set copier_count]
	$self set copier_count [expr [$self set copier_count] + 1]
	#$app inserts "$self add1-counter $c copier_scheduled"
	$app inserts "[$self set mchain] attach $copier"
	#$app inserts "puts [[$self set mchain] size]"
}

