"""Serializable normalization and reflection-padding layers."""

import tensorflow as tf
from tensorflow.keras import layers


@tf.keras.utils.register_keras_serializable(package="CycleGAN")
class InstanceNormalization(layers.Layer):
    def __init__(self, epsilon=1e-5, **kwargs):
        super().__init__(**kwargs)
        self.epsilon = epsilon

    def build(self, input_shape):
        channels = int(input_shape[-1])
        self.gamma = self.add_weight(name="gamma", shape=(channels,), initializer="ones", trainable=True)
        self.beta = self.add_weight(name="beta", shape=(channels,), initializer="zeros", trainable=True)
        super().build(input_shape)

    def call(self, inputs):
        mean, variance = tf.nn.moments(inputs, axes=[1, 2], keepdims=True)
        normalized = (inputs - mean) * tf.math.rsqrt(variance + self.epsilon)
        return self.gamma * normalized + self.beta

    def get_config(self):
        config = super().get_config()
        config.update({"epsilon": self.epsilon})
        return config


@tf.keras.utils.register_keras_serializable(package="CycleGAN")
class ReflectionPadding2D(layers.Layer):
    def __init__(self, padding=1, **kwargs):
        super().__init__(**kwargs)
        self.padding = padding

    def call(self, inputs):
        p = self.padding
        return tf.pad(inputs, [[0, 0], [p, p], [p, p], [0, 0]], mode="REFLECT")

    def compute_output_shape(self, input_shape):
        batch, height, width, channels = input_shape
        p = self.padding
        return (
            batch,
            height + 2 * p if height is not None else None,
            width + 2 * p if width is not None else None,
            channels,
        )

    def get_config(self):
        config = super().get_config()
        config.update({"padding": self.padding})
        return config
