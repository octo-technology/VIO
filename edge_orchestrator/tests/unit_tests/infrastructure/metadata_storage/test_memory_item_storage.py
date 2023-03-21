from edge_orchestrator.infrastructure.metadata_storage.memory_metadata_storage import MemoryMetadataStorage


class TestMemoryItemStorage:
    def test_save_item_metadata_should_write_item_in_memory(self, my_item_0):
        # Given
        metadata_storage = MemoryMetadataStorage()

        # When
        metadata_storage.save_item_metadata(my_item_0)

        # Then
        assert metadata_storage.items_metadata == {
            my_item_0.id: {
                'id': my_item_0.id,
                'serial_number': '123',
                'category': 'tacos',
                'station_config': None,
                'cameras': {
                    'camera_1': {"brightness": 100, "exposition": 100, "position": "right"},
                    'camera_2': {"brightness": 100, "exposition": 100, "position": "left"}
                },
                'received_time': '2021-05-19 15:00:00',
                'inferences': {},
                'decision': {},
                'state': None,
                'error': None
            }
        }

    def test_get_item_metadata_should_return_requested_item_metadata(self, my_item_0):
        # Given
        metadata_storage = MemoryMetadataStorage()
        metadata_storage.items_metadata[my_item_0.id] = my_item_0.get_metadata()

        # When
        actual_item = metadata_storage.get_item_metadata(my_item_0.id)

        # Then
        assert actual_item == {
            'id': my_item_0.id,
            'serial_number': '123',
            'category': 'tacos',
            'station_config': None,
            'cameras': {
                'camera_1': {"brightness": 100, "exposition": 100, "position": "right"},
                'camera_2': {"brightness": 100, "exposition": 100, "position": "left"}
            },
            'received_time': '2021-05-19 15:00:00',
            'inferences': {},
            'decision': {},
            'state': None,
            'error': None
        }

    def test_get_all_items_metadata_should_return_all_items(self, my_item_0, my_item_2):
        # Given
        metadata_storage = MemoryMetadataStorage()
        metadata_storage.items_metadata[my_item_0.id] = my_item_0.get_metadata()
        metadata_storage.items_metadata[my_item_2.id] = my_item_2.get_metadata()

        # When
        actual_items = metadata_storage.get_all_items_metadata()

        # Then
        assert list(actual_items) == [
            {
                'id': my_item_0.id,
                'serial_number': '123',
                'category': 'tacos',
                'station_config': None,
                'cameras': {
                    'camera_1': {"brightness": 100, "exposition": 100, "position": "right"},
                    'camera_2': {"brightness": 100, "exposition": 100, "position": "left"}
                },
                'received_time': '2021-05-19 15:00:00',
                'inferences': {},
                'decision': {},
                'state': None,
                'error': None
            },
            {
                'id': my_item_2.id,
                'serial_number': '123',
                'category': 'tacos',
                'station_config': None,
                'cameras': {
                    'camera_3': {"brightness": 100, "exposition": 100, "position": "top"}
                },
                'received_time': '2021-05-19 15:00:00',
                'inferences': {},
                'decision': {},
                'state': None,
                'error': None
            }
        ]
