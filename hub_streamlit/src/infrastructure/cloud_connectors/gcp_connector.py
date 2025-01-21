import json
import os
from io import BytesIO
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
from google.api_core.exceptions import NotFound
from google.cloud.storage import Bucket, Client
from PIL import Image

from src.infrastructure.data.edge_data import EdgeData
from src.utils.prediction_boxes import (
    filtering_items_that_have_predictions,
    plot_predictions,
)

load_dotenv()

BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
IMG_EXTENSIONS = [".jpg", ".jpeg", ".png"]


@st.cache_data(ttl=30)
def extract_items(_gcp_client: Client) -> EdgeData:
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

    edges_data = EdgeData()

    for blob in blobs_images_sorted:
        blob_name = blob.name

        # TODO: Refactor this part
        # Extracting the edge, use case and item id
        blob_name_split = blob_name.split("/")
        edge_name = blob_name_split[0]
        use_case = blob_name_split[1]
        item_id = blob_name_split[2]
        file_name = blob_name_split[-1]
        camera_id = file_name.split(".")[0]

        if "." in item_id:
            continue

        # Init some parameters
        if edge_name not in edges_data.edge_names:
            edges_data.add_edge(edge_name)
        if use_case not in edges_data.edges[edge_name].use_case_names:
            edge_ip = extract_edge_ip(bucket, edge_name)
            edges_data.edges[edge_name].add_usecase(use_case, edge_ip)
        if item_id not in edges_data.edges[edge_name].use_cases[use_case].item_names:
            metadata = extract_metadata(bucket, edge_name, use_case, item_id)
            edges_data.edges[edge_name].use_cases[use_case].add_item(
                item_id, blob.time_created, metadata
            )
        if (
            camera_id
            not in edges_data.edges[edge_name]
            .use_cases[use_case]
            .items[item_id]
            .camera_names
        ):
            edges_data.edges[edge_name].use_cases[use_case].items[item_id].add_camera(
                camera_id
            )

        if ".jpg" in file_name:
            # Downloading the first 5 pics
            number_pictures_to_download = 5
            if (
                edges_data.edges[edge_name]
                .use_cases[use_case]
                .items[item_id]
                .number_pictures
                < number_pictures_to_download
            ):
                binary_data = blob.download_as_bytes()
                picture = Image.open(BytesIO(binary_data))

                # If metadata is not empty, we plot the predictions
                if filtering_items_that_have_predictions(
                    edges_data.edges[edge_name]
                    .use_cases[use_case]
                    .items[item_id]
                    .metadata,
                    camera_id,
                ):
                    picture = plot_predictions(
                        picture,
                        camera_id,
                        metadata=edges_data.edges[edge_name]
                        .use_cases[use_case]
                        .items[item_id]
                        .metadata,
                    )
            else:
                picture = Image.new("RGB", (100, 100), (200, 155, 255))

            edges_data.edges[edge_name].use_cases[use_case].items[item_id].add_picture(
                camera_id, picture
            )

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
    if blob.exists():
        metadata = json.loads(blob.download_as_text())
    else:
        metadata = None
    return metadata
