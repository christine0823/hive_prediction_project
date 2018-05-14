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

def Keras_autoencoder(Mx, num_jobs):

        Mx = np.array(Mx)
        Mx_out = []
        for i in range(Mx.shape[1]):
                input_vec = Input(shape=(Mx.shape[2],))

                # encoder layers
                encoding_dim = 4
                mask = Masking(mask_value=0.0)(input_vec)
                encoded = Dense(24, activation='relu')(mask)
                encoded = Dense(16, activation='relu')(encoded)
		encoded = Dense(8, activation='relu')(encoded)
                encoder_output = Dense(encoding_dim)(encoded)

                # decoder layers
                decoded = Dense(8, activation='relu')(encoder_output)
                decoded = Dense(16, activation='relu')(decoded)
                decoded = Dense(24, activation='relu')(decoded)

                # construct the autoencoder model
                autoencoder = Model(input=input_vec, output=decoded)

                # construct the encoder model for plotting
                encoder = Model(input=input_vec, output=encoder_output)

                # compile autoencoder
                autoencoder.compile(optimizer='adam', loss='mse')

                # training
                autoencoder.fit(Mx[:,i,:], Mx[:,i,:], epochs=10, batch_size=16, verbose=1)
                out = encoder.predict(Mx[:,i,:])
                out = out.reshape(int(Mx.shape[0] / num_jobs), num_jobs*encoding_dim)
		Mx_out.append(out)

        return Mx_out[0], Mx_out[1]

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

