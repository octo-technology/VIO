import datetime as dt

from _pytest.fixtures import fixture
from freezegun import freeze_time

from supervisor.domain.models.item import Item


@fixture(scope='function')
@freeze_time(lambda: dt.datetime(year=2021, month=5, day=19, hour=15, minute=0, second=0))
def my_item_0(my_cameras_metadata_0, my_binaries_0):
    return Item(serial_number='123', category='tacos', cameras_metadata=my_cameras_metadata_0,
                binaries=my_binaries_0)


@fixture(scope='function')
@freeze_time(lambda: dt.datetime(year=2021, month=5, day=19, hour=15, minute=0, second=0))
def my_item_1(my_cameras_metadata_1, my_binaries_1):
    return Item(serial_number='serial_number_test', category='category_test', cameras_metadata=my_cameras_metadata_1,
                binaries=my_binaries_1)


@fixture(scope='function')
@freeze_time(lambda: dt.datetime(year=2021, month=5, day=19, hour=15, minute=0, second=0))
def my_fake_item(my_cameras_metadata_1, my_fake_binaries):
    return Item(serial_number='serial_number_test', category='category_test', cameras_metadata=my_cameras_metadata_1,
                binaries=my_fake_binaries)


@fixture(scope='function')
@freeze_time(lambda: dt.datetime(year=2021, month=5, day=19, hour=15, minute=0, second=0))
def my_fake_item_2(my_cameras_metadata_3, my_fake_binaries_2):
    return Item(serial_number='serial_number_test', category='category_test', cameras_metadata=my_cameras_metadata_3,
                binaries=my_fake_binaries_2)


@fixture(scope='function')
@freeze_time(lambda: dt.datetime(year=2021, month=5, day=19, hour=15, minute=0, second=0))
def my_item_2(my_cameras_metadata_2, my_binaries_2):
    return Item(serial_number='123', category='tacos', cameras_metadata=my_cameras_metadata_2,
                binaries=my_binaries_2)
