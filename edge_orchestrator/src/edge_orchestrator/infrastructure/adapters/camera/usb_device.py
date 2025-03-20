import logging
from typing import Dict, Tuple

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
            id_path = device.get("ID_PATH", None)
            vendor_name = device.get("ID_VENDOR", "Unknown")
            model_name = device.get("ID_MODEL", "Unknown")
            if (
                vendor_id
                and product_id
                and device_path
                and id_path
                and (vendor_id.strip(), product_id.strip(), id_path.strip()) not in usb_devices
            ):
                usb_devices[(vendor_id.strip(), product_id.strip(), id_path.strip())] = {
                    "vendor_name": vendor_name,
                    "model_name": model_name,
                    "device_path": device_path,
                }
                logging.debug(
                    f"Vendor id: {vendor_id.strip()}, Product id: {product_id.strip()}, Id Path: {id_path}, Device Path: {device_path}, Camera Name: {model_name}, Vendor Name: {vendor_name}"
                )
    return usb_devices


if __name__ == "__main__":
    usb_cameras = list_connected_usb_device()
    for key, val in usb_cameras.items():
        print(
            f"Vendor id: {key[0]}, Product id: {key[1]}, Device Path: {val['device_path']}, Camera Name: {val['model_name']}, Vendor Name: {val['vendor_name']}"
        )
