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
parser.add_argument("--s")
parser.add_argument("--m")
args = parser.parse_args()

input_file = args.i
scaler_file = args.s
model_file = args.m
X = []
Number = []
Types = []
Records = []
print "=========Read "+input_file+"========"
#Label text to number
X, Number, Types, Records = label_features(input_file)
print "Size : " + str(len(Number))
feature_dim = len(X[0])
print X[0]
print "=========Preprocessing========"
scaler_filename = "../models/"+scaler_file+".scl.pkl"
Xnew = data_preprocessing(X, Number, Types, Records,scaler_filename)
feature_dim = len(Xnew[0])
print Xnew[0]

train_num = int(len(Number) * 0.9)
total_num = int(len(Number))
print "Dataset size ",total_num


print "=========Train========"
clf, score = Keras_train(Xnew[:train_num], Number[:train_num], Xnew[train_num:total_num], Number[train_num: total_num],feature_dim)

print "=========Test========"
Ypredicted = Keras_predict(clf, Xnew)
#print [t for t in zip(Ypredicted[:total_num], Number[:total_num])]
print [t for t in zip(Ypredicted[train_num:total_num], Number[train_num:total_num])][:10]
print "=========Result Display========"
#error rate of test dataset
print "Test error rate:"
error_list = print_error(Ypredicted, Number, range(total_num-100,total_num), True)
#draw_boxplot(error_list,"rnn.png",0,0.3)

import csv

#f = open("rnn.csv","w")
#w = csv.writer(f)
#for e in error_list:
        #w.writerow([e])

#f.close()

# save model
clf.save(model_file) 
#print error_list
#print "Training error rate:"
#error_list = print_error(Ypredicted, Number, range(0,train_num), False)
