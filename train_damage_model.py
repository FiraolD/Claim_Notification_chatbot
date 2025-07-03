from tensorflow.keras.preprocessing.image import ImageDataGenerator
from keras.applications import MobileNetV2
from keras import layers, models, optimizers
import os

# Path to your dataset
dataset_dir = 'car_damage_dataset'

# Parameters
img_size = 224
batch_size = 32
epochs = 10

# Create train/validation split
datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)

train_gen = datagen.flow_from_directory(
    dataset_dir,
    target_size=(img_size, img_size),
    batch_size=batch_size,
    class_mode='categorical',
    subset='training'
)

val_gen = datagen.flow_from_directory(
    dataset_dir,
    target_size=(img_size, img_size),
    batch_size=batch_size,
    class_mode='categorical',
    subset='validation'
)

print("Found", train_gen.samples, "training images in", train_gen.num_classes, "classes")
print("Found", val_gen.samples, "validation images in", val_gen.num_classes, "classes")

# Load pre-trained MobileNetV2 without top layer
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(img_size, img_size, 3))
base_model.trainable = False  # Freeze base model for feature extraction

# Build new model on top
model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(train_gen.num_classes, activation='softmax')
])

model.compile(
    optimizer=optimizers.Adam(learning_rate=1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

history = model.fit(
    train_gen,
    epochs=epochs,
    validation_data=val_gen
)
model.save("car_damage_classifier.h5")
print("Model saved as car_damage_classifier.h5")