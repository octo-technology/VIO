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
        "model_type": "Mobilenet",
        "class_names_path": "test_detection_labels",
        "output": {
          "detection_boxes": "detection_boxes",
          "detection_scores": "detection_scores",
          "number_of_boxes": "num_detections",
          "detection_classes": "detection_classes"
        },
        "objectness_threshold": 0.5
      },
      "mobilenet_v1_640x640_detect_classif": {
        "category": "object_detection_with_classification",
        "version": 1,
        "model_type": "Mobilenet",
        "class_names_path": "test_detection_labels",
        "output": {
          "detection_boxes": "detection_boxes",
          "detection_scores": "detection_scores",
          "number_of_boxes": "num_detections",
          "detection_classes": "detection_classes"
        },
        "objectness_threshold": 0.5
      },
    "yolo_coco_nano": {
      "category": "object_detection",
      "version": 1,
      "class_names_path": "test_detection_labels_yolo",
      "model_type": "yolo",
      "output": {
        "detection_boxes": "detection_boxes",
        "detection_scores": "detection_scores",
        "detection_classes": "detection_classes"
      },
      "image_resolution": [
        320,
        320
      ],
      "objectness_threshold": 0.3
    }
    },
    "camera_rules": [
      "expected_label_rule",
      "min_nb_objects_rule"
      ],
    "item_rules": [
      "min_threshold_ok_ratio_rule",
      "min_threshold_ko_rule"
      ]
    }
    """
