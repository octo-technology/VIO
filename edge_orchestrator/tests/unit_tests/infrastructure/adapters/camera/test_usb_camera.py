from edge_orchestrator.infrastructure.adapters.camera.usb_camera import UsbCamera


class TestUsbCamera:
    def test_get_camera_device_node(self):
        # Given
        usb_devices = {
            ("1bcf", "2286", "pci-0000:00:14.0-usb-0:1:1.0"): {
                "vendor_name": "Sunplus_IT_Co",
                "model_name": "FHD_Camera",
                "device_path": "/dev/video0",
            },
            ("1bcf", "2286", "pci-0000:00:14.0-usb-0:2:1.0"): {
                "vendor_name": "Sunplus_IT_Co",
                "model_name": "FHD_Camera",
                "device_path": "/dev/video2",
            },
        }
        camera_vendor = "1bcf"
        camera_serial_number = "2286"
        same_camera_index = 0

        # When
        device_node = UsbCamera._get_camera_device_node(
            usb_devices, camera_vendor, camera_serial_number, same_camera_index
        )

        # Then
        assert device_node == "/dev/video0"
