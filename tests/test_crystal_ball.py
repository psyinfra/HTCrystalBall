"""Module for testing the htcrystalball module."""

import argparse
import sys

from pytest import raises as praises
from testfixtures import TempDirectory
sys.modules['htcondor'] = __import__('mock_htcondor')
from htcondor import Collector as mocked_collector

from htcrystalball import examine, collect, utils


def test_storage_validator():
    """
    Tests the storage input validator.
    :return:
    """
    assert utils.validate_storage_size("20GB") == "20GB"
    with praises(argparse.ArgumentTypeError):
        assert utils.validate_storage_size("20")
        assert utils.validate_storage_size("20iGB")
        assert utils.validate_storage_size("20GBt")
        assert utils.validate_storage_size("20GB3")


def test_time_validator():
    """
    Tests the time input validator.
    :return:
    """
    assert utils.validate_duration("20") == "20"
    with praises(argparse.ArgumentTypeError):
        assert utils.validate_duration("20min")
        assert utils.validate_duration("20imn")
        assert utils.validate_duration("20mint")
        assert utils.validate_duration("20hs")


def test_split_storage():
    """
    Tests the splitting method for storage inputs.
    :return:
    """
    number = 10
    unit = "GB"

    assert utils.split_num_str(str(number), 0.0, 'GiB') == (number, "GiB")
    assert utils.split_num_str(f'{number}GiB', 0.0, 'GiB') == (number, "GiB")
    assert utils.split_num_str(f'0{unit}', 0.0, 'GiB') == (0.0, "GB")


def test_split_time():
    """
    Tests the splitting method for the time input.
    :return:
    """
    number = 10
    unit = "min"
    assert utils.split_num_str(str(number), 0.0, 'min') == (number, "min")
    assert utils.split_num_str(f'{number}min', 0.0, 'min') == (number, "min")
    assert utils.split_num_str("0" + unit, 0.0, 'min') == (0, unit)


def test_time_conversion():
    """
    Tests the methods to convert and round to the next greater time dimension.
    :return:
    """
    number = 10
    assert utils.minutes_to_hours(number) == 0
    assert utils.hours_to_days(number) == 0
    number = 30
    assert utils.minutes_to_hours(number) == 1
    assert utils.hours_to_days(number) == 1
    number = 36
    assert utils.minutes_to_hours(number) == 1
    assert utils.hours_to_days(number) == 2
    number = 48
    assert utils.minutes_to_hours(number) == 1
    assert utils.hours_to_days(number) == 2
    number = 60
    assert utils.minutes_to_hours(number) == 1
    assert utils.hours_to_days(number) == 3
    number = 72
    assert utils.minutes_to_hours(number) == 1
    assert utils.hours_to_days(number) == 3


def test_conversions():
    """
    Tests the number conversion methods for storage size and time.
    :return:
    """
    assert utils.to_binary_gigabyte(10.0, "GiB") == 10.0
    assert utils.to_binary_gigabyte(10.0, "GiB") == 10
    assert utils.to_binary_gigabyte(10.0, "GB") == 10.0
    assert utils.to_binary_gigabyte(10, "GiB") == 10.0
    assert utils.to_binary_gigabyte(10.0, "MiB") == 0.01
    assert utils.to_binary_gigabyte(10.0, "KiB") == 1e-05
    assert utils.to_binary_gigabyte(1.0, "TiB") == 1000.0
    assert utils.to_binary_gigabyte(1.0, "PiB") == 1000000.0

    assert utils.to_minutes(10.0, "h") == 600.0
    assert utils.to_minutes(10.0, "min") == 10
    assert utils.to_minutes(10.0, "min") == 10.0
    assert utils.to_minutes(10, "min") == 10.0
    assert utils.to_minutes(10.0, "s") <= 0.17
    assert utils.to_minutes(1.0, "d") == 1440.0


def test_compare_request_available():
    """
    Tests the method for comparing ressources and assigning color codes.
    :return:
    """
    assert utils.compare_requested_available(7.8, 8.0) == "yellow"
    assert utils.compare_requested_available(7, 8) == "green"
    assert utils.compare_requested_available(8.1, 8) == "red"
    assert utils.compare_requested_available(8, 8) == "yellow"
    assert utils.compare_requested_available(0, 8) == "green"


def test_submit_parser():
    """
    Tests the .submit file parser.
    :return:
    """

    with TempDirectory() as d:
        d.write('test.submit', b'request_cpus = 1\n' + b'request_memory = 6000MB\n' + b'Queue 10')
        assert utils.parse_submit_file(d.path+'/test.submit')["cpu"] == 1
        assert utils.parse_submit_file(d.path+'/test.submit')["ram"] == "6000MB"
        assert utils.parse_submit_file(d.path+'/test.submit')["jobs"] == 10

    with TempDirectory() as d:
        d.write('test.submit', b'request_cpus=1\n' + b'request_memory=6000MB\n' + b'Queue 10')
        assert utils.parse_submit_file(d.path+'/test.submit')["cpu"] == 1
        assert utils.parse_submit_file(d.path+'/test.submit')["ram"] == "6000MB"
        assert utils.parse_submit_file(d.path+'/test.submit')["jobs"] == 10

    with TempDirectory() as d:
        d.write('test.submit', b'request_cpus=16\n' + b'request_memory=6GB\n' + b'Queue     10')
        assert utils.parse_submit_file(d.path+'/test.submit')["cpu"] == 16
        assert not utils.parse_submit_file(d.path+'/test.submit')["ram"] == "6000MB"
        assert utils.parse_submit_file(d.path+'/test.submit')["jobs"] == 10


def test_calc_manager():
    """
    Tests the method for preparing the slot checking.
    :return:
    """
    mocked_content = mocked_collector().query()

    assert examine.prepare(
        cpu=1, gpu=0, ram="10GB", disk="0", jobs=1, job_duration="10m",
        maxnodes=0, file="", verbose=True, content=mocked_content
    )
    assert not examine.prepare(
        cpu=0, gpu=1, ram="10GB", disk="0", jobs=1, job_duration="10m",
        maxnodes=0, file="", verbose=True, content=mocked_content
    )
    assert not examine.prepare(
        cpu=1, gpu=0, ram="0", disk="", jobs=1, job_duration="", maxnodes=0,
        verbose=True, file="", content=mocked_content
    )
    assert examine.prepare(
        cpu=1, gpu=1, ram="20GB", disk="", jobs=1, job_duration="10m",
        maxnodes=0, file="", verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=1, gpu=0, ram="10GB", disk="10GB", jobs=1, job_duration="10m",
        maxnodes=0, file="", verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=1, gpu=0, ram="10GB", disk="10GB", jobs=128, job_duration="15m",
        maxnodes=0, file="", verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=1, gpu=0, ram="10GB", disk="", jobs=1, job_duration="10m",
        maxnodes=1, file="", verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=8, gpu=0, ram="10GB", disk="", jobs=1, job_duration="10m",
        maxnodes=0, file="", verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=8, gpu=0, ram="80GB", disk="", jobs=4, job_duration="1h",
        maxnodes=0, file="", verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=2, gpu=0, ram="10GB", disk="", jobs=1, job_duration="10m",
        maxnodes=3, file="", verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=1, gpu=0, ram="20GB", disk="", jobs=1, job_duration="10m",
        maxnodes=2, file="", verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=2, gpu=0, ram="20GB", disk="", jobs=1, job_duration="",
        maxnodes=2, file="", verbose=True, content=mocked_content
    )
    assert not examine.prepare(
        cpu=2, gpu=0, ram="20GB", disk="", jobs=2, job_duration="",
        maxnodes=2, file="", verbose=True, content=mocked_content
    )
    assert not examine.prepare(
        cpu=2, gpu=0, ram="20GB", disk="", jobs=0, job_duration="10m",
        maxnodes=2, file="", verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=2, gpu=0, ram="20GB", disk="", jobs=32, job_duration="10m",
        maxnodes=1, file="", verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=2, gpu=5, ram="10GB", disk="", jobs=32, job_duration="10m",
        maxnodes=1, file="", verbose=True, content=mocked_content
    )

    # test with .submit files
    with TempDirectory() as d:
        d.write('test.submit', b'request_cpus = 1\n' + b'request_memory = 6000MB\n' + b'Queue 10')
        assert examine.prepare(
            cpu=0, gpu=0, ram="", disk="", jobs=1, job_duration="10m",
            maxnodes=0, file=d.path+'/test.submit', verbose=True, content=mocked_content
        )

    with TempDirectory() as d:
        d.write('test.submit', b'request_cpus = 1\n' + b'Queue 10')
        assert not examine.prepare(
            cpu=0, gpu=0, ram="", disk="", jobs=1, job_duration="10m",
            maxnodes=0, file=d.path+'/test.submit', verbose=True, content=mocked_content
        )

    with TempDirectory() as d:
        d.write('test.submit', b'request_cpus = 1\n' + b'Queue 10')
        assert not examine.prepare(
            cpu=0, gpu=0, ram="1G", disk="", jobs=1, job_duration="",
            maxnodes=0, file=d.path+'/test.submit', verbose=True, content=mocked_content
        )

    with TempDirectory() as d:
        d.write('test.submit', b'request_cpus = 1c\n' + b'request_memory = 6000MBc\n' + b'Queue 10c')
        assert not examine.prepare(
            cpu=0, gpu=0, ram="", disk="", jobs=1, job_duration="",
            maxnodes=0, file=d.path+'/test.submit', verbose=True, content=mocked_content
        )


def test_slot_config():
    """
    Tests the slot loading method.
    :return:
    """
    mocked_content = mocked_collector().query()

    slots = collect.collect_slots(mocked_content)

    assert "SlotType" in slots['cpu2'][0]

    assert "SlotType" in examine.filter_slots(slots, "Static")[0]
    assert examine.filter_slots(slots, "Static")[0]["SlotType"] == "Static"

    assert "SlotType" in examine.filter_slots(slots, "Partitionable")[0]
    assert examine.filter_slots(slots, "Partitionable")[0]["SlotType"] == "Partitionable"


def test_slot_checking():
    """
    Tests the slot checking method.
    :return:
    """
    mocked_content = mocked_collector().query()

    slots = collect.collect_slots(mocked_content)

    assert "preview" in examine.check_slots(
        examine.filter_slots(slots, "static"),
        examine.filter_slots(slots, "partitionable"),
        1, 10.0, 0.0, 0, 1, 0.0, 0, verbose=False
    )
    assert "slots" in examine.check_slots(
        examine.filter_slots(slots, "static"),
        examine.filter_slots(slots, "partitionable"),
        1, 10.0, 0.0, 0, 1, 0.0, 0, verbose=False
    )
    assert examine.check_slots(
        examine.filter_slots(slots, "static"),
        examine.filter_slots(slots, "partitionable"),
        0, 10.0, 0.0, 0, 1, 0.0, 0, verbose=False
    ) == {'slots': [], 'preview': []}
    assert examine.check_slots(
        examine.filter_slots(slots, "static"),
        examine.filter_slots(slots, "partitionable"),
        0, 10.0, 0.0, 0, 1, 0.0, 0, verbose=False
    ) == {'slots': [], 'preview': []}


def test_slot_result():
    """
    Tests the result slots for correct number of similar jobs based on RAM
    :return:
    """
    mocked_content = mocked_collector().query()

    slots = collect.collect_slots(mocked_content)

    ram = 10.0
    result = examine.check_slots(
        examine.filter_slots(slots, "Static"),
        examine.filter_slots(slots, "Partitionable"),
        1, ram, 0.0, 0, 1, 0.0, 0, verbose=False
    )
    slots = result["slots"]
    previews = result["preview"]

    for preview in previews:
        if preview['fits'] != 'YES':
            # Ignore results that do not fit
            continue

        # Find the slot referenced in results (same node-name and RAM)
        for slot in slots:
            slot_name = slot['Machine']

            if slot_name == preview["Machine"] and \
                    slot["TotalSlotMemory"] == preview['TotalSlotMemory']:
                ram_ratio = int(float(slot["TotalSlotMemory"]) / ram)

                # Assume that number of similar jobs does not exceed RAM ratio
                assert preview['sim_jobs'] <= ram_ratio


# ------------------ Test slot fetching -------------------------


def test_slot_in_node():
    """
    test the slot in node function of the slot fetching
    :return:
    """
    slots = [
        {
            "cpu2": [{
                "TotalSlotCpus": 1,
                "TotalSlotDisk": 287.53,
                "TotalSlotMemory": 5.0,
                "SlotType": "static",
            }]
        },
        {
            "cpu3": [{
                "TotalSlotCpus": 1,
                "TotalSlotDisk": 287.68,
                "TotalSlotMemory": 5.0,
                "SlotType": "static",
            }]
        },
        {
            "cpu4": [{
                "TotalSlotCpus": 1,
                "TotalSlotDisk": 287.68,
                "TotalSlotMemory": 5.0,
                "SlotType": "static",
            }]
        }
    ]
    slot_a = {
        "cpu4": [{
            "TotalSlotCpus": 1,
            "TotalSlotDisk": 287.68,
            "TotalSlotMemory": 5.0,
            "SlotType": "static",
        }]
    }
    slot_b = {
        "cpu5": [{
            "TotalSlotCpus": 1,
            "TotalSlotDisk": 287.68,
            "TotalSlotMemory": 5.0,
            "SlotType": "static",
        }]
    }
    slot_c = {
        "cpu4": [{
            "TotalSlotCpus": 2,
            "TotalSlotDisk": 287.68,
            "TotalSlotMemory": 5.0,
            "SlotType": "static",
        }]
    }
    assert slot_a in slots
    assert slot_b not in slots
    assert slot_c not in slots


def test__memory_conversions():
    """
    test the memory conversion of the slot fetching
    :return:
    """
    size_disk = 1048576
    size_mem = 1024

    assert utils.mib_to_gib(size_mem) == 1.0
    assert utils.mib_to_gib(size_mem * 2) == 2.0
    assert utils.mib_to_gib(size_mem * 10) == 10.0

    assert utils.kib_to_gib(size_disk) == 1.0
    assert utils.kib_to_gib(size_disk * 2) == 2.0
    assert utils.kib_to_gib(size_disk * 10) == 10.0


def test_slot_reader():
    """
    Testing the slot fetching with an extract of a condor_status command output
    :return:
    """
    mocked_content = mocked_collector().query()
    collect.collect_slots(mocked_content)
