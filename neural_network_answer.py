import numpy as np
import os.path
from PIL import Image
from tensorflow import keras
import tensorflow as tf # tensorflow 2.0


def check(img, answer):
    model = keras.models.load_model('model')
    data = np.asarray(img, dtype='uint8')
    gray_data = [[0 for i in range(28)] for j in range(28)]
    for y in range(28):
        for x in range(28):
            gray_data[y][x] = (int(data[y, x, 0]) + int(data[y, x, 1]) + int(data[y, x, 2]))/3
    gray_data = np.array(gray_data)
    prediction_list = model.predict(gray_data.reshape((1, 28, 28, 1))).tolist()[0] #weight synapse
    if max(prediction_list) == prediction_list[answer]:
        return True
    return False