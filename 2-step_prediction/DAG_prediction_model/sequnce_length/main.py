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
Number = []
Types = []
Records = []
Datasets = []
print "=========Read "+input_file+"========"
#Label text to number
X, Number = label_features(input_file)
print "Size : " + str(len(Number))
feature_dim = len(X[0])

scaler_file = model_file+"_jobInfo.scl.pkl"
print "=========Preprocessing========"
Xnew = data_preprocessing(X, Number, scaler_file)
feature_dim = len(Xnew[0])

train_num = int(len(Number) * 0.9)
total_num = int(len(Number))
print "Dataset size ",total_num

print Xnew[total_num-10:]
print Number[total_num-10:]
print "=========Train========"
clf, score = Keras_train(Xnew[:train_num], Number[:train_num], Xnew[train_num:total_num], Number[train_num: total_num],feature_dim)

print "=========Test========"
Ypredicted = Keras_predict(clf, Xnew)
#print [t for t in zip(Ypredicted[0:5], Number[0:5])]
print [t for t in zip(Ypredicted[train_num:total_num], Number[train_num:total_num])][:10]
print "=========Result Display========"
#error rate of test dataset
print "Test error rate:"
error_list = print_error(Ypredicted, Number, range(total_num-100,total_num), True)
#draw_boxplot(error_list,"rnn.png",0,0.3)

# save model
clf.save(model_file+'_seqLen.h5') 
#print error_list
print "Training error rate:"
error_list = print_error(Ypredicted, Number, range(0,train_num), False)
