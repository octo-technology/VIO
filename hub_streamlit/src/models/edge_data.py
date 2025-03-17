import os
from io import BytesIO
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from google.cloud.storage.blob import Blob
from PIL import Image
from pydantic import BaseModel

from gcp_binary_storage import GCPBinaryStorage
from models.use_case import UseCase
from utils.prediction_boxes import filter_inferences_on_camera_id, plot_predictions

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")
IMG_EXTENSIONS = [".jpg", ".jpeg", ".png"]
NUMBER_CAMERAS = os.getenv("NUMBER_CAMERAS", 2)


class EdgeData(BaseModel):
    name: str
    edge_ip: Optional[str] = None
    use_cases: List[UseCase] = []

    limit_blob_extracted: int = 20

    def add_usecase(self, use_case_name: str, edge_ip: str):
        self.edge_ip = edge_ip
        self.use_cases.append(UseCase(name=use_case_name))

    def get_use_case_names(self) -> List[str]:
        return [use_case.name for use_case in self.use_cases]

    def get_use_case(self, name: str) -> Optional[UseCase]:
        for use_case in self.use_cases:
            if use_case.name == name:
                return use_case
        return None

    def get_ip(self, gcp_client: GCPBinaryStorage):
        print(f"Getting IP for edge: {self.name}")
        ip_blobname = f"{self.name}/edge_ip.txt"
        self.edge_ip = gcp_client.get_text_blob(ip_blobname)

    def extract(self, gcp_client: GCPBinaryStorage):
        print(f"Extracting data for edge: {self.name}")

        blobs = gcp_client.bucket.list_blobs(prefix=self.name)

        blobs_images = [
            blob
            for blob in blobs
            if any(blob.name.endswith(extension) for extension in IMG_EXTENSIONS)
        ]

        blobs_sorted = sorted(blobs_images, key=lambda x: x.time_created, reverse=True)[
            : self.limit_blob_extracted
        ]

        self.package(blobs_sorted, gcp_client)

    def extract_item_ids(self, blobs: List[Blob]):
        item_ids = []
        for blob in blobs:
            item_id = Path(blob.name).stem.split("_")[0]
            item_ids.append(item_id)
        return item_ids

    def package(self, blobs: List[Blob], gcp_client: GCPBinaryStorage):
        cloud_item_ids = self.extract_item_ids(blobs)
        for blob in blobs:
            blob_name = blob.name

            blob_name_split = blob_name.split("/")
            edge_name = blob_name_split[0]
            use_case_name = blob_name_split[1]
            prefix = blob_name_split[2] if blob_name_split[2].find(".") == -1 else None
            file_name = blob_name_split[-1]
            file_name_split = file_name.split("_", 1)
            item_id = file_name_split[0]
            camera_id = file_name_split[1].split(".")[0] if len(file_name_split) > 1 else None

            if use_case_name not in self.get_use_case_names():
                self.add_usecase(use_case_name, self.edge_ip)

            use_case = self.get_use_case(use_case_name)

            use_case_item_ids = use_case.get_item_ids()
            extra_item_ids = list(set(use_case_item_ids) - set(cloud_item_ids))
            if extra_item_ids != []:
                for item_id in extra_item_ids:
                    use_case.remove_item(item_id)
                continue
            if item_id not in use_case_item_ids:
                metadata = gcp_client.extract_metadata(
                    edge_name, use_case_name, prefix, item_id
                )
                use_case.add_item(item_id, blob.time_created, metadata)

            item = use_case.get_item(item_id)
            if camera_id not in item.get_camera_ids():
                item.add_camera(camera_id)

            if any(file_name.endswith(extension) for extension in IMG_EXTENSIONS):
                # Downloading the first NUMBER_CAMERAS pics
                if item.number_pictures < NUMBER_CAMERAS:
                    binary_data = blob.download_as_bytes()
                    picture = Image.open(BytesIO(binary_data))

                    # If metadata is not empty, we plot the predictions
                    if item.contains_predictions(camera_id):
                        camera_inferences_metadata = filter_inferences_on_camera_id(
                            camera_id, item.metadata
                        )
                        if camera_inferences_metadata:
                            picture = plot_predictions(
                                picture, camera_inferences_metadata
                            )

                    camera = item.get_camera(camera_id)
                    camera.add_picture(picture)
                    item.number_pictures += 1
