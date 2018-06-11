import numpy as np
import csv
import sys
from sklearn import preprocessing
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_regression
from sklearn.decomposition import PCA,TruncatedSVD
from sklearn.ensemble import RandomForestRegressor

def data_preprocessing(X, y, Number, Time, featureFilter):
	#scalerX = preprocessing.MinMaxScaler([0,1.0])
	
	#X = scalerX.fit_transform(X)
	
	from sklearn.externals import joblib
	
	X_proccessed = []
	D_proccessed = []	
	y_proccessed = []
	t_proccessed = []
	start = 0
	
	for i in range(len(Number)):
                number_of_jobs=int(Number[i])	
                num_of_feature = len(X[0])
		#print number_of_jobs

		row = []
		time = []
		max_reducer = 0.0
		row.extend(X[start])
		for j in range(start, start + number_of_jobs):
			if float(X[j][2]) > max_reducer:
                                max_reducer=float(X[j][2])		
			time.append(Time[j])

		row = [float(r) for r in row]
		row[2] = float(max_reducer)
		time = [float(t)/1000.0 for t in time]
		time2 = np.array(time).reshape(number_of_jobs,1)
		row2=row
		dagConfig = []
		
		index = 0
		for k in range(len(featureFilter)):
			if featureFilter[k] == 'd':
				dagConfig.append(row2[k])

                X_proccessed.append(row2)
		D_proccessed.append(dagConfig)
                y_proccessed.append(float(y[i]))
		t_proccessed.append(time2)
		start = start + number_of_jobs
	
	return X_proccessed, D_proccessed, y_proccessed, t_proccessed

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
