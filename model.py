#!/usr/bin/env python3
"""   
(c) Research Group CAMMA, University of Strasbourg, IHU Strasbourg, France
Website: http://camma.u-strasbg.fr
"""

import tensorflow as tf
import os


def preprocess(image, shape=[64, 64]):
    image = tf.cast(image, tf.float32)
    image = tf.image.resize(image, shape)
    image = tf.reshape(image, shape + [3])
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    return tf.expand_dims(image, 0)


def build_model(input_shape=[64, 64]):

    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Input(input_shape +[3], dtype = tf.float32))

    model.add(tf.keras.applications.MobileNetV2(
                input_shape=input_shape+[3],
                alpha=1.0,
                include_top=False,
                weights=None))
                
    model.add(tf.keras.layers.Flatten())

    model.add(tf.keras.layers.LayerNormalization())
    
    model.add(tf.keras.layers.Dropout(0))

    model.add(tf.keras.layers.Lambda(lambda x: tf.expand_dims(x, 0)))

    model.add(tf.keras.layers.LSTM(units=640, return_sequences=True, stateful=True))
    
    model.add(tf.keras.layers.LayerNormalization())

    model.add(tf.keras.layers.Dense(1, activation='sigmoid'))

    return model
