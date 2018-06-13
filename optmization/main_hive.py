import numpy as np
from label import *
from preprocessing import *
#from train import *
from test import *
from sklearn.externals import joblib
from keras.models import load_model
import math
print "=========Initial========"
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument("--i")
parser.add_argument("--o")
parser.add_argument("--s")
parser.add_argument("--q")
args = parser.parse_args()

input_file = args.i
output_file = args.o
scale = args.s
query = args.q

print "=========Load========"
modelRootDir="../models/"
# Step 1 : read time model
scalerX = joblib.load(modelRootDir+query+'_time.scl.pkl')
clf = load_model(modelRootDir+query+'_time.h5')

# Step 2 : read jobinfo model
scaler_jinfo = joblib.load(modelRootDir+query+'_jobInfo.scl.pkl')
clf_jn = load_model(modelRootDir+query+'_seqLen.h5')
clf_jt = load_model(modelRootDir+query+'_jobInfo.h5')

print "=========Bound========"
bound = []
configs = []
hadoopIdx = []

f = open(input_file,'rb');
cnt = 0
for row in csv.reader(f):
	configs.append(row[0])
	if row[4] == "float":
		if float(row[1]) < float(row[2]):
			bound.append(np.arange(float(row[1]), float(row[2]), float(row[3])))
		else:
			bound.append((float(row[1]), float(row[2])))
	elif row[4] == "int":
		if int(row[3]) == 1: 
			bound.append((int(row[1]), int(row[2])))
		else:
			bound.append(range(int(row[1]), int(row[2])+int(row[3]), int(row[3])))
	else:
		bound.append((int(row[1]), int(row[2])))
	
	# Hive and Hadoop configurations
	if row[5] == "hadoop":
		hadoopIdx.append(cnt)
				
	print cnt,
	print bound[cnt],
	print row[5]
	cnt = cnt + 1
f.close()
#print bound

print "=========Initial========"
RECORDS = dict()
RECORDS[5]=4000000
RECORDS[10]=8000000
RECORDS[25]=20000000
RECORDS[50]=40000000

multiX = [4]
dagIdx = [1,3,5,6,7,8,14,15,16,33,34,35,40]
boolIdx = [3,5,6,7,8,10,11,13,14,15,16,37,38]

from skopt import *

def getPattern(x):
	pattern = [float(RECORDS[int(scale)])]
	for i in range(len(x)):
		if i in multiX:
                        pattern.extend(getBinarylabel(x[i],3))
		elif i in dagIdx:
			pattern.append(x[i])

	pattern = np.array(pattern).reshape(1, -1)
        # Dconfig scaler
        pattern = scaler_jinfo.transform(pattern)
	return pattern		

def getBinarylabel(idx, dim):
	blarr = np.zeros(dim)
	blarr[idx] = 1
	
	return blarr.tolist()

def transform(x):
	batchX = []
	pattern = getPattern(x)
	
	# predict jobinfo
	jobLen = clf_jn.predict(pattern)
	jobLen = int(round(jobLen[0]))
	#print jobLen
	
	batchP = []
	for l in range(jobLen):
		pp = pattern[0]
		pp = np.append(pp,[l/float(jobLen)])
		batchP.append(pp)
	
	
	batchP = np.array(batchP)
	batchP = np.reshape(batchP,(1, batchP.shape[0], batchP.shape[1]))
	jobInfo = clf_jt.predict(batchP)
	
	jobType = jobInfo[0][0]
	jobRecord = jobInfo[1][0]
	
	jobTypelist = []
	jobRecordlist = []
	
	for l in range(jobLen):
                jobTypelist.append(jobType[l].argmax(axis=-1))
		jobRecordlist.append(math.pow(10,jobRecord[l]))

	#print jobTypelist
        #print jobRecordlist

	for l in range(jobLen):
		tmpX = getBinarylabel(int(jobTypelist[l]),5)
                tmpX.append(jobRecordlist[l])
		tmpX.append(float(RECORDS[int(scale)]))
		for i in range(len(x)):
			if i not in multiX:
				tmpX.append(x[i])
			else:
				tmpX.extend(getBinarylabel(x[i],3))
		tmpX = np.array(tmpX).reshape(1, -1)
		
		tmpX = scalerX.transform(tmpX)
		batchX.append(tmpX[0])
	
	batchX = np.array(batchX)
	batchX = np.reshape(batchX,(1, batchX.shape[0], batchX.shape[1]))
	return batchX

# predict function
def f(x):
	#print x
	transformX = transform(x)
	tmp = clf.predict(transformX)
	#print tmp[1][0][0]
	return tmp[1][0][0]

print "=========Optimization========"
result = dummy_minimize(f, bound, n_calls=1000, x0=None, y0=None, random_state=None, verbose=False, callback=None)
print "=========Dummy results========"
print result.fun
print result.x

print "=========Generate output========"

def generate_output(x):
	dag_output = open(output_file+'_dag', "w")
	for i in range(len(x)):
		value = ""	
		if i == len(x)-1:
			value = "-Xmx"+str(x[i])+"m"
		elif i == len(x)-2:
			if x[i] == 0:
                                value = "BLOCK"
                        else:
                                value = "RECORD"		
		elif i in boolIdx:
			if x[i] == 0:
				value = "false"
			else:
				value = "true"
	
		elif i in multiX:
			if x[i] == 0:
				value = "minimal"
			elif x[i] == 1:
				value = "none"
			else:
				value = "more"
		else:
			value = x[i]
			
		dag_output.write("set "+configs[i]+"="+str(value)+";\n")

def generate_bound(x):
	bound_output = open(output_file+'.csv', "w")	
	f = open('bound.csv','rb');
	cnt = 0
	for row in csv.reader(f):
		if cnt not in hadoopIdx:
			bound_output.write(row[0]+','+str(int(x[cnt]))+','+str(int(x[cnt]))+',1,'+row[4]+'\n')
		else:
			bound_output.write(row[0]+','+row[1]+','+row[2]+','+row[3]+','+row[4]+'\n')
		cnt = cnt + 1

generate_output(result.x)
generate_bound(result.x)
