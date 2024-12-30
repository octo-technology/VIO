import os
from PIL import Image
from io import BytesIO
from google.cloud import storage

# GCP key path
path_key_json = "/Users/thibaut.leibel/Documents/Projects/Octo/VIO-Conf/acn-gcp-octo-sas-d657d0330cec.json"


def get_gcp_client():
    # Client configuration for GCP
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path_key_json
    client = storage.Client()
    return client


def extract_items(gcp_client):
    # Get the bucket
    bucket = gcp_client.bucket("tf-vio-bucket")
    blobs = bucket.list_blobs()
    blobs = [blob for blob in blobs if not (blob.name.endswith(".txt") or blob.name.endswith(".json"))]
    blobs = sorted(blobs, key=lambda x: x.time_created, reverse=True)

    folder_dict = {"edge_list": []}
    for blob in blobs:
        blob_name = blob.name

        # Extracting the edge, use case and item id
        blob_name_split = blob_name.split("/")
        edge_name = blob_name_split[0]
        use_case = blob_name_split[1]
        item_id = blob_name_split[2]
        file_name = blob_name_split[-1]

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
            folder_dict[edge_name][use_case][item_id]["pictures"] = []
            folder_dict[edge_name][use_case][item_id]["nbr_pictures"] = 0
            folder_dict[edge_name][use_case][item_id]["creation_date"] = blob.time_created
            folder_dict[edge_name][use_case][item_id]["metadata"] = f"{edge_name}/{use_case}/{item_id}/metadata.json"

        if ".jpg" in file_name:
            # Downloading the first 10 pics
            if folder_dict[edge_name][use_case][item_id]["nbr_pictures"] < 10:
                binary_data = blob.download_as_bytes()
                img = Image.open(BytesIO(binary_data))
            else:
                img = Image.new("RGB", (100, 100), (200, 155, 255))

            folder_dict[edge_name][use_case][item_id]["pictures"].append(img)
            folder_dict[edge_name][use_case][item_id]["nbr_pictures"] += 1

    return folder_dict


def read_edge_ip(bucket, edge_name):
    blob = bucket.blob(f"{edge_name}/edge_ip.txt")
    ip = blob.download_as_text()
    return ip


folders = extract_items(get_gcp_client())
print(folders)