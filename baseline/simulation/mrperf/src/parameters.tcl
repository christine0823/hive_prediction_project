
set jvm_start_cost [expr 4.0*1000*1000*1000]
set wrap_up_cost [expr 4.8*1000*1000*1000]
set heart_beat_delay 1
set tasks_to_start 2
	# number of tasks to start at one heartbeat
set finish_time 5000.0
set io_factor 10
set in_mem_space [expr 100.0*1024*1024 * 0.66]  ;# 100MB*0.66
set in_mem_segments 100

set read_seek 0;#0.0082
set write_seek 0;#0.0092

set timers(alive) 30
set timers(task_dead) 600
set timers(ghost_map) 189
set timers(data_req) 189

#mappers
set cycles_per_byte 20.0
	# in cycles per byte, 1G cycles per 1GB
set sort_cycles_per_byte 44.0
set merge_cycles 1.0*1000*1000*1000
set dist_cache_size 1.0*1024*1024

#reducers
set no_copiers $num_of_nodes
#set no_copiers 5
set reduce_sort_cycles 6.0*1000*1000*1000
set reduce_cycles_per_byte 90.0

