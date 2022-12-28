from edge_orchestrator.domain.models.item import Item


class TestItem:
    def test_item_from_nothing_should_instantiate_empty_item_with_serial_number_and_category_hardcoded(self):
        # When
        item = Item.from_nothing()

        # Then
        assert item.id is not None
        assert item.serial_number == 'serial_number'
        assert item.category == 'category'
        assert item.binaries == {}
        assert item.cameras_metadata == {}
        assert item.inferences == {}
        assert item.decision == {}
        assert item.state is None

    # TODO test_get_metadata
