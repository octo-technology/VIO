import logging
from typing import Dict, Optional, Tuple

from pyudev import Context


def list_connected_usb_device() -> Dict[Tuple, str]:
    context = Context()
    usb_devices = {}
    for device in context.list_devices(subsystem="video4linux"):
        if device.get("ID_BUS", "Unknown") == "usb":
            logging.debug(f"Found USB device: {device}")
            vendor_id = device.get("ID_VENDOR_ID", None)
            product_id = device.get("ID_MODEL_ID", None)
            device_path = device.get("DEVNAME", None)
            vendor_name = device.get("ID_VENDOR", "Unknown")
            model_name = device.get("ID_MODEL", "Unknown")
            if vendor_id and product_id and device_path and (vendor_id.strip(), product_id.strip()) not in usb_devices:
                usb_devices[(vendor_id.strip(), product_id.strip())] = {
                    "vendor_name": vendor_name,
                    "model_name": model_name,
                    "device_path": device_path,
                }
                logging.debug(
                    f"Vendor id: {vendor_id.strip()}, Product id: {product_id.strip()}, Device Path: {device_path}, Camera Name: {model_name}, Vendor Name: {vendor_name}"
                )
    return usb_devices


def get_camera_device_node(camera_vendor: str, camera_serial_number: str) -> Optional[str]:
    try:
        usb_devices = list_connected_usb_device()
        if (camera_vendor, camera_serial_number) in usb_devices:
            return usb_devices[(camera_vendor, camera_serial_number)]["device_path"]
        else:
            logging.warning(
                f"Camera with vendor: {camera_vendor} and serial number: {camera_serial_number} not found in connected USB devices:\n{usb_devices}"
            )
    except Exception:
        logging.warning("Error while listing connected USB devices")
    return None


if __name__ == "__main__":
    usb_cameras = list_connected_usb_device()
    for key, val in usb_cameras.items():
        print(
            f"Vendor id: {key[0]}, Product id: {key[1]}, Device Path: {val['device_path']}, Camera Name: {val['model_name']}, Vendor Name: {val['vendor_name']}"
        )
