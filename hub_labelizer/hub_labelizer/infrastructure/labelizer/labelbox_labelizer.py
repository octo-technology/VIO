import os
import aiohttp
import uuid
import labelbox as lb
import labelbox.types as lb_types
from typing import List

from hub_labelizer import logger
from hub_labelizer.ports.labelizer import Labelizer


async def get_metadata(url_orchestrator: str):
    call_url = f"{url_orchestrator}/api/v1/metadata_storage"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(call_url) as response:
                json_data = await response.json()
                logger.debug(f"Received metadata for {len(json_data)} items")

    except Exception as e:
        logger.exception(e)

    return json_data


async def aget_binaries_annotations_path(url_orchestrator: str, config_name: str):
    dict_metabin = {}
    metadata = await get_metadata(url_orchestrator)

    for item_metadata in metadata:
        item_id = item_metadata["id"]
        for camera_id in item_metadata["inferences"].keys():
            # Get detections for this binary
            lb_annotation_list = []
            camera_detections = item_metadata["inferences"][camera_id]
            camera_dimensions = item_metadata["dimensions"][camera_id]
            for model_id in camera_detections.keys():
                for detection in camera_detections[model_id].values():
                    lb_annotation = transform_annotations_to_bbox(detection, camera_dimensions)
                    lb_annotation_list.append(lb_annotation)

            # Get binary path
            call_url = f"{url_orchestrator}/api/v1/binary_path/{item_id}/{camera_id}/{config_name}"
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(call_url) as response:
                        file_path = await response.json()
                        logger.debug(f"Received metadata for {file_path} item")
            except Exception as e:
                logger.exception(e)
                file_path = "no_item"

            dict_metabin[item_id] = {}
            dict_metabin[item_id][camera_id] = {}
            dict_metabin[item_id][camera_id]["path"] = file_path
            dict_metabin[item_id][camera_id]["detections"] = lb_annotation_list

    return dict_metabin


def transform_annotations_to_bbox(annotation: dict, camera_dimensions: List[int]):
    # Transform metadata to labelbox bbox
    label = annotation["label"]
    location = annotation["location"]

    img_width, img_height = camera_dimensions
    bbox_annotation = lb_types.ObjectAnnotation(
                name=label,  # must match your ontology feature's name
                value=lb_types.Rectangle(
                    start=lb_types.Point(x=location[0] * img_width, y=location[1] * img_height),  # x = left, y = top
                    end=lb_types.Point(x=location[2] * img_width, y=location[3]* img_height)     # x= left + width , y = top + height
                )
            )

    return bbox_annotation


class LabelboxLabelizer(Labelizer):
    def __init__(self):
#        self.api_key = ---> Is it interesting to be able to reset Client ?
        self.client = lb.Client(api_key=os.getenv("LABELBOX_API_KEY"))
        self.project = None
        self.dataset = None

    def load_project(self, project_id: str) -> None:
        self.project = self.client.get_project(project_id)

    def load_dataset(self, dataset_id: str):
        self.dataset = self.client.get_dataset(dataset_id)

    async def apost_images(self, project_id: str, dataset_id: str, config_name: str, filters: dict):
        self.load_dataset(dataset_id)
        url_orchestrator = os.getenv("EDGE_ORCHESTRATOR_URL")
        print(url_orchestrator)
        binaries_annotations = await aget_binaries_annotations_path(url_orchestrator, config_name)

        data_rows = []
        labels = []
        keys_list = []
        for item_id in binaries_annotations.keys():
            binaries_item = binaries_annotations[item_id]
            for camera_id in binaries_item.keys():
                global_key = str(uuid.uuid4())
                keys_list.append(global_key)

                # Prepare file paths
                data_rows.append(
                    {"row_data": binaries_annotations[item_id][camera_id]["path"],
                     "media_type": "IMAGE",
                     "global_key": global_key,
                     })

                # Prepare annotations
                labels.append(
                    lb_types.Label(data=lb_types.ImageData(global_key=global_key),
                                   annotations=binaries_item[camera_id]["detections"]))

        # Uploading files to Labelbox
        try:
            binaries_upload_job = self.dataset.create_data_rows(data_rows)
            binaries_upload_job.wait_till_done()
            logger.info('Binaries uploaded')
        except Exception as err:
            logger.warning(f'Error while creating labelbox dataset -  Error: {err}')
            return False

        # Importing data_rows to project
        self.load_project(project_id)
        self.project.create_batch(
          name=f"Auto batch {str(uuid.uuid4())}",
          global_keys=keys_list,
          priority=5,
        )

        # Uploading labels to Labelbox
        try:
            annotations_upload_job = lb.MALPredictionImport.create_from_objects(
                client=self.client,
                project_id=project_id,
                name="mal_job" + str(uuid.uuid4()),
                predictions=labels)
            annotations_upload_job.wait_until_done()
            logger.info('Labels uploaded')
        except Exception as err:
            logger.warning(f'Error while uploading labelbox MAL predictions -  Error: {err}')
            return False

        return True
