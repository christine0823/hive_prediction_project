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


def Keras_train(trainX, trainT, trainR, testX, testT, testR, feature_dim):       	
	
	print len(trainX)
	
	input1 = Input(shape=(None,feature_dim))

	filepath="weights.best.hdf5"
	#adam = Adam(lr=0.01, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=1e-6)
        adam = Adam()
	rmsprop=RMSprop(lr=0.01, rho=0.9, epsilon=1e-08, decay=0.0)
	earlyStopping=EarlyStopping(monitor='val_loss', patience=100, verbose=0, mode='auto')
	checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=0, save_best_only=True, mode='auto')

	lstm_out = LSTM(feature_dim, kernel_initializer='Orthogonal',
			      bias_initializer='zeros',
			      kernel_regularizer=regularizers.l2(0.01),
                              activity_regularizer=regularizers.l1(0.01),
			      return_sequences=True,
			      activation = 'relu')(input1)
	
	type_output = TimeDistributed(Dense(16, activation='relu'))(lstm_out)
	type_output = TimeDistributed(Dense(8, activation='relu'))(type_output)
	type_output = TimeDistributed(Dense(5, activation='softmax'), name = 'type_output')(type_output)

	record_output = TimeDistributed(Dense(16, activation='relu'))(lstm_out)
	record_output = TimeDistributed(Dense(16, activation='relu'))(record_output)
	record_output = TimeDistributed(Dense(16, activation='relu'))(record_output)
	record_output = TimeDistributed(Dense(16, activation='relu'))(record_output)
	record_output = TimeDistributed(Dense(16, activation='relu'))(record_output)
	record_output = TimeDistributed(Dense(16, activation='relu'))(record_output)
	record_output = TimeDistributed(Dense(16, activation='relu'))(record_output)
	record_output = TimeDistributed(Dense(1, activation='linear'), name = 'record_output')(record_output)

	model = Model(inputs=input1, outputs=[type_output,record_output])
	model.compile(optimizer=adam, loss={'type_output': 'categorical_crossentropy','record_output': 'mape'}, 
				      metrics={'type_output': 'acc'})

	model.summary()
	
	def batch_generation(bX, bT, bR):
		while 1:
			idx = range(len(bX))
        		np.random.shuffle(idx)
			batches = [[bX[i], bT[i], bR[i]] for i in idx]	
				
			for batchx, batcht, batchr in batches:
                		batchr = np.reshape(batchr,(1,batcht.shape[0],1))
                		batchx = np.reshape(batchx,(1,batchx.shape[0],batchx.shape[1]))
				batcht = np.reshape(batcht,(1,batcht.shape[0],5))
				yield (batchx, [batcht, batchr])
	
	model.fit_generator(batch_generation(trainX, trainT, trainR), steps_per_epoch=len(trainX), 
			validation_data=batch_generation(testX, testT, testR), validation_steps=len(testX),
			epochs=500,callbacks=[checkpoint,earlyStopping])
	score = model.evaluate_generator(batch_generation(testX, testT, testR), steps=len(testX))
	print
        print "Score: ",
        print score
	
	#from keras.utils import plot_model
	#plot_model(model, to_file='model.png')	
        #score = 0
	# load weights
	model.load_weights("weights.best.hdf5")
	return model, score

