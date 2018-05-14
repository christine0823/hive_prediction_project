import numpy as np
from label import *
from preprocessing import *
from train import *
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
Number = []
Time = []
print "=========Read "+input_file+"========"
#Label text to number
X, y, Number, Time = label_features(input_file)
print "Size : " + str(len(y))
feature_dim = len(X[0])

print "=========Preprocessing========"
#scaler_filename = "../models/"+scaler_file+".scl.pkl"
Xnew ,ynew, tnew = data_preprocessing(X, Number, y, Time)

print Xnew[0]
train_num = int(len(ynew) * 0.9)
total_num = int(len(ynew))
print "Features : "+ str(feature_dim)

#train_num = total_num - 100
print "Dataset size ",total_num
scale = joblib.load('../plan_table/'+query+'_scale.pkl')

print "=========Load========"
scalerX = joblib.load('../models/rnn_'+query+'.scl.pkl')
clf = load_model('../models/rnn_'+query+'.h5')

# Step 1 : read jobinfo model
scaler_jinfo = joblib.load('../models/jobinfo_'+query+'.scl.pkl')
clf_jn = load_model('../models/jobnum_'+query+'.h5')
clf_jt = load_model('../models/jobinfo_'+query+'.h5')

dagidx = [1,3,5,6,7,8,14,15,16,33,34,35,40]
multi_dagidx = [4]
def getPattern(x,record):
        pattern = [record*1000000]
        for i in range(len(x)):
                if i in multi_dagidx:
                        pattern.extend(getBinarylabel(x[i],3))
                elif i in dagidx:
                        pattern.append(x[i])

        pattern = np.array(pattern).reshape(1, -1)
        print pattern
        #scale
        pattern = scaler_jinfo.transform(pattern)
        return pattern

def getBinarylabel(idx, dim):
        blarr = np.zeros(dim)
	blarr[int(idx)] = 1

        return blarr

def transform(x, record):
        batchX = []
        pattern = getPattern(x,record)
        # predict jobinfo
        jobLen = clf_jn.predict(pattern)
        jobLen = int(round(jobLen[0]))
        print jobLen
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
	
        print jobTypelist
        print jobRecordlist
        for l in range(jobLen):
                #tmpX = [RECORDS[int(scale)]]
                tmpX = [jobRecordlist[l]]
                jobType = jobTypelist[l]
                tmpX.extend(getBinarylabel(int(jobType),5))
                for i in range(len(x)):
                        if i not in multi_dagidx:
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
print len(scale)
for i in range(train_num,train_num+40):
	print i
	#print Xnew[i]
	transformX = transform(Xnew[i],scale[i])
        tmp = clf.predict(transformX)
        print tmp[0][0],
	print tnew[i]
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
