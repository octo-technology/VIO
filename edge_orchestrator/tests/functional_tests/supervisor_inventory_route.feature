Feature: The client requests the inventory available on the station

  Scenario: The client requests the inventory available on the station
    Given the app is up and running
    When the client requests the inventory
    Then the client receives the following inventory
    """
    {
    "cameras": [
      "fake"
    ],
    "models": {
      "inception": {
        "category": "classification",
        "version": 1,
        "class_names": [
          "OK",
          "KO"
        ],
        "image_resolution": [
          224,
          224
        ]
      },
      "marker_quality_control": {
        "category": "classification",
        "version": 1,
        "class_names": [
          "OK",
          "KO"
        ],
        "image_resolution": [
          224,
          224
        ]
      },
      "mask_classification_model": {
        "category": "classification",
        "version": 1,
        "class_names": [
          "OK",
          "KO"
        ],
        "image_resolution": [
          224,
          224
        ]
      },
      "mobilenet_v1_640x640": {
        "category": "object_detection",
        "version": 1,
        "model_type": "Mobilnet",
        "class_names_path": "test_detection_labels",
        "output": {
          "boxes_coordinates": "detection_boxes",
          "objectness_scores": "detection_scores",
          "number_of_boxes": "num_detections",
          "detection_classes": "detection_classes"
        },
        "objectness_threshold": 0.5
      },
      "mobilenet_v1_640x640_detect_classif": {
        "category": "object_detection_with_classification",
        "version": 1,
        "model_type": "Mobilnet",
        "class_names_path": "test_detection_labels",
        "output": {
          "boxes_coordinates": "detection_boxes",
          "objectness_scores": "detection_scores",
          "number_of_boxes": "num_detections",
          "detection_classes": "detection_classes"
        },
        "objectness_threshold": 0.5
      }
    },
    "camera_rules": [
      "expected_label_rule",
      "min_nb_objects_rule"
      ],
    "item_rules": [
      "threshold_ratio_rule",
      "min_threshold_KO_rule"
      ]
    }
    """
