from sklearn.neural_network import MLPRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
import os
import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import math

def Keras_predict(clf, X):
        print "Testing start..."
	#Ypredicted = clf.predict(X)
	predR = []
	predT = []
	for batchx in X:
		batchx = np.reshape(batchx,(1,batchx.shape[0],batchx.shape[1]))
		tmp = clf.predict_on_batch(batchx)
		records = tmp[1][0]
		operation_type = tmp[0][0].argmax(axis=-1)
		predR.append(np.reshape(tmp[1][0],(batchx.shape[1],1)))
		predT.append(operation_type)	

        return predT, predR

def print_error(Ypredicted, Ytarget, index, detailed):
	print "----------------------"
	target = np.array([Ytarget[i] for i in index])
        predicted = np.array([Ypredicted[i] for i in index])
	
	error_list = []
	for p, t in zip(predicted,target):
		#print p
		#print t
		acc = 0.0
		jlen = len(p)
		
		for i in range(jlen):
			#if p[i] != t[i]:
			#	acc = acc+1
			if t[i] > 0:
				acc = acc + float(abs(p[i] - t[i]))/float(t[i])
		#print p
		#print t
		#print acc
		error_list.append(float(acc)/jlen)
	#error_list = abs((predicted - target)/target)
		
	
	print "Dataset size: ", len(error_list)
	#print "Average: ", np.mean(target)
	print "-------------------------"
        get_percentile(error_list, 0) #min
	
        if detailed == True :
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
	
        return error_list

def get_percentile(error_list,n):
	print str(n)+"%: ",
	print np.percentile(error_list, n)

def error_threshold(error_list,t):
	print "#Error > ",t,":",
        print sum(1 for i in error_list if i >t) 

def draw_boxplot(error_list,filename,y_min,y_max):
	fig = plt.figure()
	plt.boxplot(error_list)
	x1, x2, y1, y2 = plt.axis()
	plt.axis([x1, x2, y_min, y_max])
	plt.savefig(filename)

def write_file(output_file,results):
	f = open(output_file, 'w')
	f.write(str(results))
	f.close()
