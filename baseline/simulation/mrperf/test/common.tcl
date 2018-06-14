

# wanggy 2008.7.3
# ----------------------

# This is an adapted tcl file from tcpapp.tcl in ns-2. I use this file because
# Application level data can be transferred on top of tcp. A simple protocol
# runs here and needs the ability.
# 
# Here a class MRPerf/NodeApp is defined. in C++ code (webcache/tcpapp.[cc|h]),
# MRPerf/Node and MRPerf/Scheduler are defined and mapped to tcl. MRPerf/Chunk
# and MRPerf/DataLayout are not mapped to tcl. a chunk is referred to by a
# string in tcl, and looked up in C++.
# 
# A MRPerf/Node (hnode) is a wrapper object for ns-2 node, and can save some
# useful information for the node. A MRPerf/NodeApp is one end of a connection
# between two nodes. A connection is created by new-connection(), and two
# MRPerf/NodeApp objects are created as two ends. Most operations are
# MRPerf/NodeApp oriented, in the sense that as long as App is referred to,
# everything can be found.
# 
# One scheduler (singleton) is used in the code. When it is constructed,
# metadata.xml is parsed by DataLayout singleton. Tcl cannot see DataLayout,
# and performs all operations on DataLayout through Scheduler.


Class MRPerf/NodeApp -superclass {Application/TcpApp}
Class MRPerf/LoopApp -superclass {MRPerf/NodeApp}
Class MRPerf/Empty

# wanggy 2008.11.26
# ------------------------------
# Chain class is an abstraction of a series of tasks to be run serially.  The
# head of a Chain is the currently running task.  Other tasks in a Chain will
# be run after the first (head) task finishes.  That's how a thread works.
# However, Chain/TaskList is more like an event model.  An event happens,
# optionally lasts for some time, and then next event is scheduled.
#
# Two kinds of tasks are available: simple task and device task.  A simple task
# does not work on devices (cpu/disk), which is usually sending a network
# message.  A simple task is inserted in to a Chain, and when it becomes the
# head of the Chain, it is executed, and Chain will immediately move on to the
# next task.  A device task is an operation on a device (cpu/disk), which will
# take some time.  It is also inserted into a Chain, and when it becomes head
# of the Chain, it is put into a TaskList.  When TaskList determines it
# finishes, the task is done, and the Chain moves on to the next task.
#
# A TaskList shares available resources among all concurrently running tasks.
# Every time a task finishes, or a task is inserted, TaskList do a recalculate,
# to find out which task will finish next, and schedule a wake-up at that time.
# The same process of recalculation goes on again then.

# wanggy 2009.1.5
# the above comment (2008.11.26) was on an implementation in tcl. Now this
# is moved to C++.

set g_use_thread 1
if {$g_use_thread} {
	puts "using thread"
	Class MRPerf/Chain -superclass {MRPerf/Thread/Chain}
	Class MRPerf/TaskList -superclass {MRPerf/Thread/TaskList}
	Class MRPerf/Task -superclass {MRPerf/Thread/Task}

	set epsilon 10000

}

MRPerf/NodeApp instproc out {text} {
	puts "[$self now]: $text"
}

MRPerf/NodeApp instproc out1 {text} {
	$self inserts "$self out {$text}"
}

#source io.tcl

proc finish {} {
	global ns namfile stats total_time
	global nf f
	$ns flush-trace
	close $nf
	close $f
	close $stats

	if {$total_time == "0"} {
		puts stderr "not finished till [$ns now]"
	} else {
		puts stderr "Total runtime: $total_time"
	}

	#puts "running nam..."
	#exec nam $namfile &
	exit 0
}


MRPerf/NodeApp instproc now {} {
	global ns
	return [string range [expr ([$ns now] + [$self set time]) * 1000] 0 10]
}

MRPerf/NodeApp instproc at {delay args} {
	global ns
	$self instvar time

	#set t [$self set time]

	$self set time [expr [$self set time] + $delay]
	set later [expr [$ns now] + [$self set time]]

	#puts "$self: $t + $delay = [$self set time] ($later)"

	$ns at $later "eval $args"
}

MRPerf/NodeApp instproc dummy {} {
}

MRPerf/ReduceTask instproc getget {prefix name} {
	global ns
	puts "[$ns now]: $prefix $self [$self set $name]"
}

MRPerf/ReduceTask instproc addadd {name} {
	$self set $name [expr [$self set $name] + 1]
}

MRPerf/NodeApp instproc getget {prefix var name} {
	puts "[$self now]: $prefix $var [$var set $name]"
}

#source map.tcl
#source reduce.tcl

MRPerf/NodeApp instproc dump {} {
	set node [$self set hnode]
	set name [$node nodename]
	set rem  [[[$self dst] set hnode] nodename]
	return "$rem ([$self dst]) -> $name ($self)"
}

MRPerf/LoopApp instproc connect {rapp} {
	$self instvar dst
	$self set dst $rapp
	$rapp set dst $self
}

MRPerf/LoopApp instproc dst {} {
	return [$self set dst]
}

MRPerf/LoopApp instproc init {} {
}

MRPerf/LoopApp instproc send {length msg} {
	eval $msg
}

MRPerf/NodeApp instproc snd {msg} {
	$self send 100 "[$self dst] recv {$msg}"
}

MRPerf/NodeApp instproc shuffle_send_heartbeat {} {
	global ns timers
	$self snd "shuffle heartbeat"
	#puts "[$ns now]: $self sending heartbeat"
	$self set shuffle_heartbeat_event [$ns after $timers(alive) "$self shuffle_send_heartbeat"]
	#puts "[$ns now]: $self heartbeat"
}

MRPerf/NodeApp instproc send_heartbeat {} {
	global ns heart_beat_delay
	$self snd "heartbeat"
	#puts "[$ns now]: $self sending heartbeat"
	$ns after $heart_beat_delay "$self send_heartbeat"
	#puts "[$ns now]: $self heartbeat"
}

MRPerf/NodeApp instproc new-connection rhnode {
	global ns

	if { [$self set hnode] == $rhnode } {
		set loop0 [new MRPerf/LoopApp]
		set loop1 [new MRPerf/LoopApp]
		$loop0 set hnode $rhnode
		$loop1 set hnode $rhnode
		$loop0 set time 0
		$loop1 set time 0
		$loop0 set chain [new MRPerf/Chain]
		$loop1 set chain [new MRPerf/Chain]
		$loop0 connect $loop1

		$loop0 set parent $self
		return $loop0
	}

	set tcp2 [new Agent/TCP/FullTcp]
	set tcp3 [new Agent/TCP/FullTcp]
	set local [[$self set hnode] set nsnode]
	set remote [$rhnode set nsnode]
	$ns attach-agent $local $tcp2
	$ns attach-agent $remote $tcp3
	$ns connect $tcp2 $tcp3
	$tcp3 listen

	set app2 [new MRPerf/NodeApp $tcp2]
	set app3 [new MRPerf/NodeApp $tcp3]
	$app2 set hnode [$self set hnode]
	$app3 set hnode $rhnode
	$app2 set time 0
	$app3 set time 0
	$app2 set chain [new MRPerf/Chain]
	$app3 set chain [new MRPerf/Chain]
	$app2 set tcp $tcp2
	$app3 set tcp $tcp3

	# parent is the connection that creates this new one.
	# when this connection finishes, its parent is the way to go back.
	$app2 set parent $self
	$app2 connect $app3

	return $app2
}

if {0} {
proc connclose {app} {
	set remote [$app dst]
	delete [$app set chain]
	delete [$remote set chain]
	if { [$app set hnode] != [$remote set hnode] } {
		#delete [$app set tcp]
		#delete [$remote set tcp]
	}
	delete $app
	delete $remote
}

MRPerf/NodeApp instproc des1troy {} {
	#puts "destroy $self [$self dst]"
	set task [new MRPerf/Thread/Task]
	$task conf 2 "ns after 0.1 \"connclose $self\"" 0
	[$self set chain] insert $task
}
}

MRPerf/NodeApp instproc nsnode {} {
	return [[$self set hnode] set nsnode]
}

#source timer.tcl
#source shuffle.tcl

proc lremove {alist toremove} {
	upvar $alist lst
	#puts "to remove $toremove from \[$lst\]"
	set index [lsearch $lst $toremove]
	if {$index >= 0} {
		#puts "did remove"
		set lst [lreplace $lst $index $index]
	}
	#puts $lst
	#return $alist
}

MRPerf/NodeApp instproc recv {data} {
	$self instvar parent
	global ns n1 n sched max_mappers stats buffer_size
	global total_time max_reducers num_chunks
	global num_of_reducers
	global heart_beat_delay max_mappers max_reducers tasks_to_start
	global no_maptasks_to_start no_reducetasks_to_start
	global finished_maptasks started_reducers done_reducers
	global dist_cache_size
	global timers

	set thisnode [$self set hnode]
	set remotenode [[$self dst] set hnode]
	$ns trace-annotate "[$thisnode nodename] received data \"$data\" from [$remotenode nodename]"
	#$self out1 "$self ([$self set hnode]) recv from [$self dst] ([[$self dst] set hnode]) \"$data\""

	# 'at' timer reset
	$self set time 0

	if {[string compare $data "FS request"] == 0} {
		# Namenode receives
		[$self nsnode] color cyan
		$self inserts "$self snd \"FS reply\""

	} elseif {[string compare $data "FS reply"] == 0} {
		# Job Tracker receives
		[$self nsnode] color tan

		#set no_maptasks_to_start $num_chunks
		#set no_reducetasks_to_start $num_of_reducers

		set done_reducers 0

	} elseif {[string first "heartbeat" $data] == 0} {
		# Job Tracker receives
		set remote_node [[$self dst] set hnode]

		set once $tasks_to_start
		set min $once

		#$self out1 "$remote_node map: $once $no_maptasks_to_start"
		if {$min > $no_maptasks_to_start} {
			set min $no_maptasks_to_start
		}
		if {$min > 0} {
			#$self out1 "start $min map tasks on heartbeat"
		}
		for {set i 0} {$i < $min} {incr i} {
			incr once [expr -[$self start_maptask $remote_node]]
		}
		#set once [expr $once - $min]
		set min $once
		#set no_maptasks_to_start [expr $no_maptasks_to_start - $min]

		#$self out1 "$remote_node reduce: $min $no_reducetasks_to_start"
		if {$min > $no_reducetasks_to_start} {
			set min $no_reducetasks_to_start
		}
		for {set i 0} {$i < $min} {incr i} {
			incr once [expr -[$self start_reducetask $remote_node]]
		}
		#set no_reducetasks_to_start [expr $no_reducetasks_to_start - $min]
		#puts $once

		$self inserts "$self snd \"hb reply\""

#	} elseif {[string first "hb reply" $data] == 0} {
		# data nodes receive
#		$ns after $heart_beat_delay "$self snd \"heartbeat\""

	} elseif {[string first "alive" $data] == 0} {
		set task [string range $data 6 end]
		# task could be either map or reduce
		[$task set expire_timer] reset

		if {[$task info vars mchain] != ""} {
			puts "[$self now]: alive from reduce $task"
		} else {
			puts "[$self now]: alive from map $task"
		}

	} elseif {[string first "map task" $data] == 0} {
		# mappers receive. Note that one node can have multiple mappers
		set task [string range $data 9 end]
		puts $stats "MapAttempt TASKID=\"$task\" TASK_ATTEMPT_ID=\"$self\" START_TIME=\"[$self now]\" HOSTNAME=\"[[$task worker] hostname]\""
		puts "[$self now]: $task map task start [$task chunk] [$task worker]"
		$self set maptask $task

		$task set alive_timer [$ns after $timers(alive) "$self send_alive $task"]

		set node [$self set hnode]

		if {[$node info vars next_task_fail] != ""} {
			puts "$task is set to fail"
			$node unset next_task_fail
			$task set to_fail 1
		} elseif {[$node info vars next_task_passive_fail] != ""} {
			puts "$task is set to passively fail"
			$node unset next_task_passive_fail
			$task set to_passive_fail 1
		}

		#puts "map task started on $node"
		#$self inserts "$task add-counter init"
		$self jvm-start $task
		$self inserts "$task add-counter map_start"

		set chunkstr [$task chunk]
		set alist [split $chunkstr ":"]
		set length [lindex $alist 3]
		$task set input_size $length


		#puts "[[$task disk] host] [$task worker]"
		if { [[$task disk] host] == [$task worker] } {
			[$self nsnode] color green
			global filter_ratio

			for {set remain $length} {$remain > 0} {} {
				set offset [expr $length-$remain]

				set fr [$filter_ratio value]
				set input_size [expr { $remain > $buffer_size/$fr ? $buffer_size/$fr : $remain}]
				set output_size [expr $input_size * $fr]

				$self readsize $task $offset $input_size
				$self compute $task $offset $input_size
				$self inserts "$task add-counter map_finish"
				$self spill $task $output_size
				set remain [expr $remain - $input_size]
			}
			if {[$task set spill] > 1} {
				$self merge $task
			}
			$self inserts "$self snd \"map finish $task\""
		} else {
			# wanggy 2009.6.9
			# Problem: if the data node has already failed, the
			# scheduler will not know the failure, and still
			# schedule a rack-local or rack-remote task to get
			# data from that data node. That map task will
			# never finish, but because it sends out keep-alive
			# it's never killed, and will run forever.
			# ------------------
			# possible work around: add a data_req_timer=189
			# This is still not correct. The current implementation
			# requires whole data reply by 189s. If due to slow
			# network, data reply is started but not finished by
			# 189s, the task will fail. But the correct behavior
			# is to wait for the task to finish, as long as the
			# request reaches data node. TCP is another layer.
			# -----------------
			# Preferably, send function will return an error,
			# after 189s, to the sender. That can be an event.

			# TODO: what if data node fails, and "data request"
			# never comes back. Scheduler should know about
			# which nodes have failed, and avoid scheduling
			# to those nodes.
			# TODO What about inter-rack link failure?

			#puts [$task chunk]
			#puts "[[$task disk] host] [$task worker]"
			[$self nsnode] color red
			global filter_ratio
			set fr [$filter_ratio value]
			set size [expr { $length > $buffer_size/$fr ? $buffer_size/$fr : $length}]

			set datanode [[$task disk] host]
			set app4 [$self new-connection $datanode]
			$app4 set fr $fr
			#$task set data_req_timer [$ns after $timers(data_req) "$task fail"]
			$app4 set task $task
			$task set connection $app4
			$self inserts "$app4 snd \"data request $task 0 $size\""
			#set app5 [$app4 dst]
			#$app4 send 100 "[$app4 dst] recv {data request $task}"
		}

	} elseif {[string first "data request" $data] == 0} {
		# Data nodes receive. In hadoop it should be Task Tracker that
		# receives this message. But here it's a temporary NodeApp.
		[$self nsnode] color blue
		set alist [split $data]

		set task [lindex $alist 2]
		set offset [lindex $alist 3]
		set size [lindex $alist 4]

		set chunkstr [$task chunk]
		set alist [split $chunkstr ":"]
		set length [lindex $alist 3]

		if { [$self set hnode] == [[$task disk] host] } {
			#$self enqueue

			$self readsize $task $offset $size
			$self inserts "$self send $size \"[$self dst] recv {data reply $task $offset $size}\""
		} else {
			## error!
			puts [[$self set hnode] nodename]
			puts "Error! data requested not on this node"
			$ns trace-annotate "Error! data requested not on this node"
		}

	} elseif {[string first "data reply" $data] == 0} {
		# mappers receive
		[$self nsnode] color green
		set alist [split $data]

		set task [lindex $alist 2]
		set offset [lindex $alist 3]
		set size [lindex $alist 4]
		set output_size [expr $size * [$self set fr]]

		set chunkstr [$task chunk]
		set alist [split $chunkstr ":"]
		set length [lindex $alist 3]

		$self compute $task $offset $size
		$self inserts "$task add-counter map_finish"

		$self spill $task $output_size

		if {[expr $offset + $size >= $length]} {
			if {[$task set spill] > 1} {
				$self merge $task
			}

			set app6 [$self set parent]
			$self inserts "$app6 snd \"map finish $task\""
		} else {
			global filter_ratio
			set fr [$filter_ratio value]
			set r [expr $length - $offset]
			set nextsize [expr { $r > $buffer_size/$fr ? $buffer_size/$fr : $r}]
			set nextoffset [expr $offset + $size]
			$self set fr $fr
			$self inserts "$self snd \"data request $task $nextoffset $nextsize\""
		}

	} elseif {[string first "map finish" $data] == 0} {
		# Job Tracker receives
		set task [string range $data 11 end]
		set worker [[$self dst] set hnode]
		if {[$task info vars to_fail] != ""} {
			$task unset to_fail
			$task fail
			return
		} elseif {[$task info vars to_passive_fail] != ""} {
			# TODO: wanggy 2009-6-9
			# this is not implemented yet, since it's not used.
			$task unset to_passive_fail
			return
		}

		puts "[$self now]: $task map finish [$task worker] [$task chunk]"

		$ns cancel [$task set alive_timer]
		$ns cancel [[$task set expire_timer] set eid]
		puts $stats "MapAttempt TASKID=\"$task\" TASK_STATUS=\"SUCCESS\" FINISH_TIME=\"[$self now]\" HOSTNAME=\"[[$task worker] hostname]\""

		set chunkstr [$task chunk]
		set alist [split $chunkstr ":"]
		set filename [lindex $alist 0]
		set chunk [lindex $alist 1]
		$ns trace-annotate "***** Chunk $filename:$chunk finished on [$remotenode nodename] *****"

		$self wrap-up $task

		$task set finish_time [$self now]
		$task write-counters

		$self inserts "$worker set running_maptasks [expr [$worker set running_maptasks] - 1]"

		foreach reduceapp $started_reducers {
			$self inserts "[$reduceapp dst] snd \"map f1inish signal $task\""
			#puts "Job Tracker sent map $task f1inish signal to $reduceapp"
		}
		$task finish
		lappend finished_maptasks $task

		$self inserts "[$self set parent] start_maptask $worker"

	} elseif {[string first "reduce task" $data] == 0} {
		# reducers receive. One node can have multiple reducers.
		set rtask [string range $data 12 end]
		puts $stats "ReduceAttempt TASKID=\"$rtask\" TASK_ATTEMPT_ID=\"$self\" START_TIME=\"[$self now]\" HOSTNAME=\"[[$rtask worker] hostname]\""
		$self out1 "reducer($rtask) started on node([$rtask worker])"

		$self set reducetask $rtask
		$rtask set app $self

		$rtask set alive_timer [$ns after $timers(alive) "$self send_alive $rtask"]

		# potentially increasing counter here is not correct.
		# Another heartbeat may goes to job tracker, even before this counter
		# gets updated.
		set node [$self set hnode]

		if {[$node info vars next_reduce_task_fail] != ""} {
			puts "reduce task $rtask is set to fail"
			$node unset next_reduce_task_fail
			$rtask set to_fail 1
		} elseif {[$node info vars next_reduce_task_passive_fail] != ""} {
			puts "$rtask is set to passively fail"
			$node unset next_reduce_task_passive_fail
			$rtask set to_passive_fail 1
		}

		$self jvm-start $rtask
		$self inserts "$rtask add-counter reduce_start"

		foreach maptask $finished_maptasks {
			$rtask fetch_map_output $maptask $self
		}
		#$self inserts "lappend started_reducers $self"
		lappend started_reducers $self
		#if {[llength $started_reducers] == $num_of_reducers} {
		#	$self inserts "lreplace started_reducers 0 0"
		#}

	} elseif {[string first "map f1inish signal" $data] == 0} {
		# reducers receive
		set alist [split $data]
		set task [lindex $alist 3]
		set rtask [$self set reducetask]

		#puts "reduce task $rtask"
		#puts "map $task f1inish signal to reduce task $rtask received at $self"

		$rtask fetch_map_output $task $self

	} elseif {[string first "ghost map" $data] == 0} {
		set alist [split $data]
		set ghost_map [lindex $alist 2]
		puts "[$self now]: ghost map $ghost_map found by $self"

		$ghost_map mark_ghost

	} elseif {[string first "reduce data request" $data] == 0} {
		# data nodes receive. What is requested is intermediate result,
		# output previously by mappers
		set alist [split $data]
		set rcopier [lindex $alist 3]

		set app20 [$self new-connection $remotenode]
		[$app20 dst] set rcopier $rcopier
		$rcopier set heartbeat_app $app20
		$app20 shuffle_send_heartbeat

		# Guanying 2009.6.12 workaround
		# When output size is small, sometimes [$rcopier set size] can be 
		# less than 1.0, and "$self send" will not do anything, so the other
		# end assume the message is lost and a ghost map is found.
		# workaround: limit size minimum to 10.0. However, the better way to
		# fix the problem is to limit minimum in ns-2 C++ code.
		set size [$rcopier set size]
		if {$size < 10.0} {
			set size 10.0
		}
		#TODO: maybe specify offset instead of 0 here
		$self readsize [$rcopier set maptask] 0 [$rcopier set size]
		$self inserts "$self send $size \"[$self dst] recv {reduce data reply $rcopier}\""

	} elseif {[string first "shuffle heartbeat" $data] == 0} {
		# reduce copiers receive
		set rcopier [$self set rcopier]
		if {[$rcopier set done] == 0} {
			$ns cancel [$rcopier set ghost_map_timer]
			$rcopier set ghost_map_timer [$ns after $timers(ghost_map) "$rcopier mark_ghost"]
		}

	} elseif {[string first "reduce data reply" $data] == 0} {
		# reducers receive
		set alist [split $data]
		set rcopier [lindex $alist 3]
		set rtask [$rcopier set rtask]

		$ns cancel [[$rcopier set heartbeat_app] set shuffle_heartbeat_event]
		$ns cancel [$rcopier set ghost_map_timer]
		# TODO: delete connection
		$rcopier set done 1

		#set c [[$rtask set counters] set copiers([$rcopier set count])]
		#$self inserts "$rtask add1-counter $c copier_finish"

		[$rtask set mchain] next-task
		#$self inserts "puts [[$rtask set mchain] size]"

		$self reduce-merge-sort $rcopier
		#puts "$rcopier, [$rcopier set maptask]"
		$self inserts "$rtask shuffle-finish [$rcopier set maptask] $self"
		$self inserts "$self is-sort-finished $rtask"

	} elseif {[string first "reduce finish" $data] == 0} {
		# Job Tracker receives
		set alist [split $data]
		set rtask [lindex $alist 2]

		set task $rtask
		if {[$task info vars to_fail] != ""} {
			$task unset to_fail
			$task fail
			return
		} elseif {[$task info vars to_passive_fail] != ""} {
			# TODO: wanggy 200-6-9
			# this is not implemented, since it's not used
			$task unset to_passive_fail
			return
		}

		$ns cancel [$rtask set alive_timer]
		$ns cancel [[$task set expire_timer] set eid]

		set c [$rtask set counters]
		puts $stats "ReduceAttempt TASKID=\"$rtask\" TASK_ATTEMPT_ID=\"[$self dst]\" TASK_STATUS=\"SUCCESS\" HOSTNAME=\"[[$rtask worker] hostname]\" SHUFFLE_FINISHED=\"[$c set shuffle_finished]\" SORT_FINISHED=\"[$c set sort_finished]\" FINISH_TIME=\"[$self now]\""
		$rtask write-counters

		$rtask set finish_time [$self now]

		set worker [[$self dst] set hnode]
		$worker set running_reducetasks [expr [$worker set running_reducetasks] - 1]

		set done_reducers [expr $done_reducers + 1]
		$self out1 "($done_reducers / $num_of_reducers) reducers done"

		if {$no_reducetasks_to_start > 0} {
			$self inserts "$self start_reducetask $worker"
		}

		if {$done_reducers > $num_of_reducers} {
			puts "error 2"
		} elseif {$done_reducers == $num_of_reducers} {
			set total_time [$ns now]
			finish

		}

	}

}

set namfile	out.nam
set tracefile	out.tr
set statsfile "stats"



# define color index
$ns color 0 black
$ns color 1 blue
$ns color 2 cyan
$ns color 3 yellow
$ns color 4 brown
$ns color 5 tan
$ns color 6 gold
$ns color 7 red
$ns color 8 purple
$ns color 9 green



set total_time 0


