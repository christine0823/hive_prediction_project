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
parser.add_argument("--m")
args = parser.parse_args()

input_file = args.i
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


print "=========Test========"
Ypredicted = Keras_predict(clf, Xnew)
print [t for t in zip(Ypredicted[train_num:total_num], ynew[train_num:total_num])][:10]


print len(ynew)
print "=========Result Display========"
#error rate of test dataset
print "Total error rate:"
error_list = print_error(Ypredicted, ynew, range(total_num-100,total_num), True)

#training error
print "Training error rate:"
error_list = print_error(Ypredicted, ynew, range(0,train_num), True)

