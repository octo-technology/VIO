import os
import uuid
import labelbox as lb
import labelbox.types as lb_types

from edge_orchestrator import logger
from edge_orchestrator.domain.ports.labelizer import Labelizer
from edge_orchestrator.domain.ports.metadata_storage import MetadataStorage
from edge_orchestrator.domain.ports.binary_storage import BinaryStorage


def transform_annotations_to_bbox(annotation: dict):
    # Transform metadata to labelbox bbox
    bbox_annotation = []
    for object in annotation:
        label = object["label"]
        location = object["location"]

        bbox_annotation.append(
            lb_types.ObjectAnnotation(
                name=label,  # must match your ontology feature's name
                value=lb_types.Rectangle(
                    start=lb_types.Point(x=location[0], y=location[1]),  # x = left, y = top
                    end=lb_types.Point(x=location[2], y=location[3])     # x= left + width , y = top + height
                )
            )
        )

    return bbox_annotation


def get_binaries_annotations_path(metadata_storage: MetadataStorage, binary_storage: BinaryStorage, config_name: str):
    binaries_paths = []
    annotations = []
    ids = []

    # Match binary with its metadata
    metadata = metadata_storage.get_metadata()
    for metadata_item in metadata:
        item_cameras = metadata_item["cameras"].keys()
        for camera in item_cameras:
            # Get binary from camera
            binary_path = binary_storage.get_binary_path(metadata_item["id"], camera, config_name)
            binaries_paths.append(binary_path)

            # Get ids
            ids.append(metadata_item["id"])

            # Get label from metadata
            bbox_annotation = transform_annotations_to_bbox(metadata_item["inferences"][camera])
            annotations.append(bbox_annotation)

    return binaries_paths, annotations, ids


class LabelboxLabelizer(Labelizer):
    def __init__(self):
#        self.api_key = ---> Is it interesting to be able to reset Client ?
        self.client = lb.Client(api_key=os.getenv("LABELBOX_API_KEY"))
        self.project = None
        self.dataset = None

    def load_project(self, project_id: str) -> None:
        self.project = self.client.get_project(project_id)

    def check_dataset(self, dataset_id: str, dataset_name: str):
        datasets = list(self.client.get_datasets())
        dataset_uids = [dataset.uid for dataset in datasets]
        if dataset_name in dataset_uids:
            index_dataset = dataset_uids.index(dataset_id)
            self.dataset = datasets[index_dataset]
        else:
            self.dataset = self.client.create_dataset(name=dataset_name)

    def post_images(self, dataset_id: str, dataset_name: str, config_name: str, metadata_storage: MetadataStorage,
                    binary_storage: BinaryStorage, filters: dict):
        self.check_dataset(dataset_id, dataset_name)
        binaries_paths, annotations, ids = get_binaries_annotations_path(metadata_storage, binary_storage, config_name)

        labels = []
        data_rows = []
        for item_index, binary_path in enumerate(binaries_paths):
            global_key = ids[item_index]
            data_rows.append(
                {"row_data": binary_path,
                 "global_key": global_key,
                 "media_type": "IMAGE",
                 })
            labels.append(
                lb_types.Label(data=lb_types.ImageData(global_key=global_key),
                               annotations=annotations[item_index]))
        # Uploading files to Labelbox
        try:
            binaries_upload_job = self.dataset.create_data_rows(data_rows=data_rows)
            binaries_upload_job.wait_till_done()
        except Exception as err:
            print(f'Error while creating labelbox dataset -  Error: {err}')

        # Uploading labels to Labelbox
        try:
            annotations_upload_job = lb.MALPredictionImport.create_from_objects(
                client=self.client,
                project_id=self.project.uid,
                name="mal_job" + str(uuid.uuid4()),
                predictions=labels)
            annotations_upload_job.wait_until_done()
        except Exception as err:
            print(f'Error while uploading labelbox MAL predictions -  Error: {err}')

        return True
