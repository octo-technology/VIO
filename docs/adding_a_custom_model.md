# Adding a custom model to VIO

## Model export & VIO Configuration 
### Model format
The edge model serving supports models of 3 types : TensorFlow, TensorFlowLite and Torch.

This note will present how to add a custom TensorFlowLite model in VIO. The process is similar for the two other types,
for which you can follow the respective ReadMe files ([Torch serving](../edge_model_serving/torch_serving/README.md) and for 
[TensorFlow serving](../edge_model_serving/tf_serving/README.md)) and work in their respective edge sub-folder.

Comming soon: Integration with [Hugging Face](https://huggingface.co/) 

### Saving the model
The model has to be given to the Edge_serving module. Export your custom model to tflite and store it as 
`VIO/edge_model_serving/models/tflite/<model_folder_name>/<model_name>.tflite`. (If needed add a .txt file with the 
labels/class names)

The Edge_orchestrator has to know about the new model that is available. To do so, complete the inventory file 
`VIO/edge_orchestrator/config/inventory.json` with all the information required depending on you model type under the 
````models ```` category. Note that the model name variable should fit the model folder name. You can refer to [this subsection](edge_orchestrator.md#add-a-new-model).


### Creating the configuration files
Now that all the components know about your new model, you will need to create a configuration that will use your custom 
model. Create a new JSON file in `VIO/edge_orchestrator/config/station_configs` with any config name. You can follow the
configuration of this file in the [Add a new configuration](edge_orchestrator.md#add-a-new-configuration-) subsection.

## Adapting the code to your model - Optional

There are two layers of post-processing that may need to be edited to integrate your model. At the Edge Serving inference 
level & for the Edge Orchestrator reception.

- Detection model

The implemented methods are designed to support Mobilenet_SSD format, where the output of the model is 
`List[List[Boxes], List[Classes], List[Scores]]` and box format is `[ymin, xmin, ymax, xmax]`.

If your custom model doesn't fit this format, you can add custom post-processing methods.

The Edge Serving `VIO/edge_model_serving/tflite_serving/src/tflite_serving/api_routes.py` calling the model does a first 
treatment. Its purpose is separating model's output tensor into a dictionary of the final boxes coordinates, classes and
scores.

The results are then post processed at the Orchestrator `VIO/edge_orchestrator/edge_orchestrator/infrastructure/
model_forward/tf_serving_detection_wrapper.py` level to filter the detections of the desired classes and convert the box
coordinates to `Box: [xmin, ymin, xmax, ymax]` then converts the information into a dictionary having a key for each 
detection.

- Classification & other models

The process is exactly the same as for the detection model, the only difference will be at the Orchestrator level. 
Instead of modifying the `tf_serving_detection_wrapper.py` file select the file that corresponds to your model, 
modifying the `classification` or `detection_and_classification` wrappers. And you may not have to handle boxes coordinates.




