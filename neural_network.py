import numpy as np
import os.path
import imageio
from PIL import Image
from tensorflow import keras
import tensorflow as tf # tensorflow 2.0


def get_input_array(root):
    folder_names = os.listdir(path=root)
    folders = []
    px_learning_data = []
    test = []
    ytest = []
    for i in range(len(folder_names)):
        test_num = 0
        name = folder_names[i]
        hieroglyphs = os.listdir(path=(root + '/' + name))
        for j in range(len(hieroglyphs)):
            if hieroglyphs[j][-4:] != '.png':
                continue
            if test_num < 10:
                test.append([[0 for x in range(28)] for j in range(28)])
                ytest.append(folder_hier_accordance[name])
            else:
                px_learning_data.append([[0 for x in range(28)] for j in range(28)])
                folders.append(folder_hier_accordance[name])
            img_name = root + '/' + name + '/' + hieroglyphs[j]
            data = imageio.imread(img_name, pilmode='RGB')
            for y in range(28):
                for x in range(28):
                    if test_num < 10:
                        test[-1][y][x] = (int(data[y, x, 0]) + int(data[y, x, 1]) + int(data[y, x, 2]))/3
                    else:
                        px_learning_data[-1][y][x] = (int(data[y, x, 0]) + int(data[y, x, 1]) + int(data[y, x, 2]))/3
            test_num += 1
    folders = np.array(folders)
    ytest = np.array(ytest)
    px_learning_data = np.array(px_learning_data)
    test = np.array(test)
    return px_learning_data, folders, test, ytest


folder_hier_accordance = {'一' : 1, '二' : 2, '两': 0, '三': 3, '四' : 4, '五' : 5, '六' : 6, '七' : 7, '八' : 8, '九' : 9, '十' : 10, '百' : 11, '千' : 12}
path = './include'
seed = 0
np.random.seed(seed) #adding entropy to np
tf.compat.v1.random.set_random_seed(seed) #more random to tf
num_classes = len(folder_hier_accordance)
img_rows, img_cols = 28, 28

X_train, Y_train, X_test, Y_test = get_input_array(path)
X_train = X_train.astype('float32')
X_test = X_test.astype('float32')

X_train = X_train.reshape((X_train.shape[0], img_rows, img_cols, 1)) 
X_test = X_test.reshape((X_test.shape[0], img_rows, img_cols, 1))

Y_train = Y_train.astype('float32')
Y_test = Y_test.astype('float32')

X_train /= 255 #normalization
X_test /= 255
Y_train = keras.utils.to_categorical(Y_train, num_classes) #making matrix
Y_test = keras.utils.to_categorical(Y_test, num_classes)

from keras.models import Sequential #training mode
from keras.layers import Dense, Conv2D, Flatten #neuron data types
from keras.layers import MaxPooling2D, Dropout #neuron data types

#thoughtless_copypaste
#it was used for initialization. now i can improve it with saved model
'''model = Sequential()
model.add(Conv2D(32, kernel_size=(5, 5),
                     activation='relu',
                     input_shape=(img_rows, img_cols, 1)))

model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(64, (5, 5), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Flatten())
model.add(Dense(1024, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, Y_train, validation_data=(X_test, Y_test), epochs=3)
score = model.evaluate(X_test, Y_test, verbose=1)
print()
print('Test loss:', score[0])
print('Test accuracy:', score[1])'''

model = keras.models.load_model('model')
model.fit(X_train, Y_train, validation_data=(X_test, Y_test), epochs=3)
score = model.evaluate(X_test, Y_test, verbose=1)
print()
print('Test loss:', score[0])
print('Test accuracy:', score[1])
model.save('model')