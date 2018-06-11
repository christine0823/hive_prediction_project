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
print "=========Read "+input_file+"========"
#Label text to number
X, Number, Types, Records = label_features(input_file)
print "Size : " + str(len(Number))
feature_dim = len(X[0])

scaler_file = model_file+"_jobInfo.scl.pkl"
print "=========Preprocessing========"
Xnew ,tnew, rnew = data_preprocessing(X, Number, Types, Records, scaler_file)

train_num = int(len(rnew) * 0.9)
total_num = int(len(rnew))
print "Dataset size ",total_num

feature_dim = feature_dim + 1

print "=========Train========"
clf, score = Keras_train(Xnew[:train_num], tnew[:train_num], rnew[:train_num], Xnew[train_num:total_num], tnew[train_num:total_num], rnew[train_num: total_num],feature_dim)

#import matplotlib as mpl
#mpl.use('Agg')
#import matplotlib.pyplot as plt

# Type target
target = []
for t in tnew:
	target.append(t.argmax(axis=-1))

print "=========Test========"
predT, predR = Keras_predict(clf, Xnew)
print [t for t in zip(predT[train_num:total_num], target[train_num:total_num])][:5]
print [t for t in zip(predR[train_num:total_num], rnew[train_num:total_num])][:5]

print "=========Result Display========"

print "## For Operation types ##"
#error rate of test dataset
print "Test error rate:"
error_list = print_error(predT, target, range(total_num-100,total_num), True)

#print error_list
print "Training error rate:"
error_list = print_error(predT, target, range(0,train_num), False)

print "## For Records ##"
#error rate of test dataset
print "Test error rate:"
error_list = print_error(predR, rnew, range(total_num-100,total_num), True)

#print error_list
print "Training error rate:"
error_list = print_error(predR, rnew, range(0,train_num), False)

# save model
clf.save(model_file+'_jobInfo.h5')
