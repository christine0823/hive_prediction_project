import numpy as np
from label import *
from preprocessing import *
from test import * 
from sklearn.externals import joblib
from sklearn.externals import joblib
from keras.models import load_model
import math
#initial
print "=========Initial========"
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument("--i")
parser.add_argument("--q")
args = parser.parse_args()

input_file = args.i
query = args.q
X = []
y = []

print "=========Read "+input_file+"========"
#Label text to number
X, y, Number, Time, featureFilter = label_features(input_file)
print "Size : " + str(len(y))
feature_dim = len(X[0])

print "=========Preprocessing========"
Xnew, Dnew, ynew, tnew = data_preprocessing(X, y, Number, Time, featureFilter)

train_num = int(len(ynew) * 0.9)
total_num = int(len(ynew))
print "Features : "+ str(feature_dim)

#train_num = total_num - 100
print "Dataset size ",total_num

print "=========Load Model========"
scalerX = joblib.load('../models/'+query+'_time.scl.pkl')
clf = load_model('../models/'+query+'_time.h5')

# Step 1 : read jobinfo model
scaler_jinfo = joblib.load('../models/'+query+'_jobInfo.scl.pkl')
clf_jn = load_model('../models/'+query+'_seqLen.h5')
clf_jt = load_model('../models/'+query+'_jobInfo.h5')

multi_X = [5]
multi_Dag = [3]

def getBinarylabel(idx, dim):
        blarr = np.zeros(dim)
	blarr[int(idx)] = 1

        return blarr.tolist()

def transform(x, dagX):
        batchX = []
        # predict jobinfo
	dd = [] 
	for i in range(len(dagX)):
        	if i not in multi_Dag:
                	dd.append(dagX[i])
                else:
                       	dd.extend(getBinarylabel(dagX[i],3))
	
	dd = np.array(dd).reshape(1, -1)
	dd = scaler_jinfo.transform(dd)
        jobLen = clf_jn.predict(dd)
        jobLen = int(round(jobLen[0]))
        
	batchP = []
        for l in range(jobLen):
                pp = np.append(dd, [float(l)/float(jobLen)])
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
	
        print jobTypelist
        print jobRecordlist
        for l in range(jobLen):
                tmpX = getBinarylabel(int(jobTypelist[l]),5)
		tmpX.append(jobRecordlist[l])
			
                for i in range(len(x)):
                        if i not in multi_X:
                                tmpX.append(x[i])
                        else:
                                tmpX.extend(getBinarylabel(x[i],3))
                tmpX = np.array(tmpX).reshape(1, -1)
                #scale
                tmpX = scalerX.transform(tmpX)
                batchX.append(tmpX[0])
	
        batchX = np.array(batchX)
        batchX = np.reshape(batchX,(1, batchX.shape[0], batchX.shape[1]))
        return batchX

error_list = []
print len(Xnew)

for i in range(total_num-100,total_num):
	print i
	transformX = transform(Xnew[i], Dnew[i])
        tmp = clf.predict(transformX)
        #print tmp[0][0],
	#print tnew[i]
	print "("+str(tmp[1][0][0])+","+str(ynew[i])+")"
	error_list.append(abs(tmp[1][0][0] - ynew[i])/ynew[i])

print "Dataset size: ", len(error_list)
print "-------------------------"
get_percentile(error_list, 0) #min

get_percentile(error_list, 10) #Q1
get_percentile(error_list, 25) #Q1
get_percentile(error_list, 50) #Q2
get_percentile(error_list, 75) #Q3
get_percentile(error_list, 90) #90%
get_percentile(error_list, 95) #95%

get_percentile(error_list, 100) #max
print "mean: ",
print np.mean(error_list)
print error_threshold(error_list,1)
print "----------------------\n"
