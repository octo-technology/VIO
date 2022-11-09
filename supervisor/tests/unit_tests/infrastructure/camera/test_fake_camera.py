from supervisor.infrastructure.camera.fake_camera import FakeCamera
from tests.conftest import TEST_DATA_FOLDER_PATH


class TestFakeCamera:
    def test_select_random_image_should_return_random_image_from_input_images_folder(self):
        # Given
        camera = FakeCamera("id", {"type": "top_camera", "input_images_folder": "fake_item"})
        camera.data_folder_path = TEST_DATA_FOLDER_PATH

        # When
        image_path = camera.select_random_image()

        print(image_path)

        # Then
        assert image_path in list((TEST_DATA_FOLDER_PATH / 'fake_item').glob('*.jpg'))
