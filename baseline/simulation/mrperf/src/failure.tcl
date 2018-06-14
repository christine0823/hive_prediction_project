

set ns [new Simulator]
source common.tcl

source io.tcl
source timer.tcl
source map.tcl
source reduce.tcl
source shuffle.tcl

# open trace files and enable tracing
set nf [open $namfile w]
#$ns namtrace-all $nf
set f [open $tracefile w]
#$ns trace-all $f

set stats [open $statsfile w]

source common-schedule.tcl
source schedule.tcl
source common-topology.tcl
puts begin



source hadoop.topo.tcl
puts "topology created"


set sched [new MRPerf/Scheduler]
set num_chunks [$sched read-metadata "random.xml"]

#puts "$jt $nn"
puts "scheduler created"


source hadoop.job.tcl




set finished_maptasks [list]
set started_reducers [list]

set no_maptasks_to_start $num_chunks
set no_reducetasks_to_start $num_of_reducers
set uncounted 0

set tcp0 [new Agent/TCP/FullTcp]
set dummy [new MRPerf/NodeApp $tcp0]
$dummy set hnode $jt
set app1 [$dummy new-connection $nn]



puts "NN and JT created"



puts $stats "Job JOBID=\"job_sim_111\" JOBNAME=\"TeraSort-sim\" USER=\"mrperf\" SUBMIT_TIME=\"[$ns now]\" JOBCONF=\"job.xml\""
puts $stats "Job JOBID=\"job_sim_111\" LAUNCH_TIME=\"[$ns now]\" TOTAL_MAPS=\"$num_chunks\" TOTAL_REDUCES=\"$num_of_reducers\""

# send a message via MRPerf/NodeApp
# The string will be interpreted by the receiver as Tcl code.
$ns at 0.01 "$app1 snd {FS request}"
[$nn set nsnode] label NN
[$jt set nsnode] label JT


$ns set-animation-rate 0.5ms
$ns at 0.2 "$ns set-animation-rate 1ms"
$ns at 0.5 "$ns set-animation-rate 2ms"

proc map_fail {} {
	global ns n_rg0_0_ng0_0
	$ns at 10 "$n_rg0_0_ng0_0 set next_task_fail 1"
	#$ns at 5 "$n_rg0_0_ng0_2 set next_task_passive_fail 1"
}

proc reduce_fail {} {
	global n_rg0_0_ng0_0
	$n_rg0_0_ng0_0 set next_reduce_task_fail 1
}

proc node_fail {} {
	global ns n_rg0_0_ng0_1 r_rg0_0
	[$ns link [$n_rg0_0_ng0_1 set nsnode] $r_rg0_0] dynamic
	$ns at 20 "[$ns link [$n_rg0_0_ng0_1 set nsnode] $r_rg0_0] down"
}

proc rack_fail {} {
	global ns r_rg0_0 r1
	[$ns link $r_rg0_0 $r1] dynamic
	$ns at 15 "[$ns link $r_rg0_0 $r1] down"
}

proc no_fail {} {
}

source "failure-command.tcl"

foreach i {1 2 3 4 5 6 7 8 9 10} {
	$ns at [expr 1440+$i] "puts [expr 1440+$i]:"
}

$ns at $finish_time "finish"

$ns run

