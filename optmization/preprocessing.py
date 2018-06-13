import numpy as np
import csv
import sys
from sklearn import preprocessing
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_regression
from sklearn.decomposition import PCA,TruncatedSVD
from sklearn.ensemble import RandomForestRegressor

def read_file(input_file, X, y):
	f = open(input_file, 'rb')
	
	for row in csv.reader(f):
        	row = [float(i) if i else 0 for i in row]

		total_time = row[0]
                number_of_jobs=int(row[1])
		row2=row[2:]
		
		dim = len(row2)
		num_of_feature = dim / number_of_jobs
		
		row3=np.array(row2).reshape((number_of_jobs,num_of_feature))
		
		X.append(row3)				
                y.append(total_time)
	
	print "Read : "+str(np.array(X).shape)
	f.close()

def read_metrics_file(input_file, X, mcnt):
        f = open(input_file, 'rb')
	
	max_length = 24
        for row in csv.reader(f):
                row = [float(i) if i else 0 for i in row]

                dim = len(row)
                
		if dim%2 == 1:
			dim = dim - 1
			row = row[:-1]

		num_of_feature = dim / mcnt
		
                row=np.array(row).reshape((mcnt,num_of_feature))
		
		for i in range(len(row[0])):
			row[0][i] = row[0][i] - min(row[0])
			row[1][i] = row[1][i] - min(row[1])
					
		row2 = np.zeros((mcnt, max_length))
               	row2[0][:len(row[0])] = row[0]
		row2[1][:len(row[1])] = row[1]
       		X.append(row2)
 
	print "Read : "+str(np.array(X).shape)
	
        f.close()


def data_preprocessing(X, Number, y):
	#scalerX = preprocessing.MinMaxScaler([0,1.0])
	
	#X = scalerX.fit_transform(X)
	X = np.array(X)
	X_proccessed = []	
	y_proccessed = []
	
	start = 0
	
	for i in range(len(Number)):
                number_of_jobs=int(Number[i])	
                num_of_feature = len(X[0])
		#print number_of_jobs
		
		row = []
		time = []
		max_records = 0
		max_reducer = 0

		for n in range(start,start + number_of_jobs):
			if X[n][0] > max_records:
				max_records = X[n][0]
			if X[n][3] > max_reducer:
                                max_reducer = X[n][3]			
		row = X[start]
		row[0] = max_records
		row[3] = max_reducer
		row = [float(r) for r in row]
	
                X_proccessed.append(row)
                y_proccessed.append(float(y[i]))
		start = start + number_of_jobs
		#print row2
	#X_proccessed = selecter.fit_transform(X_proccessed, y)	
	return X_proccessed, y_proccessed

def feature_select(X, y, k):
	selecter= SelectKBest(f_regression, k=k) #reduce to k features
	X = selecter.fit_transform(X, y)
	scores = selecter.scores_
	print "feature scores : ",scores
	return X
def svd(X,n):
	svd = TruncatedSVD(algorithm='randomized', n_components=n, n_iter=7,
        random_state=42)
	print svd.fit(X)
        X = svd.transform(X)
        return X	
	
def pca(X,n):
	pca = PCA(n_components=n)
	print pca.fit(X)
	X = pca.transform(X)
	return X

def randomforest(X, y):
	print("Random forest feature importance")
	rf = RandomForestRegressor()
	rf.fit(X, y)
	print "Features sorted by their score:"
	print map(lambda x: round(x, 4), rf.feature_importances_)
