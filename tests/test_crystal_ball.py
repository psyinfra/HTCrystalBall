"""Module for testing the htcrystalball module."""
import argparse
import json

from os import path
from pytest import fixture, raises as praises

from htcrystalball import examine, collect, utils


@fixture
def root_dir():
    """
    Defines the absolute path to this file.
    Returns:

    """
    return path.dirname(path.abspath(__file__))


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


def test_calc_manager(root_dir):
    """
    Tests the method for preparing the slot checking.
    :return:
    """

    root_dir = path.dirname(path.abspath(__file__))
    config_file = path.join(root_dir, 'example_config.json')

    assert examine.prepare(
        cpu=1, gpu=0, ram="10GB", disk="0", jobs=1, job_duration="10m",
        maxnodes=0, verbose=True, config_file=config_file
    )
    assert not examine.prepare(
        cpu=0, gpu=1, ram="10GB", disk="0", jobs=1, job_duration="10m",
        maxnodes=0, verbose=True, config_file=config_file
    )
    assert not examine.prepare(
        cpu=1, gpu=0, ram="0", disk="", jobs=1, job_duration="", maxnodes=0,
        verbose=True, config_file=config_file
    )
    assert examine.prepare(
        cpu=1, gpu=1, ram="20GB", disk="", jobs=1, job_duration="10m",
        maxnodes=0, verbose=True, config_file=config_file
    )
    assert examine.prepare(
        cpu=1, gpu=0, ram="10GB", disk="10GB", jobs=1, job_duration="10m",
        maxnodes=0, verbose=True, config_file=config_file
    )
    assert examine.prepare(
        cpu=1, gpu=0, ram="10GB", disk="10GB", jobs=128, job_duration="15m",
        maxnodes=0, verbose=True, config_file=config_file
    )
    assert examine.prepare(
        cpu=1, gpu=0, ram="10GB", disk="", jobs=1, job_duration="10m",
        maxnodes=1, verbose=True, config_file=config_file
    )
    assert examine.prepare(
        cpu=8, gpu=0, ram="10GB", disk="", jobs=1, job_duration="10m",
        maxnodes=0, verbose=True, config_file=config_file
    )
    assert examine.prepare(
        cpu=8, gpu=0, ram="80GB", disk="", jobs=4, job_duration="1h",
        maxnodes=0, verbose=True, config_file=config_file
    )
    assert examine.prepare(
        cpu=2, gpu=0, ram="10GB", disk="", jobs=1, job_duration="10m",
        maxnodes=3, verbose=True, config_file=config_file
    )
    assert examine.prepare(
        cpu=1, gpu=0, ram="20GB", disk="", jobs=1, job_duration="10m",
        maxnodes=2, verbose=True, config_file=config_file
    )
    assert examine.prepare(
        cpu=2, gpu=0, ram="20GB", disk="", jobs=1, job_duration="",
        maxnodes=2, verbose=True, config_file=config_file
    )
    assert examine.prepare(
        cpu=2, gpu=0, ram="20GB", disk="", jobs=32, job_duration="10m",
        maxnodes=1, verbose=True, config_file=config_file
    )
    assert examine.prepare(
        cpu=2, gpu=5, ram="10GB", disk="", jobs=32, job_duration="10m",
        maxnodes=1, verbose=True, config_file=config_file
    )


def test_slot_config(root_dir):
    """
    Tests the slot loading method.
    :return:
    """
    config_file = path.join(root_dir, 'example_config.json')

    with open(config_file) as f:
        slots = json.load(f)['slots']

    assert "SlotType" in slots[0]["slot_size"][0]

    assert "SlotType" in examine.filter_slots(slots, "static")[0]
    assert examine.filter_slots(slots, "static")[0]["SlotType"] == "static"

    assert "SlotType" in examine.filter_slots(slots, "partitionable")[0]
    assert examine.filter_slots(slots, "partitionable")[0]["SlotType"] == "partitionable"

    if len(examine.filter_slots(slots, "gpu")) > 0:
        assert "SlotType" in examine.filter_slots(slots, "gpu")[0]
        assert examine.filter_slots(slots, "gpu")[0]["SlotType"] == "gpu"


def test_slot_checking(root_dir):
    """
    Tests the slot checking method.
    :return:
    """
    config_file = path.join(root_dir, 'example_config.json')

    with open(config_file) as f:
        slots = json.load(f)['slots']

    assert "preview" in examine.check_slots(
        examine.filter_slots(slots, "static"),
        examine.filter_slots(slots, "partitionable"),
        examine.filter_slots(slots, "gpu"),
        1, 10.0, 0.0, 0, 1, 0.0, 0, verbose=False
    )
    assert "slots" in examine.check_slots(
        examine.filter_slots(slots, "static"),
        examine.filter_slots(slots, "partitionable"),
        examine.filter_slots(slots, "gpu"),
        1, 10.0, 0.0, 0, 1, 0.0, 0, verbose=False
    )
    assert examine.check_slots(
        examine.filter_slots(slots, "static"),
        examine.filter_slots(slots, "partitionable"),
        examine.filter_slots(slots, "gpu"),
        0, 10.0, 0.0, 0, 1, 0.0, 0, verbose=False
    ) == {}
    assert examine.check_slots(
        examine.filter_slots(slots, "static"),
        examine.filter_slots(slots, "partitionable"),
        examine.filter_slots(slots, "gpu"),
        0, 10.0, 0.0, 0, 1, 0.0, 0, verbose=False
    ) == {}


def test_slot_result(root_dir):
    """
    Tests the result slots for correct number of similar jobs based on RAM
    :return:
    """
    config_file = path.join(root_dir, 'example_config.json')

    with open(config_file) as f:
        slots = json.load(f)['slots']

    ram = 10.0
    result = examine.check_slots(
        examine.filter_slots(slots, "static"),
        examine.filter_slots(slots, "partitionable"),
        examine.filter_slots(slots, "gpu"),
        1, ram, 0.0, 0, 1, 0.0, 0, verbose=False
    )
    slots = result["slots"]
    previews = result["preview"]

    for preview in previews:
        if preview['fits'] != 'YES':
            # Ignore results that do not fit
            continue

        preview_name = preview["name"]
        preview_ram = preview['ram_usage']

        # Find the slot referenced in results (same node-name and RAM)
        for slot in slots:
            slot_name = slot['node']
            slot_ram = f'/{slot["ram"]}'

            if slot_name == preview_name and slot_ram in preview_ram:
                ram_ratio = int(float(slot['ram']) / ram)

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
            "UtsnameNodename": "cpu2",
            "slot_size": [{
                "TotalSlotCpus": 1,
                "TotalSlotDisk": 287.53,
                "TotalSlotMemory": 5.0,
                "SlotType": "static",
                "TotalSlots": 12
            }]
        },
        {
            "UtsnameNodename": "cpu3",
            "slot_size": [{
                "TotalSlotCpus": 1,
                "TotalSlotDisk": 287.68,
                "TotalSlotMemory": 5.0,
                "SlotType": "static",
                "TotalSlots": 12
            }]
        },
        {
            "UtsnameNodename": "cpu4",
            "slot_size": [{
                "TotalSlotCpus": 1,
                "TotalSlotDisk": 287.68,
                "TotalSlotMemory": 5.0,
                "SlotType": "static",
                "TotalSlots": 12
            }]
        }
    ]
    slot_a = {
        "UtsnameNodename": "cpu4",
        "slot_size": [{
            "TotalSlotCpus": 1,
            "TotalSlotDisk": 287.68,
            "TotalSlotMemory": 5.0,
            "SlotType": "static",
            "TotalSlots": 12
        }]
    }
    slot_b = {
        "UtsnameNodename": "cpu5",
        "slot_size": [{
            "TotalSlotCpus": 1,
            "TotalSlotDisk": 287.68,
            "TotalSlotMemory": 5.0,
            "SlotType": "static",
            "TotalSlots": 12
        }]
    }
    slot_c = {
        "UtsnameNodename": "cpu4",
        "slot_size": [{
            "TotalSlotCpus": 2,
            "TotalSlotDisk": 287.68,
            "TotalSlotMemory": 5.0,
            "SlotType": "static",
            "TotalSlots": 12
        }]
    }
    assert slot_a in slots
    assert slot_b not in slots
    assert slot_c not in slots


def test_nodename_in_list():
    """
    test the nodename in list function of the slot fetching
    :return:
    """
    slots = [
        {
            "UtsnameNodename": "cpu2",
            "slot_size": [{
                "TotalSlotCpus": 1,
                "TotalSlotDisk": 287.53,
                "TotalSlotMemory": 5.0,
                "SlotType": "static",
                "TotalSlots": 12
            }]
        },
        {
            "UtsnameNodename": "cpu3",
            "slot_size": [{
                "TotalSlotCpus": 1,
                "TotalSlotDisk": 287.68,
                "TotalSlotMemory": 5.0,
                "SlotType": "static",
                "TotalSlots": 12
            }]
        },
        {
            "UtsnameNodename": "cpu4",
            "slot_size": [{
                "TotalSlotCpus": 1,
                "TotalSlotDisk": 287.68,
                "TotalSlotMemory": 5.0,
                "SlotType": "static",
                "TotalSlots": 12
            }]
        }
    ]

    assert collect.node_name_in_list("cpu2", slots) is not None
    assert collect.node_name_in_list("cpu3", slots) is not None
    assert collect.node_name_in_list("cpu5", slots) is None
    assert collect.node_name_in_list("cpu21", slots) is None
    assert collect.node_name_in_list("cpU2", slots) is None


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


def test_slot_reader(root_dir):
    """
    Testing the slot fetching with an extract of a condor_status command output
    :return:
    """
    condor_status = path.join(root_dir, 'htcondor_status_long.txt')
    slots_in = collect.collect_slots(condor_status)
    collect.format_slots(slots_in["slots"])
