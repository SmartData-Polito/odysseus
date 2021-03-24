from keras.optimizers import Adam
from keras.models import Model
from keras.layers import (
    Input, Dense, Conv3D, Flatten, Dropout, MaxPooling3D,
    Activation, Lambda, Reshape, Concatenate, LSTM
)
from functools import reduce
from keras.backend import sigmoid
import numpy as np


def swish(x, beta = 1):
    return (x * sigmoid(beta * x))

def CLoST3D(X_train, conv_filt = 64, kernel_sz = (2, 3, 3),
            mask = np.empty(0),
            lstm = None, lstm_number = 0,
            add_external_info = False, conv_block=2):

    # Input:
    # - mask: np.array. Filter that is applied to the data output to the model. If not passed, no filter is applied
    # - lstm: int. Parameter to pass to the LSTM layer. If equal to None, the LSTM layer is not added.
    # - add_external_info: bool. Parameter to insert external information or not.

    X_train, ext_train = X_train # split flow volumes and ext features

    main_inputs = []

    start = Input(shape= (X_train.shape[1], X_train.shape[2] , X_train.shape[3], 2))

    main_inputs.append(start)
    main_output = main_inputs[0]

    x = Conv3D(conv_filt / 2, kernel_size = kernel_sz, activation='relu')(main_output)
    x = MaxPooling3D(pool_size=(1, 2, 2))(x)
    for i in range(conv_block-1):
        x = Dropout(0.25)(x)
        x = Conv3D(conv_filt, kernel_size = kernel_sz, activation='relu', padding = 'same')(x)
        x = MaxPooling3D(pool_size=(1, 2, 2))(x)
    x = Flatten()(x)
    x = Dense(128,  activation = 'relu') (x)
    if lstm != None:
      x = Reshape((x.shape[1], 1))(x)
      for num in range(lstm_number):
          x = LSTM(int(lstm/(num+1)), return_sequences=True)(x)
    x = Flatten()(x)
    if add_external_info:
      external_input = Input(shape=ext_train.shape[1:])
      main_inputs.append(external_input)
      x_ext = Dense(units=10, activation='relu')(external_input)
      x_ext = Dense(units=reduce(lambda e1, e2: e1*e2, X_train.shape[2:]), activation='relu')(x_ext)
      x = Concatenate(axis = -1)([x, x_ext])
    x = Dense(reduce(lambda e1, e2: e1*e2, X_train.shape[2:]))(x)
    x = Reshape(X_train.shape[2:])(x)
    x = Activation(swish)(x)
    if mask.shape[0] != 0:
      x = Lambda(lambda el: el * mask)(x)
    model = Model(main_inputs, x)
    return model

def inverse_transform(X, max):
    X = 1. * X * (max - 0) + 0
    return X

def denormalization(X, max):
    # shape = (N , M, 2)
    X = inverse_transform(X, max)
    return X

def build_model(X_train, X_test, conv_filt, kernel_sz, mask, lstm, lstm_number,
    add_external_info, conv_block, path, max, lr=0.0001):
    #X_train mi servono per definire le dimensioni dell'output
    model = CLoST3D(X_train, conv_filt, kernel_sz, mask, lstm, lstm_number, add_external_info, conv_block)
    model.load_weights(path)
    # predict
    Y_pred = denormalization(model.predict(X_test), max) # compute predictions e denormalization

    return Y_pred



#def model_prediction
