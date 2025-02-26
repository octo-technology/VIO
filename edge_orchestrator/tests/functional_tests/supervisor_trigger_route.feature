Feature: The client trigger a visual inspection and request the resulting metadata and binaries

	Scenario: The Client trigger a visual inspection
		Given the app is up and running
		And the config 'config_3' is activated
		And the following cameras are registered in the configuration
			| camera_id  | camera_type | position | source_directory                                      |
			| camera_1   | fake        | front    | fake_images |
			| camera_2   | fake        | front    | fake_images |
		When the client triggers a visual inspection
		Then item metadata are like the following
		"""
		{
		"id": "[a-z0-9-_]{36}",
		"creation_date": "2025-02-10T14:02:28.097549",
		"cameras_metadata": {
		"camera_1": {
		"camera_id": "camera_1",
		"camera_type": "fake",
		"source_directory": "fake_images",
		"position": "front",
		"model_forwarder_config": {
		"model_name": "pin_detection",
		"model_type": "classification",
		"expected_image_resolution": {
		"width": 224,
		"height": 224
		},
		"model_version": "1",
		"class_names": [
		"OK",
		"KO"
		],
		"model_serving_url": "http://0.0.0.0:8501/",
		"recreate_me": false,
		"model_id": "pin_detection_classification_1"
		},
		"camera_rule_config": {
		"camera_rule_type": "expected_label_rule",
		"expected_class": "OK",
		"recreate_me": false
		},
		"recreate_me": false
		},
		"camera_2": {
		"camera_id": "camera_2",
		"camera_type": "fake",
		"source_directory": "fake_images",
		"position": "front",
		"model_forwarder_config": {
		"model_name": "mobilenet_ssd_v2_coco",
		"model_type": "object_detection",
		"expected_image_resolution": {
		"width": 300,
		"height": 300
		},
		"model_version": "1",
		"class_names": [],
		"class_names_filepath": "model_labels/imagenet_labels.txt",
		"model_serving_url": "http://0.0.0.0:8501/",
		"recreate_me": false,
		"model_id": "mobilenet_ssd_v2_coco_object_detection_1"
		},
		"camera_rule_config": {
		"camera_rule_type": "min_nb_objects_rule",
		"class_to_detect": "OK",
		"threshold": 1,
		"recreate_me": false
		},
		"recreate_me": false
		}
		},
		"binaries": {
		"camera_1": {
		"creation_date": "2025-02-10T14:02:28.106651",
		"storing_path": "/tmp/tmpza91f2gn/data_storage/cb5e2fac-4a6f-49f2-bd82-2bb951ea5b19/camera_1.jpg"
		},
		"camera_2": {
		"creation_date": "2025-02-10T14:02:28.107943",
		"storing_path": "/tmp/tmpza91f2gn/data_storage/cb5e2fac-4a6f-49f2-bd82-2bb951ea5b19/camera_2.jpg"
		}
		},
		"predictions": {
		"camera_1": {
		"prediction_type": "class",
		"label": "KO",
		"probability": 0.9464232325553894
		},
		"camera_2": {
		"prediction_type": "objects",
		"detected_objects": {
		"object_1": {
		"location": [
		0.36,
		0.6234,
		0.6545,
		0.817
		],
		"objectness": 0.58203125,
		"label": "motorcycle"
		},
		"...": {}
		}
		}
		},
		"camera_decisions": {
		"camera_1": "KO",
		"camera_2": "KO"
		},
		"decision": "KO",
		"state": "DONE"
		}
		"""
		And the item binaries are stored
			| binary_name | binary_extension |
			| camera_1    | jpg              |
			| camera_2    | jpg              |