import numpy as np
import math
import sklearn
from sklearn.linear_model import LinearRegression
import csv
from sklearn.svm import SVR

DISK_READ = 3481.6*1024*1024
DISK_WRITE = 966.7*1024*1024
HDFS_WRITE = 70*1024*1024 
MAP_LOCAL_RATIO = 0.33
MAP_SPLIT_SIZE = 128*1024*1024
NETWORK=67*1024*1024
MAP_MAXIMUM=2*3
REDUCE_MAXIMUM=2*3 

lm_set = dict()

def LinearRegression_JobType():
	types = ["Deux" ,"TableScan", "Group", "Join", "Select", "None"]
	for t in types:
		print t
		# InputRecords, Time 
		fin = open("testtypes/"+str(t)+".csv",'r');
		X = []
		y = []
		for row in csv.reader(fin):
			if row[0] != "null" and row[1] != "null":
				X.append(float(row[1]))
				y.append(float(row[2])/1000.0)	
		
		lm = LinearRegression(normalize=True)
                #lm = SVR(C=1.0, epsilon=0.8, degree = 1)
		model = lm.fit(np.array(X).reshape(-1, 1),y)
                print lm.score(np.array(X).reshape(-1, 1),y)
		lm_set[t] = model
		X = np.array(X).reshape(-1, 1)

def Map_Ops(JobType, TotalRecords):
	model = lm_set[JobType]
	
	return model.predict(np.array([TotalRecords]).reshape(1,-1))

def Reduce_Ops(JobType, TotalRecords):
	model = lm_set[JobType]
	
        return model.predict(np.array([TotalRecords]).reshape(1,-1))

# MapInputRecords, ReduceInputRecords, MapOutputRecords, MapOutputBytes, RecuceOutputRecords, ReduceOutputBytes, Reducer, MapType, ReduceType
def SingleJobCost(mipt, ript, mtr, mb, rtr, rb, reducer, mapType, reduceType):
        
	#### Output Job Type #####
	Map_JobType = mapType
	Reduce_JobType = reduceType

	#### Output information#####
	Map_TotalRecords = mtr
        mab = mb / mtr    
	Map_AverageBytes = mab
	Reduce_TotalRecords = rtr
        if rtr > 0:
		rab = rb / rtr
        else:
		rab = 0.0
	Reduce_AverageBytes = rab
	Map_TotalBytes = Map_TotalRecords*Map_AverageBytes
	Number_of_Mapper = Map_TotalBytes / MAP_SPLIT_SIZE
	Number_of_Reducer = reducer

	####### Map ###########
	Cost_Map_Read = MAP_LOCAL_RATIO * (MAP_SPLIT_SIZE / DISK_READ) + (1 - MAP_LOCAL_RATIO) * (MAP_SPLIT_SIZE / NETWORK)
	Cost_Map_Ops = Map_Ops(Map_JobType, mipt)

	Cost_Map = Cost_Map_Read + Cost_Map_Ops
	####### Map Spill ##########
	Cost_Spill = Map_TotalBytes / DISK_WRITE
	####### Map Merge ##########
	Cost_M_Merge = Map_TotalBytes / DISK_READ + Map_TotalBytes / DISK_WRITE	
	####### M ##########
	# max in n input tables
	Cost_M = Cost_Map + Cost_Spill + Cost_M_Merge 
	
	####### Shuffle ##########
	if Number_of_Reducer > 0:
        	Seg_Size = Map_TotalBytes * Number_of_Mapper / Number_of_Reducer
        else:
		Seg_Size = 0.0
	Cost_Shuffle = Seg_Size / NETWORK
	####### Reduce Merge ##########
	Cost_R_Merge = Seg_Size / DISK_READ + Seg_Size / DISK_WRITE 

	####### Reduce ###########
	Cost_Reduce_Ops = Reduce_Ops(Reduce_JobType, ript)
	Cost_Reduce = Cost_Reduce_Ops + Reduce_AverageBytes*Reduce_TotalRecords / HDFS_WRITE

	###### Total Cost ########
	Pm = math.ceil(Number_of_Mapper/MAP_MAXIMUM)
	Pr = math.ceil(Number_of_Reducer/REDUCE_MAXIMUM)
	
        if Number_of_Reducer > 0:
        	Total_Cost =  Pm*Cost_M + Pr*(Cost_Shuffle + Cost_R_Merge + Cost_Reduce)
        else:
               Total_Cost =  Pm*Cost_M
	
	return Total_Cost

LinearRegression_JobType()

# Record each dag in csv files
fin = open("dags/dag1.csv",'r');

# MAP_INPUT_RECORDS, REDUCE_INPUT_RECORDS, MAP_OUTPUT_RECORDS, MAP_OUTPUT_BYTES, RECORDS_OUT_0.reduce, HDFS_BYTES_WRITTEN.reduce
Time = []
cnt = 0
for row in csv.reader(fin):
	types = row[0].split('_')
        print types
        reducer = float(row[1])
        #reducer = 1
        row = row[2:]
        print row
	row2 = [float(r) for r in row]
        
        Time.extend(SingleJobCost(row2[0], row2[1], row2[2], row2[3], row2[4], row2[5],reducer, types[0],types[1]))

print len(Time)		
start = 0
jobLen = 10
for scale in range(4):
	times = Time[start:start+jobLen]
	start = start + jobLen
        print times
	# Adjust workflow equation 
	# Example for DAG1 of TPC-H Q2	
	t1 = max(times[3]+times[4], times[6]+times[7]+times[8]+times[9])
	t2 = max(times[0], t1 + times[5])
	total = t2 + times[1]+times[2]
	print total
