from functools import reduce

import numpy as np
from keras.backend import sigmoid
from keras.layers import (
    Input, Dense, Conv3D, Flatten, Dropout, MaxPooling3D,
    Activation, Lambda, Reshape, Concatenate, LSTM
)
from keras.models import Model


from odysseus.utils.time_utils import weekday2vec

class PredictionModel:

    def __init__(self, prediction_model_config, flow_volumes_shape, ext_train_shape, mask, path):
        # Model creationreduce(lambda e1, e2: e1 * e2, X_train.shape[2:])
        self.model = CLoST3D(prediction_model_config["past_window"],
                             flow_volumes_shape, ext_train_shape,
                             prediction_model_config["conv_filt"],
                             tuple(prediction_model_config["kernel_sz"]),
                             mask,
                             prediction_model_config["lstm"],
                             prediction_model_config["lstm_number"],
                             prediction_model_config["add_external_info"],
                             prediction_model_config["conv_block"])
        # Load model weights
        self.model.load_weights(path)

    def predict(self, X_test, max):
        # predict
        Y_pred = denormalization(self.model.predict(X_test), max)  # compute predictions e denormalization
        return Y_pred


def swish(x, beta=1):
    return (x * sigmoid(beta * x))


def CLoST3D(past_window, flow_volumes_shape, ext_train_shape, conv_filt=64, kernel_sz=(2, 3, 3),
            mask=np.empty(0),
            lstm=None, lstm_number=0,
            add_external_info=False, conv_block=2):
    # Input:
    # - mask: np.array. Filter that is applied to the data output to the model. If not passed, no filter is applied
    # - lstm: int. Parameter to pass to the LSTM layer. If equal to None, the LSTM layer is not added.
    # - add_external_info: bool. Parameter to insert external information or not.

    main_inputs = []
    # X_train.shape[1] = fa riferimento ai tensori concatenati quindi dipende da quante ore precedenti consideriamo
    # variabile da inserire in configurazione
    start = Input(shape=(past_window, flow_volumes_shape[0], flow_volumes_shape[1], 2))

    main_inputs.append(start)
    main_output = main_inputs[0]

    x = Conv3D(conv_filt / 2, kernel_size=kernel_sz, activation='relu')(main_output)
    x = MaxPooling3D(pool_size=(1, 2, 2))(x)
    for i in range(conv_block - 1):
        x = Dropout(0.25)(x)
        x = Conv3D(conv_filt, kernel_size=kernel_sz, activation='relu', padding='same')(x)
        x = MaxPooling3D(pool_size=(1, 2, 2))(x)
    x = Flatten()(x)
    x = Dense(128, activation='relu')(x)
    if lstm is not None:
        x = Reshape((x.shape[1], 1))(x)
        for num in range(lstm_number):
            x = LSTM(int(lstm / (num + 1)), return_sequences=True)(x)
    x = Flatten()(x)
    if add_external_info:
        external_input = Input(shape=(ext_train_shape,))
        main_inputs.append(external_input)
        x_ext = Dense(units=10, activation='relu')(external_input)
        x_ext = Dense(units=reduce(lambda e1, e2: e1 * e2, (flow_volumes_shape[0], flow_volumes_shape[1], 2)), activation='relu')(x_ext)
        x = Concatenate(axis=-1)([x, x_ext])
    x = Dense(reduce(lambda e1, e2: e1 * e2, (flow_volumes_shape[0], flow_volumes_shape[1], 2)))(x)
    x = Reshape((flow_volumes_shape[0], flow_volumes_shape[1], 2))(x)
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



