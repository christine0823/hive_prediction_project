import csv
import sys
import numpy as np
from sklearn import preprocessing

def label_features(input_file):
	
	X, time, job_num, job_time, featureFilter = read_file(input_file) 
	print X[1]
	isLabel = X[0]
	origin = X[1:]
	X = label(isLabel, origin)
	print "Dataset size ",len(X)
	
	Xarray = np.array(X)
	job_type = Xarray[:,0]
        job_record = Xarray[:,1]
        X = Xarray[:,2:]
	
	# Remove operation_type and input_records
	featureFilter = featureFilter[2:]
	print X[0]
	print featureFilter
	return X, time, job_num, job_time, featureFilter

def read_file(input_file):
	fin = open(input_file,'r');
        X = []
	time = []
	job_num = []
	job_time = []
       	numR = 0
 
	for row in csv.reader(fin):
        	if len(row) == 2:
			time.append(float(row[0]))		
			job_num.append(int(row[1]))	
		elif numR == 0:
			featureFilter = row[1:]
			numR = 1
		elif numR == 1:
			# label
			X.append(row[1:])
                        numR = 2 
		else:
			job_time.append(row[0])
                        X.append(row[1:])
        fin.close()	
	
	return X, time, job_num, job_time, featureFilter

def label(isLabel, X):
        Xzipped = zip(*X)
        le = preprocessing.LabelEncoder()
	
	from sklearn.externals import joblib
	import os
        label_filename = "jobtype_label.pkl"


        Xlabel = []
	print np.array(Xzipped).shape
        for i in range(len(isLabel)):
                if isLabel[i] == "1":
			# For operation type
			if i != 0:
                        	le.fit(Xzipped[i])
			else:
				if os.path.exists(label_filename):
					print label_filename
					le = joblib.load(label_filename)
				else:
					le.fit(Xzipped[i])

			print le.classes_
			Xlabel.append(le.transform(Xzipped[i]))
                else:
                        Xlabel.append(Xzipped[i])
        X = zip(*Xlabel)
        return X

def write_file(labeled_file, results):
	fout = open(labeled_file,'wb')
        writer = csv.writer(fout)
        writer.writerows(results)
