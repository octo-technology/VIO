import json
import os
import streamlit as st
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from src.utils.prediction_boxes import filtering_items_that_have_predictions, plot_predictions
from google.api_core.exceptions import NotFound
from google.cloud.storage import Client

load_dotenv()

BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
IMG_EXTENSIONS = [".jpg", ".jpeg", ".png"]

def get_gcp_client():
    # Client configuration for GCP
    return Client()


@st.cache_data(ttl=30)
def extract_items(_gcp_client: Client) -> dict:
    # Get the bucket
    bucket = _gcp_client.bucket(os.getenv("GCP_BUCKET_NAME"))
    blobs = bucket.list_blobs()
   
    blobs_images = [blob for blob in blobs if any(blob.name.endswith(extension) for extension in IMG_EXTENSIONS)]
    blobs_images_sorted = sorted(blobs_images, key=lambda x: x.time_created, reverse=True)

    folder_dict = {"edge_list": []}
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
        if edge_name not in folder_dict["edge_list"]:
            folder_dict["edge_list"].append(edge_name)
            folder_dict[edge_name] = {}
            folder_dict[edge_name]["use_case_list"] = []
        if use_case not in folder_dict[edge_name]["use_case_list"]:
            folder_dict[edge_name]["use_case_list"].append(use_case)
            folder_dict[edge_name]["edge_ip"] = read_edge_ip(bucket, edge_name)
            folder_dict[edge_name][use_case] = {}
            folder_dict[edge_name][use_case]["item_list"] = []
        if item_id not in folder_dict[edge_name][use_case]["item_list"]:
            folder_dict[edge_name][use_case]["item_list"].append(item_id)
            folder_dict[edge_name][use_case][item_id] = {}
            folder_dict[edge_name][use_case][item_id]["nbr_pictures"] = 0
            folder_dict[edge_name][use_case][item_id]["creation_date"] = blob.time_created
            folder_dict[edge_name][use_case][item_id]["metadata"] = read_metadata(bucket, edge_name, use_case, item_id)
            folder_dict[edge_name][use_case][item_id]["camera_list"] = []
        if camera_id not in folder_dict[edge_name][use_case][item_id]:
            folder_dict[edge_name][use_case][item_id]["camera_list"].append(camera_id)
            folder_dict[edge_name][use_case][item_id][camera_id] = {}
            folder_dict[edge_name][use_case][item_id][camera_id]["pictures"] = []

        if ".jpg" in file_name:
            # Downloading the first 10 pics
            if folder_dict[edge_name][use_case][item_id]["nbr_pictures"] < 5:
                binary_data = blob.download_as_bytes()
                img = Image.open(BytesIO(binary_data))

                # If metadata is not empty, we plot the predictions
                if filtering_items_that_have_predictions(folder_dict[edge_name][use_case][item_id]["metadata"], camera_id):
                    img = plot_predictions(img, camera_id,
                                           metadata=folder_dict[edge_name][use_case][item_id]["metadata"])
            else:
                img = Image.new("RGB", (100, 100), (200, 155, 255))

            folder_dict[edge_name][use_case][item_id][camera_id]["pictures"].append(img)
            folder_dict[edge_name][use_case][item_id]["nbr_pictures"] += 1

    return folder_dict


def read_edge_ip(bucket, edge_name):
    blob = bucket.blob(f"{edge_name}/edge_ip.txt")
    try:
        ip = blob.download_as_text()
    except NotFound as e:
        print(f"Edge IP not found for {edge_name}. Error: {e}")
        ip = None
    return ip


def read_metadata(bucket, edge_name, use_case, item_id):
    blob = bucket.blob(f"{edge_name}/{use_case}/{item_id}/metadata.json")
    if blob.exists():
        metadata = json.loads(blob.download_as_text())
    else:
        metadata = None
    return metadata
