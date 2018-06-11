import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM, GRU
from keras.layers import Embedding, Masking
from keras.optimizers import *
from keras import losses
from keras.layers import *
from keras import initializers
from keras.callbacks import *
from keras.models import Model
from keras.layers.advanced_activations import PReLU, LeakyReLU


def Keras_train(trainX, trainN, testX, testN, feature_dim):       	
	
	print len(trainX)
	
	input1 = Input(shape=(feature_dim,))

	filepath="weights.best.hdf5"
	#adam = Adam(lr=0.01, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=1e-6)
	adam = Adam()
	rmsprop=RMSprop(lr=0.01, rho=0.9, epsilon=1e-08, decay=0.0)
	earlyStopping=EarlyStopping(monitor='val_loss', patience=50, verbose=0, mode='auto')
	checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=0, save_best_only=True, mode='auto')

	output = Dense(16, activation='relu')(input1)
	output = Dense(8, activation='relu')(output)
	output = Dense(4, activation='relu')(output)
	output = Dense(1, activation='linear', name = 'num_output')(output)

	model = Model(inputs=input1, outputs=output)
	model.compile(optimizer=adam, loss={'num_output': 'mape'}, 
				      metrics={'num_output': 'mae'})
	model.summary()
	
	trainN = np.array(trainN)
	testN = np.array(testN)
	trainX = np.array(trainX)
        testX = np.array(testX)
	
	model.load_weights("weights.best.hdf5")
	model.fit(trainX, trainN, validation_data=(testX, testN), batch_size=1,
			epochs=100,callbacks=[checkpoint,earlyStopping])
	score = model.evaluate(testX, testN)
	print
        print "Score: ",
        print score
	#score = 0
	#from keras.utils import plot_model
	#plot_model(model, to_file='model.png')	
        
	# load weights
	model.load_weights("weights.best.hdf5")
	return model, score

