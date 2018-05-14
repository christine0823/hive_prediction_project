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
output_file = args.s
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
scaler_filename = "../models/"+output_file+".scl.pkl"
Xnew ,tnew, rnew = data_preprocessing(X, Number, Types, Records,scaler_filename)

print Xnew[0]
#print Number[:5]
print rnew[:5]
train_num = int(len(rnew) * 0.9)
total_num = int(len(rnew))
#train_num = total_num - 20
print "Dataset size ",total_num

feature_dim = feature_dim + 1

print "=========Train========"
clf, score = Keras_train(Xnew[:train_num], tnew[:train_num], rnew[:train_num], Xnew[train_num:total_num], tnew[train_num:total_num], rnew[train_num: total_num],feature_dim)

#import matplotlib as mpl
#mpl.use('Agg')
#import matplotlib.pyplot as plt

target = []
for t in tnew:
	target.append(t.argmax(axis=-1))

print "=========Test========"
Ypredicted = Keras_predict(clf, Xnew)
#print [t for t in zip(Ypredicted[train_num:total_num], target[train_num:total_num])][:1]
#print [t for t in zip(Ypredicted[train_num:total_num], rnew[train_num:total_num])][0:5]
#print "=========Result Display========"
#error rate of test dataset
print "Test error rate:"
error_list = print_error(Ypredicted, rnew, range(total_num-100,total_num), True)
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
#error_list = print_error(Ypredicted, target, range(train_num,train_num+4), False)
#error_list = print_error(Ypredicted, target, range(train_num+4,train_num+8), False)
#error_list = print_error(Ypredicted, target, range(train_num+8,train_num+12), False)
#error_list = print_error(Ypredicted, target, range(train_num+12,train_num+16), False)
#error_list = print_error(Ypredicted, target, range(train_num+16,train_num+20), False)
