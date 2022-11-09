from supervisor.domain.models.camera import get_last_inference_by_camera, get_camera_rule
from supervisor.domain.use_cases.supervisor import get_labels


class TestCameraBusinessRule:
    def test_camera_decision_should_return_KO_when_expected_label_is_OK(self):  # noqa
        # Given
        inferences = {'camera_id3': {'model_id4': {'full_image': {'label': 'KO', 'probability': 0.999930501}}}}

        # When
        camera_decisions = {}
        for camera in inferences:
            camera_rule_name = 'expected_label_rule'
            camera_rule_parameters = {"expected_label": ["OK"]}

            last_model_inferences = get_last_inference_by_camera(inferences[camera])
            labels_of_last_model_inferences = get_labels(last_model_inferences)

            item_camera_rule = get_camera_rule(camera_rule_name)(**camera_rule_parameters)
            camera_decision = item_camera_rule.get_camera_decision(labels_of_last_model_inferences)

            camera_decisions[f'{camera}'] = camera_decision.value

        # Then
        assert camera_decisions == {'camera_id3': 'KO'}

    def test_camera_decision_should_return_OK_when_minimum_one_person_is_detected(self):  # noqa
        # Given
        inferences = {
            'camera_id3': {
                'model_id5': {
                    'object_1': {
                        'location': [155, 413, 381, 709], 'score': 0.773778856, 'label': 'person'},
                    'object_2': {
                        'location': [422, 10, 719, 720], 'score': 0.709803939, 'label': 'bicycle'},
                    'object_3': {
                        'location': [623, 430, 757, 648], 'score': 0.523171604,
                        'label': 'couch'}
                }
            }
        }

        # When
        camera_decisions = {}
        for camera in inferences:
            camera_rule_name = 'min_nb_objects_rule'
            camera_rule_parameters = {
                "class_to_detect": ["person"],
                "min_threshold": 1
            }

            last_model_inferences = get_last_inference_by_camera(inferences[camera])
            labels_of_last_model_inferences = get_labels(last_model_inferences)

            item_camera_rule = get_camera_rule(camera_rule_name)(**camera_rule_parameters)
            camera_decision = item_camera_rule.get_camera_decision(labels_of_last_model_inferences)

            camera_decisions[f'{camera}'] = camera_decision.value

        # Then
        assert camera_decisions == {'camera_id3': 'OK'}

        def test_camera_decision_should_return_OK_when_minimum_one_face_is_detected_with_two_object_detection_models(self):  # noqa
            # Given
            inferences = {
                'camera_id3': {
                    {'model_id1': {
                        'object_1': {'label': 'person', 'location': [351, 110, 508, 361], 'score': 0.98046875},
                        'object_2': {'label': 'person', 'location': [233, 73, 385, 397], 'score': 0.91015625},
                        'object_3': {'label': 'person', 'location': [7, 3, 240, 509], 'score': 0.87890625},
                        'object_4': {'label': 'person', 'location': [493, 93, 678, 389], 'score': 0.87890625},
                        'object_5': {'label': 'person', 'location': [135, 35, 276, 417], 'score': 0.83984375},
                        'object_6': {'label': 'person', 'location': [520, 47, 804, 527], 'score': 0.58203125}},
                     'model_id6': {'object_1': {'label': 'face', 'location': [555, 97, 611, 207], 'score': 0.98046875},
                                   'object_2': {'label': 'face', 'location': [645, 46, 727, 180], 'score': 0.5}}}
                }
            }

            # When
            camera_decisions = {}
            camera = 'camera_id3'
            camera_rule_name = 'min_nb_objects_rule'
            camera_rule_parameters = {
                "class_to_detect": ["face"],
                "min_threshold": 1
            }

            item_camera_rule = get_camera_rule(camera_rule_name)(**camera_rule_parameters)
            camera_decision = item_camera_rule.get_camera_decision(inferences[camera])

            camera_decisions[f'{camera}'] = camera_decision.value

            # Then
            assert camera_decisions == {'camera_id3': 'OK'}


        def test_camera_decision_should_return_OK_when_minimum_one_connected_cellphone_is_detected_with_one_object_detection_and_one_classification_model(self):  # noqa
            # Given
            inferences = {'camera_id1': {'model_id1': {
                'object_3': {'label': 'cell phone', 'location': [427, 227, 467, 278], 'score': 0.41796875}},
                                         'model_id6': {
                                             'object_3': {'label': 'unconnected', 'probability': 0.9975850582122803}}}}

            # When
            camera_decisions = {}
            camera = 'camera_id1'
            camera_rule_name = 'min_nb_objects_rule'
            camera_rule_parameters = {
                "class_to_detect": ["connected"],
                "min_threshold": 1
            }

            item_camera_rule = get_camera_rule(camera_rule_name)(**camera_rule_parameters)
            camera_decision = item_camera_rule.get_camera_decision(inferences[camera])

            camera_decisions[f'{camera}'] = camera_decision.value

            # Then
            assert camera_decisions == {'camera_id1': 'KO'}
