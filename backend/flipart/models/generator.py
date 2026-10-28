"""ResNet-6 generator architecture used during training."""

import tensorflow as tf
from tensorflow.keras import layers, Model

from ..config import IMAGE_SIZE
from .layers import InstanceNormalization, ReflectionPadding2D

NUM_RESIDUAL_BLOCKS = 6


def weight_initializer():
    return tf.keras.initializers.RandomNormal(mean=0.0, stddev=0.02)


def residual_block(x, filters=256):
    shortcut = x
    x = ReflectionPadding2D(1)(x)
    x = layers.Conv2D(filters, kernel_size=3, padding="valid", kernel_initializer=weight_initializer())(x)
    x = InstanceNormalization()(x)
    x = layers.ReLU()(x)
    x = ReflectionPadding2D(1)(x)
    x = layers.Conv2D(filters, kernel_size=3, padding="valid", kernel_initializer=weight_initializer())(x)
    x = InstanceNormalization()(x)
    return layers.Add()([shortcut, x])


def build_generator(name, num_residual_blocks=6):
    inputs = layers.Input(shape=(IMAGE_SIZE, IMAGE_SIZE, 3))
    x = ReflectionPadding2D(3)(inputs)
    x = layers.Conv2D(64, kernel_size=7, padding="valid", kernel_initializer=weight_initializer())(x)
    x = InstanceNormalization()(x)
    x = layers.ReLU()(x)
    for filters in [128, 256]:
        x = layers.Conv2D(filters, kernel_size=3, strides=2, padding="same", kernel_initializer=weight_initializer())(x)
        x = InstanceNormalization()(x)
        x = layers.ReLU()(x)
    for _ in range(num_residual_blocks):
        x = residual_block(x, filters=256)
    for filters in [128, 64]:
        x = layers.Conv2DTranspose(filters, kernel_size=3, strides=2, padding="same", kernel_initializer=weight_initializer())(x)
        x = InstanceNormalization()(x)
        x = layers.ReLU()(x)
    x = ReflectionPadding2D(3)(x)
    outputs = layers.Conv2D(3, kernel_size=7, padding="valid", activation="tanh", kernel_initializer=weight_initializer())(x)
    return Model(inputs, outputs, name=name)
