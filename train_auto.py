import tensorflow as tf
import matplotlib.pyplot as plt

from tensorflow.keras.datasets import mnist
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.models import Sequential

#seven days data in numpy file
x_train = numpy.load(sensor_data.npy)

model = Sequential([
  Dense(4,'relu')
  Dense(3, 'relu'),
  Dense(2, 'relu'),
  Dense(3, 'relu'),
  Dense(4, 'relu'),
  Dense(5,'relu')
])

model.compile(optimizer='adam',
              loss='mse')

history = model.fit(x_train, x_train, epochs=10)
model.save_weights("model2.h5")


