import datetime as dt

from freezegun import freeze_time
from edge_orchestrator.infrastructure.metadata_storage.memory_metadata_storage import MemoryMetadataStorage


@freeze_time(lambda: dt.datetime(year=2021, month=5, day=19, hour=15, minute=0, second=0))
class TestMemoryItemStorage:
    def test_save_item_metadata_should_write_item_in_memory(self, my_item_0):
        # Given
        metadata_storage = MemoryMetadataStorage()

        # When
        metadata_storage.save_item_metadata(my_item_0)

        # Then
        assert metadata_storage.items_metadata == {
            my_item_0.id: {
                'decision': {},
                'inferences': {},
                'serial_number': '123',
                'category': 'tacos',
                'station_config': None,
                'received_time': '2021-05-19 15:00:00',
                'cameras': {
                    'camera_1': {"brightness": 100, "exposition": 100, "position": "right"},
                    'camera_2': {"brightness": 100, "exposition": 100, "position": "left"}
                },
                'state': None
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
            'decision': {},
            'inferences': {},
            'serial_number': '123',
            'category': 'tacos',
            'station_config': None,
            'received_time': '2021-05-19 15:00:00',
            'cameras': {
                'camera_1': {"brightness": 100, "exposition": 100, "position": "right"},
                'camera_2': {"brightness": 100, "exposition": 100, "position": "left"}
            },
            'state': None
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
                'decision': {},
                'inferences': {},
                'serial_number': '123',
                'category': 'tacos',
                'station_config': None,
                'received_time': '2021-05-19 15:00:00',
                'cameras': {
                    'camera_1': {"brightness": 100, "exposition": 100, "position": "right"},
                    'camera_2': {"brightness": 100, "exposition": 100, "position": "left"}
                },
                'state': None
            },
            {
                'decision': {},
                'inferences': {},
                'serial_number': '123',
                'category': 'tacos',
                'station_config': None,
                'received_time': '2021-05-19 15:00:00',
                'cameras': {
                    'camera_3': {"brightness": 100, "exposition": 100, "position": "top"}
                },
                'state': None
            }
        ]
