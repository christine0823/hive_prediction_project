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
y = []
Number = []
Time = []
print "=========Read "+input_file+"========"
#Label text to number
X, y, Number, Time = label_features(input_file)
print "Size : " + str(len(y))
feature_dim = len(X[0])

print "=========Preprocessing========"
Xnew ,ynew, tnew = data_preprocessing(X, Number, y, Time, scaler_file)

train_num = int(len(ynew) * 0.9)
total_num = int(len(ynew))
#train_num = total_num - 100
print "Dataset size ",total_num


print "=========Train========"

clf, score = Keras_train(Xnew[:train_num], tnew[:train_num], ynew[:train_num], Xnew[train_num:total_num], tnew[train_num:total_num], ynew[train_num: total_num],feature_dim)

#import matplotlib as mpl
#mpl.use('Agg')
#import matplotlib.pyplot as plt

print "=========Test========"
Ypredicted = Keras_predict(clf, Xnew)
print [t for t in zip(Ypredicted[train_num:total_num], ynew[train_num:total_num])][:10]

print "=========Result Display========"
#error rate of test dataset
print "Test error rate:"
error_list = print_error(Ypredicted, ynew, range(train_num-50, train_num+50), True)

#draw_boxplot(error_list,"rnn.png",0,0.3)


# save model
clf.save(model_file) 

print "Training error rate:"
error_list = print_error(Ypredicted, ynew, range(0,train_num), False)
