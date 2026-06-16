"""
Arquiteturas CNN para classificação de imagens ECG — Fase 4 CardioIA.
"""

from __future__ import annotations

from tensorflow import keras
from tensorflow.keras import layers


def build_cnn_simples(
    input_shape: tuple[int, int, int] = (224, 224, 3),
    num_classes: int = 5,
) -> keras.Model:
    """CNN convolucional simples treinada do zero."""
    inputs = keras.Input(shape=input_shape)
    x = layers.Conv2D(32, (3, 3), activation="relu", padding="same")(inputs)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Conv2D(64, (3, 3), activation="relu", padding="same")(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Conv2D(128, (3, 3), activation="relu", padding="same")(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Flatten()(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.4)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = keras.Model(inputs, outputs, name="ecg_cnn_simples")
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def build_transfer_learning(
    num_classes: int = 5,
    input_shape: tuple[int, int, int] = (224, 224, 3),
    backbone: str = "vgg16",
    trainable_base: bool = False,
) -> keras.Model:
    """Transfer learning com VGG16 ou ResNet50 (ImageNet)."""
    if backbone == "vgg16":
        base = keras.applications.VGG16(
            include_top=False,
            weights="imagenet",
            input_shape=input_shape,
            pooling="avg",
        )
    elif backbone == "resnet50":
        base = keras.applications.ResNet50(
            include_top=False,
            weights="imagenet",
            input_shape=input_shape,
            pooling="avg",
        )
    else:
        raise ValueError(f"Backbone não suportado: {backbone}")

    base.trainable = trainable_base

    inputs = keras.Input(shape=input_shape)
    x = base(inputs, training=False)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = keras.Model(inputs, outputs, name=f"ecg_{backbone}_transfer")
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-4),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model
