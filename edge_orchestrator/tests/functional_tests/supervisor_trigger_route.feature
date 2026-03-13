Feature: The client trigger a visual inspection and request the resulting metadata and binaries

	Scenario: The Client trigger a visual inspection
		Given the app is up and running
		And the config 'config_3' is activated
		And the following cameras are registered in the configuration
			| camera_id  | camera_type | position |
			| camera_1   | http        | front    |
			| camera_2   | http        | front    |
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
		"position": "front"
		},
		"camera_2": {
		"camera_id": "camera_2",
		"camera_type": "fake",
		"source_directory": "fake_images",
		"position": "front"
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
		"step_1": {
		"prediction_type": "class",
		"label": "KO",
		"probability": 0.94642
		},
		"step_2": {
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
		"step_1": "KO",
		"step_2": "KO"
		},
		"decision": "KO",
		"state": "DONE"
		}
		"""
		And the item binaries are stored
			| binary_name | binary_extension |
			| camera_1    | jpg              |
			| camera_2    | jpg              |
