import numpy as np
import csv
import sys
from sklearn import preprocessing
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_regression
from sklearn.decomposition import PCA,TruncatedSVD
from sklearn.ensemble import RandomForestRegressor

def data_preprocessing(X, Number, y):
	scalerX = preprocessing.MinMaxScaler([0,1.0])
	
	X = scalerX.fit_transform(X)
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
		
		for n in range(start,start + number_of_jobs):
			if X[n][2] > max_records:
				max_records = X[n][2]
	
		row = X[start]
		row[2] = max_records
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
