Feature: The client trigger a visual inspection and request the resulting metadata and binaries

  Scenario: The Client trigger a visual inspection
    Given the app is up and running
    And the config 'station_config_TEST' is activated
    And the following cameras are registered in the configuration
      | camera_id  | camera_type | input_images_folder |
      | camera_id3 | fake        | marker_images       |
    When the client triggers a visual inspection
    Then item metadata like the following are captured
    """
    {
      "id": "[a-z0-9-_]{36}",
      "cameras": {
        "camera_id3": {
          "brightness": null,
          "exposition": 100,
          "position": "back",
          "input_images_folder": "marker_images"
        }
      },
      "category": "category",
      "decision": null,
      "inferences": {},
      "received_time": "%Y-%m-%d %H:%M:%S",
      "serial_number": "serial_number",
      "state": "Capture|Save Binaries|Inference|Decision|Done",
      "station_config": "station_config_TEST"
    }
    """
    And the item binaries are stored
      | binary_name | binary_extension |
      | camera_id3  | jpg              |
    And the item inference is computed
    """
    {
      "id": "[a-z0-9-_]{36}",
      "cameras": {
        "camera_id3": {
          "brightness": null,
          "exposition": 100,
          "position": "back",
          "input_images_folder": "marker_images"
        }
      },
      "category": "category",
      "inferences": {
        "camera_id3": {
          "model_id4": {
            "full_image": {
              "label": "OK|KO",
              "probability": "[0-9.]+"
            }
          }
        }
      },
      "received_time": "%Y-%m-%d %H:%M:%S",
      "serial_number": "serial_number",
      "state": "Capture|Save Binaries|Inference|Decision|Done",
      "station_config": "station_config_TEST"
    }
    """
    And the item decision is made
    """
    {
      "id": "[a-z0-9-_]{36}",
      "cameras": {
        "camera_id3": {
          "brightness": null,
          "exposition": 100,
          "position": "back",
          "input_images_folder": "marker_images"
        }
      },
      "category": "category",
      "decision": "OK|KO",
      "inferences": {
        "camera_id3": {
          "model_id4": {
            "full_image": {
              "label": "OK|KO",
              "probability": "[0-9.]+"
            }
          }
        }
      },
      "received_time": "%Y-%m-%d %H:%M:%S",
      "serial_number": "serial_number",
      "state": "Capture|Save Binaries|Inference|Decision|Done",
      "station_config": "station_config_TEST"
    }
    """
    And the item state is set to done
    """
    {
      "id": "[a-z0-9-_]{36}",
      "cameras": {
        "camera_id3": {
          "brightness": null,
          "exposition": 100,
          "position": "back",
          "input_images_folder": "marker_images"
        }
      },
      "category": "category",
      "decision": "OK|KO",
      "inferences": {
        "camera_id3": {
          "model_id4": {
            "full_image": {
              "label": "OK|KO",
              "probability": "[0-9.]+"
            }
          }
        }
      },
      "received_time": "%Y-%m-%d %H:%M:%S",
      "serial_number": "serial_number",
      "state": "Done",
      "station_config": "station_config_TEST"
    }
    """
    And the item metadata are stored
    And a telemetry message is stored
