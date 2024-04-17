from edge_orchestrator.infrastructure.metadata_storage.mongodb_metadata_storage import (
    MongoDbMetadataStorage,
)


class TestMongoDbItemStorage:
    def test_save_item_metadata_should_write_item_metadata_in_mongo_db(self, test_mongo_db_uri, my_item_0):
        # Given
        metadata_storage = MongoDbMetadataStorage(mongodb_uri=test_mongo_db_uri)
        my_item_0.id = "d1adfc08-cb98-46d6-ae9c-b07c5d16a2ec"

        # When
        metadata_storage.save_item_metadata(my_item_0)

        # Then
        all_items_metadata = [item for item in metadata_storage.items_metadata.find()]
        assert all_items_metadata == [
            {
                "_id": "d1adfc08-cb98-46d6-ae9c-b07c5d16a2ec",
                "serial_number": "123",
                "category": "tacos",
                "station_config": None,
                "cameras": {
                    "camera_1": {
                        "brightness": 100,
                        "exposition": 100,
                        "position": "right",
                    },
                    "camera_2": {
                        "brightness": 100,
                        "exposition": 100,
                        "position": "left",
                    },
                },
                "received_time": "2021-05-19 15:00:00",
                "inferences": {},
                "decision": {},
                "dimensions": [100, 100],
                "state": None,
                "error": None,
            }
        ]

    def test_get_item_metadata_should_return_requested_item_metadata(self, test_mongo_db_uri, my_item_0):
        # Given
        my_item_0.id = "d1adfc08-cb98-46d6-ae9c-b07c5d16a2ec"
        metadata_storage = MongoDbMetadataStorage(mongodb_uri=test_mongo_db_uri)
        metadata_storage.items_metadata.update_one(
            {"_id": my_item_0.id}, {"$set": my_item_0.get_metadata(False)}, upsert=True
        )

        # When
        item_metadata = metadata_storage.get_item_metadata(my_item_0.id)

        # Then
        assert item_metadata == {
            "id": "d1adfc08-cb98-46d6-ae9c-b07c5d16a2ec",
            "serial_number": "123",
            "category": "tacos",
            "station_config": None,
            "cameras": {
                "camera_1": {"brightness": 100, "exposition": 100, "position": "right"},
                "camera_2": {"brightness": 100, "exposition": 100, "position": "left"},
            },
            "received_time": "2021-05-19 15:00:00",
            "inferences": {},
            "decision": {},
            "dimensions": [100, 100],
            "state": None,
            "error": None,
        }

    def test_get_all_items_metadata_should_return_all_items(self, test_mongo_db_uri, my_item_0, my_item_2):
        # Given
        my_item_0.id = "d1adfc08-cb98-46d6-ae9c-b07c5d16a2ec"
        my_item_2.id = "af6b4922-8e4a-4dbc-ac9b-b5fd56ceaf25"
        metadata_storage = MongoDbMetadataStorage(mongodb_uri=test_mongo_db_uri)
        metadata_storage.items_metadata.update_one(
            {"_id": my_item_0.id}, {"$set": my_item_0.get_metadata(False)}, upsert=True
        )
        metadata_storage.items_metadata.update_one(
            {"_id": my_item_2.id}, {"$set": my_item_2.get_metadata(False)}, upsert=True
        )

        # When
        item_metadata = metadata_storage.get_all_items_metadata()

        # Then
        assert item_metadata == [
            {
                "id": "d1adfc08-cb98-46d6-ae9c-b07c5d16a2ec",
                "serial_number": "123",
                "category": "tacos",
                "station_config": None,
                "cameras": {
                    "camera_1": {
                        "brightness": 100,
                        "exposition": 100,
                        "position": "right",
                    },
                    "camera_2": {
                        "brightness": 100,
                        "exposition": 100,
                        "position": "left",
                    },
                },
                "received_time": "2021-05-19 15:00:00",
                "inferences": {},
                "decision": {},
                "dimensions": [100, 100],
                "state": None,
                "error": None,
            },
            {
                "id": "af6b4922-8e4a-4dbc-ac9b-b5fd56ceaf25",
                "serial_number": "123",
                "category": "tacos",
                "station_config": None,
                "cameras": {
                    "camera_3": {
                        "brightness": 100,
                        "exposition": 100,
                        "position": "top",
                    }
                },
                "received_time": "2021-05-19 15:00:00",
                "inferences": {},
                "decision": {},
                "dimensions": [100, 100],
                "state": None,
                "error": None,
            },
        ]
