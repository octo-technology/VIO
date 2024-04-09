import os
import uuid
import labelbox as lb

from edge_orchestrator import logger
from edge_orchestrator.domain.ports.labelizer import Labelizer
from edge_orchestrator.domain.ports.metadata_storage import MetadataStorage
from edge_orchestrator.domain.ports.binary_storage import BinaryStorage


class LabelboxLabelizer(Labelizer):
    def __init__(self):
#        self.api_key = ---> To reset Client
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

    def get_binaries_annotations_path(self, metadata_storage: MetadataStorage, binary_storage: BinaryStorage, config_name: str):
        # Match binary with its metadata

        # Convert metadata to labelbox bbox or other
        for annotation in metadata:
            transform_annotations_to_bbox(annotation)

        return doublets_list

    def transform_annotations_to_bbox(self, annotation: ??):
        return bbox_annotation


    def post_images(self, dataset_id: str, dataset_name: str, config_name: str, metadata_storage: MetadataStorage,
                    binary_storage: BinaryStorage, filters: dict):
        self.check_dataset(dataset_id, dataset_name)
        data_doublets = self.get_binaries_annotations_path(metadata_storage, binary_storage)

###
        for binary, annotation in data_doublets:
            binaries[f"{variable}"] = do_stuff(binary)
            labels[f"{variable}"] = do_stuff(annotation)
        try:
            binaries_upload_job = self.dataset.create_data_rows()
            binaries_upload_job.wait_till_done()
        except Exception as err:
            print(f'Error while creating labelbox dataset -  Error: {err}')
###
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
