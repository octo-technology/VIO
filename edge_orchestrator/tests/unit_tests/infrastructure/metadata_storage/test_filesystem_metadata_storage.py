import json
from pathlib import Path
from unittest.mock import patch

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.use_cases.supervisor import SupervisorState
from edge_orchestrator.infrastructure.metadata_storage.filesystem_metadata_storage import FileSystemMetadataStorage


class TestFileSystemMetadataStorage:

    @patch('edge_orchestrator.domain.models.item.generate_id')
    def test_save_item_metadata_should_write_metadata_on_filesystem(self, generate_id_mocked, tmpdir,
                                                                    my_cameras_metadata_0):
        # Given
        generate_id_mocked.return_value = 'my_item_id'
        item = Item(serial_number='serial_number', category='category', cameras_metadata=my_cameras_metadata_0,
                    binaries={})
        src_directory_path = Path(tmpdir.mkdir('metadata'))
        metadata_storage = FileSystemMetadataStorage(src_directory_path)

        # When
        metadata_storage.save_item_metadata(item)

        # Then
        path_to_my_metadata = (src_directory_path / 'my_item_id' / 'metadata.json')
        assert path_to_my_metadata.is_file()
        actual_metadata = json.load(path_to_my_metadata.open('r'))
        assert actual_metadata == item.get_metadata()

    def test_get_item_metadata_should_return_requested_item_metadata(self, tmpdir, my_cameras_metadata_0):
        # Given
        src_directory_path = Path(tmpdir.mkdir('metadata'))
        expected_metadata = my_cameras_metadata_0
        (src_directory_path / 'my_item_id').mkdir()
        with (src_directory_path / 'my_item_id' / 'metadata.json').open('w') as f:
            json.dump(expected_metadata, f)
        metadata_storage = FileSystemMetadataStorage(src_directory_path)

        # When
        actual_metadata = metadata_storage.get_item_metadata('my_item_id')

        # Then
        assert actual_metadata == expected_metadata

    @patch('edge_orchestrator.domain.models.item.generate_id')
    def test_get_item_state_should_return_expected_state(self, generate_id_mocked, tmpdir, my_cameras_metadata_0):
        # Given
        generate_id_mocked.return_value = 'my_item_id'
        src_directory_path = Path(tmpdir.mkdir('metadata'))
        (src_directory_path / 'my_item_id').mkdir()
        item = Item(serial_number='serial_number', category='category', cameras_metadata=my_cameras_metadata_0,
                    binaries={})
        item.state = SupervisorState.DONE.value
        expected_state = item.state
        with (src_directory_path / 'my_item_id' / 'metadata.json').open('w') as f:
            json.dump(item.get_metadata(), f)
        metadata_storage = FileSystemMetadataStorage(src_directory_path)

        # When
        actual_state = metadata_storage.get_item_state('my_item_id')

        # Then
        assert actual_state == expected_state

    def test_get_all_items_metadata_should_return_expected_metadata_list(self, tmpdir, my_cameras_metadata_0,
                                                                         my_cameras_metadata_1):
        src_directory_path = Path(tmpdir.mkdir('metadata'))
        (src_directory_path / 'my_item_id_1').mkdir()
        (src_directory_path / 'my_item_id_2').mkdir()
        with (src_directory_path / 'my_item_id_1' / 'metadata.json').open('w') as f1, \
                (src_directory_path / 'my_item_id_2' / 'metadata.json').open('w') as f2:
            json.dump(my_cameras_metadata_0, f1)
            json.dump(my_cameras_metadata_1, f2)
        metadata_storage = FileSystemMetadataStorage(src_directory_path)

        # When
        actual_items_metadata = metadata_storage.get_all_items_metadata()

        # Then
        assert (actual_items_metadata == [my_cameras_metadata_0, my_cameras_metadata_1] or
                actual_items_metadata == [my_cameras_metadata_1, my_cameras_metadata_0])
