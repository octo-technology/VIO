Feature: The client request metadata and binaries

	Scenario: The Client reads all items metadata
		Given the app is up and running
		And the config 'config_3' is activated
		When the client requests the items metadata list
		Then the client receives the items metadata list

	Scenario: The Client reads one specific item metadata
		Given the app is up and running
		And the config 'config_3' is activated
		And item 'item_id' is stored
		When the item 'item_id' metadata is requested
		Then the item 'item_id' metadata is read
	"""
	{
	"id": "[a-z0-9-_]{36}",
	"creation_date": "2025-02-10T14:02:28.097549",
	"cameras_metadata": {
	"camera_1": {
	"camera_id": "camera_1",
	"camera_type": "fake",
	"camera_instance_index": 0,
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
	"model_id": "pin_detection_classification_1"
	},
	"camera_rule_config": {
	"camera_rule_type": "expected_label_rule",
	"expected_class": "OK"
	}
	},
	"camera_2": {
	"camera_id": "camera_2",
	"camera_type": "fake",
	"camera_instance_index": 0,
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
	"model_id": "mobilenet_ssd_v2_coco_object_detection_1"
	},
	"camera_rule_config": {
	"camera_rule_type": "min_nb_objects_rule",
	"class_to_detect": "OK",
	"threshold": 1
	}
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
	"probability": 0.94642
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
	"objectness": 0.58203,
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

	Scenario: The Client reads one specific item picture
		Given the app is up and running
		And the config 'config_3' is activated
		And item 'item_id' is stored
		When one item 'item_id' binary from camera 'camera_2' is requested
		Then one item 'item_id' binary from camera 'camera_2' is read
