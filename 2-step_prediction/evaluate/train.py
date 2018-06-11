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

def Keras_autoencoder(Mx, num_jobs):

	Mx = np.array(Mx)
	Mx_out = []
	for i in range(Mx.shape[1]):
		input_vec = Input(shape=(Mx.shape[2],))
	
		# encoder layers
		encoding_dim = 4
		mask = Masking(mask_value=1.0)(input_vec)
		encoded = Dense(24, activation='relu')(mask)
		encoded = Dense(8, activation='relu')(encoded)
		encoder_output = Dense(encoding_dim, activation='relu')(encoded)
	
		# decoder layers
		decoded = Dense(8, activation='relu')(encoder_output)
		decoded = Dense(24, activation='relu')(decoded)

		# construct the autoencoder model
		autoencoder = Model(input=input_vec, output=decoded)

		# construct the encoder model for plotting
		encoder = Model(input=input_vec, output=encoder_output)
	
		# compile autoencoder
		autoencoder.compile(optimizer='adam', loss='mse')

		# training
		autoencoder.fit(Mx[:,i,:], Mx[:,i,:], epochs=20, batch_size=16, verbose=0)
		out = encoder.predict(Mx[:,i,:])
		out = out.reshape(int(Mx.shape[0] / num_jobs), num_jobs, encoding_dim)
		Mx_out.append(out)

	return Mx_out[0], Mx_out[1]


def Keras_train(trainX, trainT, trainY, testX, testT, testY, feature_dim):       	
	print len(trainX)
	
	input1 = Input(shape=(None,feature_dim))

	filepath="weights.best.hdf5"
	adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=1e-6)
        rmsprop=RMSprop(lr=0.01, rho=0.9, epsilon=1e-08, decay=0.0)
	earlyStopping=EarlyStopping(monitor='loss', patience=50, verbose=0, mode='auto')
	checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=0, save_best_only=True, mode='auto')

	lstm_out = LSTM(32, kernel_initializer='Orthogonal',
			      bias_initializer='zeros',
			      kernel_regularizer=regularizers.l2(0.01),
                              activity_regularizer=regularizers.l1(0.01),
			      activation='relu',return_sequences=True)(input1)

	lstm_out = LSTM(16, kernel_initializer='Orthogonal',
			      bias_initializer='zeros',
			      kernel_regularizer=regularizers.l2(0.01),
                              activity_regularizer=regularizers.l1(0.01),
			      activation='relu',return_sequences=True)(lstm_out)


	time_output = TimeDistributed(Dense(8, activation='relu'))(lstm_out)
	time_output = TimeDistributed(Dense(1, activation='linear'))(time_output)

	lstm_out1 = LSTM(8, kernel_initializer='Orthogonal',
                              bias_initializer='zeros',
                              kernel_regularizer=regularizers.l2(0.01),
                              activity_regularizer=regularizers.l1(0.01),
                              activation='relu',return_sequences=False)(lstm_out)

	#lstm_out1 = Dense(16, activation='relu')(lstm_out1)
	lstm_out1 = Dense(4, activation='relu')(lstm_out1)
	output = Dense(1, activation='linear')(lstm_out1)
	#output = Dense(1, activation='linear')(output)

	model = Model(inputs=input1, outputs=[time_output,output])
	#model = Model(inputs=input1, outputs=output)
	model.compile(optimizer=adam, loss='mean_absolute_percentage_error')
	model.summary()
	
	def batch_generation(bX, bT, bY):
		while 1:
			idx = range(len(bX))
        		np.random.shuffle(idx)
			batches = [[bX[i], bT[i], bY[i]] for i in idx]	
				
			for batchx, batcht, batchy in batches:
                		batchy = np.reshape(batchy,(1,1))
                		batchx = np.reshape(batchx,(1,batchx.shape[0],batchx.shape[1]))
				batcht = np.reshape(batcht,(1,batcht.shape[0],batcht.shape[1]))
				yield (batchx, [batcht,batchy])
				#yield (batchx, batchy)
	
	#model.load_weights("../models/rnn.h5")
	model.load_weights("../models/rnn_query2.h5")
	model.fit_generator(batch_generation(trainX, trainT, trainY), steps_per_epoch=len(trainX), 
			validation_data=batch_generation(testX, testT, testY), validation_steps=len(testX),
			epochs=0,callbacks=[checkpoint, earlyStopping])
	score = model.evaluate_generator(batch_generation(testX, testT, testY), steps=len(testX))
	print
        print "Score: ",
        print score
	#from keras.utils import plot_model
	#plot_model(model, to_file='model.png')	
        
	# load weights
	#model.load_weights("weights.best.hdf5")
	return model, score

