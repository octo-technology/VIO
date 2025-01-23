import json
import os
from io import BytesIO
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
from google.api_core.exceptions import NotFound
from google.cloud.storage import Bucket, Client
from PIL import Image

from models.edge_data_manager import EdgeDataManager
from utils.prediction_boxes import filter_inferences_on_camera_id, plot_predictions

load_dotenv()

BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
IMG_EXTENSIONS = [".jpg", ".jpeg", ".png"]
NUMBER_CAMERAS = os.getenv("NUMBER_CAMERAS", 2)


@st.cache_data(ttl=30)
def extract_items(_gcp_client: Client) -> EdgeDataManager:
    # Get the bucket
    bucket = _gcp_client.bucket(BUCKET_NAME)
    blobs = bucket.list_blobs()

    blobs_images = [
        blob
        for blob in blobs
        if any(blob.name.endswith(extension) for extension in IMG_EXTENSIONS)
    ]
    blobs_images_sorted = sorted(
        blobs_images, key=lambda x: x.time_created, reverse=True
    )

    edges_data = EdgeDataManager()

    for blob in blobs_images_sorted:
        blob_name = blob.name

        # TODO: Refactor this part
        # Extracting the edge, use case and item id
        blob_name_split = blob_name.split("/")
        edge_name = blob_name_split[0]
        use_case_name = blob_name_split[1]
        item_id = blob_name_split[2]
        file_name = blob_name_split[-1]
        camera_id = file_name.split(".")[0]

        # Init some parameters
        if edge_name not in edges_data.get_edge_names():
            edges_data.add_edge(edge_name)

        edge = edges_data.get_edge(edge_name)
        if edge:
            if use_case_name not in edge.get_use_case_names():
                edge_ip = extract_edge_ip(bucket, edge_name)
                edge.add_usecase(use_case_name, edge_ip)

            use_case = edge.get_use_case(use_case_name)
            if item_id not in use_case.get_item_ids():
                metadata = extract_metadata(bucket, edge_name, use_case_name, item_id)
                use_case.add_item(item_id, blob.time_created, metadata)

            item = use_case.get_item(item_id)
            if camera_id not in item.camera_names:
                item.add_camera(camera_id)

            if any(file_name.endswith(extension) for extension in IMG_EXTENSIONS):
                # Downloading the first NUMBER_CAMERAS pics
                if (
                    item.number_pictures
                    < NUMBER_CAMERAS
                ):
                    binary_data = blob.download_as_bytes()
                    picture = Image.open(BytesIO(binary_data))

                    # If metadata is not empty, we plot the predictions
                    if (
                        item
                        .contains_predictions(camera_id)
                    ):
                        camera_inferences_metadata = filter_inferences_on_camera_id(
                            camera_id, item.metadata
                        )
                        if camera_inferences_metadata:
                            picture = plot_predictions(
                                picture, camera_inferences_metadata
                            )
                    
                    item.add_picture(camera_id, picture)

    return edges_data


def extract_edge_ip(bucket: Bucket, edge_name: str) -> Optional[str]:
    blob = bucket.blob(f"{edge_name}/edge_ip.txt")
    try:
        edge_ip = blob.download_as_text()
    except NotFound as e:
        print(f"Edge IP not found for {edge_name}. Error: {e}")
        edge_ip = None
    return edge_ip


def extract_metadata(
    bucket: Bucket, edge_name: str, use_case: str, item_id: str
) -> Optional[dict]:
    blob = bucket.blob(f"{edge_name}/{use_case}/{item_id}/metadata.json")
    try:
        metadata = json.loads(blob.download_as_text())
    except NotFound as e:
        print(f"Metadata not found for {edge_name}/{use_case}/{item_id}. Error: {e}")
        metadata = None
    return metadata
