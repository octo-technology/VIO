from _pytest.fixtures import fixture


@fixture(scope="function")
def test_items_config():
    return {
        "test_item_category_A": {
            "camera_id1": {
                "business_rule": {"shape": "square", "threshold": 0.02},
                "models_graph": {
                    "model_1": {
                        "depends_on": [],
                        "metadata": {
                            "category": "classification",
                            "name": "inception",
                            "version": "1",
                        },
                    }
                },
                "settings": {
                    "exposition": 100,
                    "position": "front_camera",
                    "type": "fake",
                },
            },
            "camera_id2": {
                "business_rule": {"shape": "square", "threshold": 0.02},
                "models_graph": {
                    "model_1": {
                        "depends_on": [],
                        "metadata": {
                            "category": "object_detection_with_classification",
                            "name": "yolov3_harnais",
                            "version": "1",
                        },
                    }
                },
                "settings": {
                    "exposition": 100,
                    "position": "left_camera",
                    "type": "fake",
                },
            },
            "camera_id3": {
                "business_rule": {"shape": "square", "threshold": 0.02},
                "models_graph": {
                    "model_1": {
                        "depends_on": [],
                        "metadata": {
                            "category": "object_detection",
                            "name": "yolov3_harnais",
                            "version": "1",
                        },
                    },
                    "model_2": {
                        "depends_on": ["model_1"],
                        "metadata": {
                            "category": "classification",
                            "name": "inception",
                            "version": "1",
                        },
                    },
                },
                "settings": {
                    "exposition": 100,
                    "position": "right_camera",
                    "type": "fake",
                },
            },
            "camera_id4": {
                "business_rule": {"shape": "square", "threshold": 0.02},
                "models_graph": {
                    "model_1": {
                        "depends_on": [],
                        "metadata": {
                            "category": "object_detection",
                            "name": "yolov3_harnais",
                            "version": "1",
                        },
                    },
                    "model_2": {
                        "depends_on": ["model_1"],
                        "metadata": {
                            "category": "classification",
                            "name": "inception",
                            "version": "1",
                        },
                    },
                },
                "settings": {
                    "exposition": 100,
                    "position": "back_camera",
                    "type": "fake",
                },
            },
        },
        "test_item_category_B": {
            "camera_id1": {
                "business_rule": {"shape": "square", "threshold": 0.02},
                "models_graph": {
                    "model_1": {
                        "depends_on": [],
                        "metadata": {
                            "category": "object_detection",
                            "name": "yolov3_harnais",
                            "version": "1",
                        },
                    },
                    "model_2": {
                        "depends_on": ["model_1"],
                        "metadata": {
                            "category": "classification",
                            "name": "inception",
                            "version": "1",
                        },
                    },
                },
                "settings": {
                    "exposition": 100,
                    "position": "right_camera",
                    "type": "fake",
                },
            }
        },
    }
