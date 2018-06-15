import numpy as np
import csv
import sys

import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument("--i")
parser.add_argument("--d")
parser.add_argument("--n")
parser.add_argument("--l")
parser.add_argument("--o")
args = parser.parse_args()

input_file = args.i
output_file = args.o
dataset = int(args.d)
job = int(args.n)
length=int(args.l)

GHz = (2.93*1000000000.0)*2
# MapTime MapBytes 
# ReduceTime ReduceBytes
# ShuffleBytes
# Mergetime
# Shuffletime

output = open(output_file, 'w')

def read_file(input_file):
        f = open(input_file, 'rb')
        n = 0
        for row in csv.reader(f):
                row = [float(i) if i else 0 for i in row]
                chunkCount = int(row[0])
                mapCycles = GHz/(row[1]*1024*1024)
                if row[2] > 0:
			reduceCycles = GHz/(row[2]*1024*1024)
		else:
			reduceCycles = 0.0000000001

                mergeCycles = (row[4]/1000.0)*2.93*2
		
		if  mergeCycles == 0:
			 mergeCycles = 0.0000000001
                shuffleCycles = ((row[5]/1000.0)*GHz) / (row[3])
		
		if  shuffleCycles == 0:
                         shuffleCycles = 0.0000000001
                n = n+1
  
		if n == (dataset-1)*length + job:
			# Number of mapper
			print chunkCount
			output.write("set cycles_per_byte "+str(mapCycles)+"\n")
			output.write("set sort_cycles_per_byte "+str(shuffleCycles)+"\n")
			output.write("set merge_cycles "+str(mergeCycles)+"*1000*1000*1000\n")
			output.write("set reduce_sort_cycles "+str(mergeCycles)+"*6.0*1000*1000*1000\n")
			output.write("set reduce_cycles_per_byte "+str(reduceCycles)+"\n")
			output.close()
	f.close()
        

# TOTAL_LAUNCHED_MAPS, MB_MILLIS_MAPS, MB_MILLIS_REDUCES, FILE_BYTES_WRITTEN, avgMergeTime, avgShuffleTime
read_file(input_file)


