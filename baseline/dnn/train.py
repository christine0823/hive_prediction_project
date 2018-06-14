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
from keras.callbacks import *
from keras.layers import *
from keras.models import Model

def Keras_train(trainX, trainY, testX, testY, feature_dim):
      	
	trainY=np.array(trainY).reshape(-1,1)
	testY=np.array(testY).reshape(-1,1)
	
	model = Sequential()
	#model.add(Masking(mask_value=-1, input_shape=(maxlength, feature_dim)))
	
	model.add(Dense(64, activation='relu', input_dim=feature_dim))
	model.add(Dense(32, activation='relu'))
	model.add(Dense(16, activation='relu'))
	model.add(Dense(1, activation='linear'))
	
		
	filepath="weights.best.hdf5"
        adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=1e-6)
        rmsprop=RMSprop(lr=0.001, rho=0.9, epsilon=1e-08, decay=0.0)
	checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=0, save_best_only=True, mode='auto')	
	earlyStopping=EarlyStopping(monitor='val_loss', patience=5, verbose=0, mode='auto')
	model.compile(optimizer=adam, loss='mean_absolute_percentage_error')
	
	model.fit(trainX, trainY, epochs=100, batch_size=1, verbose=1, validation_data=(testX, testY), callbacks=[checkpoint])
	#model.fit(trainX, trainY, epochs=100, batch_size=4, verbose=1, validation_data=(testX, testY))
	model.summary()
	score = model.evaluate(testX, testY, batch_size=4)
        print
        print "Score: ",
        print score
	# load weights
        model.load_weights("weights.best.hdf5")
        return model, score

