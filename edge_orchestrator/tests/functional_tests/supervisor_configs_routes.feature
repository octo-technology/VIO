Feature: The client set an active configuration

  Scenario: The client request the active configuration which is unset
    Given the app is up and running
    When the client requests the active configuration
    Then the active configuration is
    """
    null
    """

  Scenario: The client request all available configurations
    Given the app is up and running
    When the client requests all available configurations
    Then the client receives all available configurations
      | config_filepath                                  |
      | config/station_configs/station_config_TEST.json  |
      | config/station_configs/station_config_TEST2.json |

  Scenario: The client set a configuration as active
    Given the app is up and running
    When the client activates configuration 'station_config_TEST'
    Then the active configuration is
    """
    {
      "cameras": {
        "camera_id3": {
          "type": "fake",
          "source": "marker_images",
          "position": "back",
          "exposition": 100,
          "models_graph": {
            "model_id4": {
              "name": "marker_quality_control",
              "depends_on": []
            }
          },
          "camera_rule": {
            "name": "expected_label_rule",
            "parameters": {
              "expected_label": "OK"
            }
          }
        }
      },
      "item_rule": {
        "name": "min_threshold_KO_rule",
        "parameters": {
          "threshold": 1
        }
      }
    }
    """
