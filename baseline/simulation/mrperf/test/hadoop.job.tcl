
set avg_record_size 100
	# in byte.
	# not in use --Guanying 2008.1.11
#set jt $n_rg0_0_ng0_1

source parameters_test.tcl

# mappers
set max_mappers 6
	# per node
set start_sort_when_buffer 1
set buffer_size [expr 4096*1024*1024]
set filter_ratio [new RandomVariable/Uniform]
$filter_ratio set min_ 0
$filter_ratio set max_ 0.01

# reducers
set max_reducers 1
	# concurrent reducers per node.
#set num_of_reducers [expr $max_reducers*$num_of_nodes]
set num_of_reducers 1
	# total reducers to start
# on the above two parameters, if num_of_reducers is larger than max_reducers
# times number of nodes, then some reducers are started first, and other
# reducers are not started until some reducers finishes.
set reduce_filter_ratio [new RandomVariable/Uniform]
$reduce_filter_ratio set min_ 0.2
$reduce_filter_ratio set max_ 0.3

