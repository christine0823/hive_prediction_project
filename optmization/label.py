import csv
import sys
import numpy as np
from sklearn import preprocessing

def label_features(input_file):
	
	X, time, job_num, job_time = read_file(input_file) 

	isLabel = X[0]
	print isLabel
	print X[1]
	origin = X[1:]
	print "Dataset size ",len(X)
	X = label(isLabel, X[1:])
	print "Dataset size ",len(X)
 
	return X, time, job_num, job_time 

def read_file(input_file):
	fin = open(input_file,'r');
        flag = 0
        X = []
	time = []
	job_num = []
	job_time =[]
        for row in csv.reader(fin):
        	if len(row) == 2:
			time.append(row[0])		
			job_num.append(row[1])	
		elif flag == 0:
			X.append(row)
			flag = 1 
		else:
			job_time.append(row[0])
                        X.append(row[1:])        
        fin.close()	
	
	return X, time, job_num, job_time

def label(isLabel, X):
	Xzipped = zip(*X)
        le = preprocessing.LabelEncoder()

        Xlabel = []
	print np.array(Xzipped).shape
        for i in range(len(isLabel)):
                if isLabel[i] == "1":
                        le.fit(Xzipped[i])
                        Xlabel.append(le.transform(Xzipped[i]))
                else:
                        Xlabel.append(Xzipped[i])
        X = zip(*Xlabel)
        return X

def binarylabel(isLabel, X):
        Xzipped = zip(*X)
        le = preprocessing.LabelEncoder()
        binaryle = preprocessing.LabelBinarizer()

        Xlabel = []
	print np.array(Xzipped).shape
        for i in range(len(isLabel)):
                if isLabel[i] == "1":
                        binaryle.fit(Xzipped[i])
                        #Xlabel.append(le.transform(Xzipped[i]))
                        #print str(i) + ":" + str(binaryle.classes_)
			labelarray = binaryle.transform(Xzipped[i])
                        
			for j in range(labelarray.shape[1]):
                        	Xlabel.append(labelarray[:,j])
                else:
                        Xlabel.append(Xzipped[i])
        X = zip(*Xlabel)
        return X

def write_file(labeled_file, results):
	fout = open(labeled_file,'wb')
        writer = csv.writer(fout)
        writer.writerows(results)
