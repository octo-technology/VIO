Feature: The client set an active configuration

	Scenario: The client request the active configuration which is unset
		Given the app is up and running
		When the client requests the active configuration
		Then the active configuration is
	"""
	{"detail": "No active configuration set"}
	"""

	Scenario: The client request all available configurations
		Given the app is up and running
		When the client requests all available configurations
		Then the client receives all available configurations
			| config_filepath                                  |
			| config/config_1.json  |
			| config/config_2.json |
			| config/config_3.json |

	Scenario: The client set a configuration as active
		Given the app is up and running
		When the client activates configuration 'config_1'
		Then the active configuration is
		"""
		{
		"station_name": "config_1",
		"camera_configs": {
		"camera_1": {
		"camera_id": "camera_1",
		"camera_type": "fake",
		"camera_instance_index": 0,
		"source_directory": "fake_images",
		"position": "front",
		"model_forwarder_config": {
		"model_name": "fake_model",
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
		"model_id": "fake_model_classification_1"
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
		"model_name": "fake_model",
		"model_type": "object_detection",
		"expected_image_resolution": {
		"width": 224,
		"height": 224
		},
		"model_version": "1",
		"class_names": [
		"OK",
		"KO"
		],
		"model_id": "fake_model_object_detection_1"
		},
		"camera_rule_config": {
		"camera_rule_type": "min_nb_objects_rule",
		"class_to_detect": "OK",
		"threshold": 1
		}
		}
		},
		"binary_storage_config": {
		"storage_type": "filesystem",
		"target_directory": "data_storage"
		},
		"metadata_storage_config": {
		"storage_type": "filesystem",
		"target_directory": "data_storage"
		},
		"item_rule_config": {
		"item_rule_type": "min_threshold_ratio_rule",
		"expected_decision": "OK",
		"threshold": 1
		}
		}
		"""
