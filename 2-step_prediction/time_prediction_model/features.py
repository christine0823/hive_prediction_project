import numpy as np
from label import *
from preprocessing import *
from train import *
from test import *
from sklearn.externals import joblib

#initial
print "=========Initial========"
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument("--i")
parser.add_argument("--l")
parser.add_argument("--o")
parser.add_argument("--BATCH_SIZE", default=200, type=int)
parser.add_argument("--NUM_LAYER", default=3, type=int)
parser.add_argument("--NUM_NEURAL", default=100, type=int)
parser.add_argument("--MAX_ITER", default=200, type=int)
parser.add_argument("--L_R_INIT", default=0.001, type=float)
parser.add_argument("--POWER_T", default=0.5, type=float)
parser.add_argument("--ALPHA", default=0.0001, type=float)
parser.add_argument("--SOLVER", default="adam", type=str)
parser.add_argument("--TMP", default=0, type=int)
args = parser.parse_args()

input_file = args.i
labeled_file = args.l
output_file = args.o
X = []
y = []
Ytarget = []

print "=========Label "+input_file+"========"
#Label text to number
isLabel, origin = label_features(input_file, labeled_file, True)
#joblib.dump(isLabel, output_file + '.lab.pkl', compress=False)

print "=========Read "+labeled_file+"========"
read_file(labeled_file, X, y,Ytarget)
print X[0]

train_num = int(len(X) * 0.8)
total_num = int(len(X))
print "Dataset size ",total_num

#scaling each feature 
print "=========Scale========"
X,y,scalerX = scale_values(X,y)
#joblib.dump([scalerX, scalerY], output_file + '.scl.pkl', compress=False)

#feature selection with SelectKBest
#print "=========Feature Selection========"
#X = feature_select(X, y, args.TMP)
#randomforest(X,y)
#PCA
#print "=========PCA========"
#X = pca(X, 5)

#training
print "=========Train========"
#clf, score = NN_train(X[:train_num], y[:train_num], args)
#clf, score = SVR_train(X[:train_num], y[:train_num], args)
#clf, score = DT_train(X[:train_num], y[:train_num], args)
clf, score = Keras_train(X[:train_num], y[:train_num], X[train_num:], y[train_num:])
#clfs, score = ALL_train(X[:train_num], y[:train_num], args)

#output training model to file
#joblib.dump(clf, output_file + '.mdl.pkl')

print "=========Test========"
Ypredicted = Keras_predict(clf, X)
#Ypredicted = predict(clf, X)
#print zip(Ypredicted[train_num: total_num], Ytarget[train_num: total_num])[:10]

print "=========Result Display========"
#error rate of test dataset
print "Total error rate:"
error_list, mean, badindex, errindex = print_error(Ypredicted, Ytarget, range(train_num,total_num), True)


for i in range(4,27):
	print output_file+"_X"+str(i)+".csv"
	X_back = scalerX.inverse_transform(X[train_num:total_num])
	record = zip(Ypredicted[train_num: total_num], Ytarget[train_num: total_num], X_back[:,i])
	file = open(output_file+"_X"+str(i)+".csv", "w")
	writer = csv.writer(file, delimiter = ",")
	for r in record:
     		writer.writerows([r])
	file.close
'''
for r in record:
        print r

file = open(output_file+"_Ytarget.csv", "w")
writer = csv.writer(file, delimiter = ",")
for r in record:
     writer.writerows([r])
file.close
'''
#training error
#print "Training error rate:"
#error_list, mean, badindex  = print_error(Ypredicted, Ytarget, range(0,train_num), False)

#print "=========Write "+output_file+"========"
#write_file(output_file,np.percentile(Z, 75))

#fout = open('tuning_mean','w')
#fout.write(str(mean))
#fout.close()

#print clf.predict(scalerX.transform([0.0, 0.0, 3.0, 6.0, 54.0, 10.0, 12.0, 110.0, 100.0, 20.0, 0.5, 0.7, 0.2, 0.7, 0.9, 1200.0, 0.05, 50.0, 40.0, 4.0, 2.0, 1664.0, 1792.0, 1920.0, 4.0, 0.0, 415.0, 10000000000.0, 8.0, 3.0, 1.0, 3.0, 0.0, 894.0, 0.0, 446.0, 17.0, 2.0, 1.0, 2.0, 0.0, 883.0, 0.0, 882.0, 0.0, 5.0, 2.0, 2.5, 0.5, 443.0, 163.0, 294.333, 224.383, 0]))
#print len ([0.0, 0.0, 3.0, 6.0, 54.0, 10.0, 12.0, 110.0, 100.0, 20.0, 0.5, 0.7, 0.2, 0.7, 0.9, 1200.0, 0.05, 50.0, 40.0, 4.0, 2.0, 1664.0, 1792.0, 1920.0, 4.0, 0.0, 415.0, 10000000000.0, 8.0, 3.0, 1.0, 3.0, 0.0, 894.0, 0.0, 446.0, 17.0, 2.0, 1.0, 2.0, 0.0, 883.0, 0.0, 882.0, 0.0, 5.0, 2.0, 2.5, 0.5, 443.0, 163.0, 294.333, 224.383, 0])
