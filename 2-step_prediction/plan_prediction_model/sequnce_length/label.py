import csv
import sys
import numpy as np
from sklearn import preprocessing

def label_features(input_file):
	
	X, job_num, featureFilter = read_file(input_file) 
	print X[1]
	isLabel = X[0]
	origin = X[1:]
	print "Dataset size ",len(X)
	print featureFilter
	X = binarylabel(isLabel, featureFilter, origin)
	print X[0]
	print "Dataset size ",len(X)
	
	Xarray = np.array(X) 
	job_type = Xarray[0:5]
	job_record = Xarray[:,5]
	X = Xarray[:,6:]
	
	return X, job_num, job_type, job_record 

def read_file(input_file):
	fin = open(input_file,'r');
        flag = 0
        X = []
	job_num = []
	

        for row in csv.reader(fin):
        	if len(row) == 2:
			job_num.append(int(row[1]))	
		elif flag == 0:
			featureFilter = row
			flag = 1 
		else:
                        X.append(row)        
        fin.close()	
	
	return X, job_num, featureFilter

def binarylabel(isLabel, featureFilter, X):
        Xzipped = zip(*X)
        le = preprocessing.LabelEncoder()
        binaryle = preprocessing.LabelBinarizer()
	
	from sklearn.externals import joblib
        import os.path
	label_filename = "../../models/jobtype_binarylabel.pkl"

        Xlabel = []
	print np.array(Xzipped).shape
        for i in range(len(featureFilter)):
		
		# For DAG configurations
		if featureFilter[i] == "d":
                	if isLabel[i] == "1":
				# Predefined Job Type	
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
