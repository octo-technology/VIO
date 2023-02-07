import tensorflow as tf
import os

model_name = 'mask_classification_model'
saved_model_dir = f'model_serving/{model_name}/1'

# Converting a SavedModel to a TensorFlow Lite model.
converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)  # path to the SavedModel directory
tflite_model = converter.convert()

tflite_model_dir = f'tflite_serving/{model_name}'
if not os.path.exists(tflite_model_dir):
    os.mkdir(tflite_model_dir)

# Save the model.
with open(f'{tflite_model_dir}/model.tflite', 'wb') as f:
    f.write(tflite_model)

# reduce the size of a floating point model by quantizing the weights to float16
quantization = False
if quantization:
    converter.optimizations = [tf.lite.Optimize.OPTIMIZE_FOR_LATENCY]
    converter.target_spec.supported_types = [tf.float16]
    tflite_quant_model = converter.convert()

    with open(f'{tflite_model_dir}/model_quant.tflite', 'wb') as f:
        f.write(tflite_quant_model)
