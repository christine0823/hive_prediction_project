import csv
import sys
import numpy as np
from sklearn import preprocessing

def label_features(input_file):
	
	X, time, job_num, job_time = read_file(input_file) 
	print X[1]
	isLabel = X[0]
	origin = X[1:]
	print "Dataset size ",len(X)
	X = binarylabel(isLabel, origin)
	print X[0]
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
	print Xzipped.shape
        for i in range(len(isLabel)):
		print i
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
	
	from sklearn.externals import joblib
        import os.path
	label_filename = "jobtype_binarylabel.pkl"

        Xlabel = []
	binaryle_table = dict()

	print np.array(Xzipped).shape
        for i in range(len(isLabel)):
                if isLabel[i] == "1":
                        if i != 1:
				binaryle.fit(Xzipped[i])
                        else:
				if os.path.exists(label_filename):
					binaryle = joblib.load(label_filename)
				else:
					binaryle.fit(Xzipped[i])
				

			print binaryle.classes_
			#Xlabel.append(le.transform(Xzipped[i]))
                        #print str(i) + ":" + str(binaryle.classes_)
			labelarray = binaryle.transform(Xzipped[i])
                        
			# jobType
			#if i == 1:
				#joblib.dump(binaryle, label_filename)
				#joblib.load(label_filename)
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
