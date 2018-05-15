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
parser.add_argument("--o")
parser.add_argument("--m")
args = parser.parse_args()

input_file = args.i
output_file = args.o
model_file = args.m
X = []
y = []
Number = []
Time = []

print "=========Label "+input_file+"========"
#Label text to number
X, y, Number, Time = label_features(input_file)
print "Size : " + str(len(y))
feature_dim = len(X[0])

#print X[0][7]
print "=========Preprocessing========"
Xnew ,ynew = data_preprocessing(X, Number, y)

train_num = int(len(Xnew) * 0.9)
total_num = int(len(Xnew))
print "Dataset size ",total_num

print Xnew[:][0]
#training
print "=========Train========"
clf, score = Keras_train(Xnew[:train_num], ynew[:train_num], Xnew[train_num:total_num], ynew[train_num: total_num], feature_dim)

#output training model to file
#joblib.dump(clf, output_file + '.mdl.pkl')

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

print "=========Test========"
Ypredicted = Keras_predict(clf, Xnew)
#Ypredicted = scalerY.inverse_transform(Ypredicted.reshape(-1, 1))
print [t for t in zip(Ypredicted[train_num:total_num], ynew[train_num:total_num])][:10]


print len(ynew)
print "=========Result Display========"
#error rate of test dataset
print "Total error rate:"
error_list = print_error(Ypredicted, ynew, range(train_num,total_num), True)
#print zip(Ypredicted[train_num: total_num], y[train_num: total_num])[:10]

draw_boxplot(error_list,"dnn.png",0,0.3)

import csv

f = open("dnn.csv","w")
w = csv.writer(f)
for e in error_list:
	w.writerow([e])

f.close()

# save model
clf.save(model_file)
#print error_list
#training error
print "Training error rate:"
error_list = print_error(Ypredicted, ynew, range(0,train_num), True)

#print "=========Write "+output_file+"========"
#write_file(output_file,np.percentile(Z, 75))i

#fout = open('tuning_mean','w')
#fout.write(str(mean))
#fout.close()

