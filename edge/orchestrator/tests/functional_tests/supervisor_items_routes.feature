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
	"camera_type": "http",
	"position": "front",
	"service_url": "http://localhost:8001"
	},
	"camera_2": {
	"camera_id": "camera_2",
	"camera_type": "http",
	"position": "front",
	"service_url": "http://localhost:8001"
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

	Scenario: The Client reads one specific item picture
		Given the app is up and running
		And the config 'config_3' is activated
		And item 'item_id' is stored
		When one item 'item_id' binary from camera 'camera_2' is requested
		Then one item 'item_id' binary from camera 'camera_2' is read
