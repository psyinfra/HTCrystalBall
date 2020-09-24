"""Module for testing the htcrystalball module."""

import argparse

from pytest import raises as praises

from htcrystalball import examine, collect, utils


COLL_QUERY = [
        {
            "UtsnameNodename": "cpu2",
            "TotalSlotCpus": "1",
            "TotalSlotDisk": "287530000",
            "TotalSlotMemory": "500000",
            "SlotType": "Static",
            "TotalSlots": "12"
        },
        {
            "UtsnameNodename": "cpu3",
            "TotalSlotCpus": "1",
            "TotalSlotDisk": "287680000",
            "TotalSlotMemory": "500000",
            "SlotType": "Partitionable",
            "TotalSlots": "12"
        },
        {
            "UtsnameNodename": "gpu1",
            "TotalSlotCpus": "1",
            "TotalSlotGPUs": "4",
            "TotalSlotDisk": "287680000",
            "TotalSlotMemory": "500000",
            "SlotType": "Partitionable",
            "TotalSlots": "12"
        }
    ]


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


def test_calc_manager():
    """
    Tests the method for preparing the slot checking.
    :return:
    """
    mocked_content = COLL_QUERY

    assert examine.prepare(
        cpu=1, gpu=0, ram="10GB", disk="0", jobs=1, job_duration="10m",
        maxnodes=0, verbose=True, content=mocked_content
    )
    assert not examine.prepare(
        cpu=0, gpu=1, ram="10GB", disk="0", jobs=1, job_duration="10m",
        maxnodes=0, verbose=True, content=mocked_content
    )
    assert not examine.prepare(
        cpu=1, gpu=0, ram="0", disk="", jobs=1, job_duration="", maxnodes=0,
        verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=1, gpu=1, ram="20GB", disk="", jobs=1, job_duration="10m",
        maxnodes=0, verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=1, gpu=0, ram="10GB", disk="10GB", jobs=1, job_duration="10m",
        maxnodes=0, verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=1, gpu=0, ram="10GB", disk="10GB", jobs=128, job_duration="15m",
        maxnodes=0, verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=1, gpu=0, ram="10GB", disk="", jobs=1, job_duration="10m",
        maxnodes=1, verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=8, gpu=0, ram="10GB", disk="", jobs=1, job_duration="10m",
        maxnodes=0, verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=8, gpu=0, ram="80GB", disk="", jobs=4, job_duration="1h",
        maxnodes=0, verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=2, gpu=0, ram="10GB", disk="", jobs=1, job_duration="10m",
        maxnodes=3, verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=1, gpu=0, ram="20GB", disk="", jobs=1, job_duration="10m",
        maxnodes=2, verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=2, gpu=0, ram="20GB", disk="", jobs=1, job_duration="",
        maxnodes=2, verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=2, gpu=0, ram="20GB", disk="", jobs=32, job_duration="10m",
        maxnodes=1, verbose=True, content=mocked_content
    )
    assert examine.prepare(
        cpu=2, gpu=5, ram="10GB", disk="", jobs=32, job_duration="10m",
        maxnodes=1, verbose=True, content=mocked_content
    )


def test_slot_config():
    """
    Tests the slot loading method.
    :return:
    """
    mocked_content = COLL_QUERY

    slots = collect.collect_slots(mocked_content)

    assert "SlotType" in slots['cpu2']["slot_size"][0]

    assert "SlotType" in examine.filter_slots(slots, "Static")[0]
    assert examine.filter_slots(slots, "Static")[0]["SlotType"] == "Static"

    assert "SlotType" in examine.filter_slots(slots, "Partitionable")[0]
    assert examine.filter_slots(slots, "Partitionable")[0]["SlotType"] == "Partitionable"

    if len(examine.filter_slots(slots, "GPU")) > 0:
        assert "SlotType" in examine.filter_slots(slots, "GPU")[0]
        assert examine.filter_slots(slots, "GPU")[0]["SlotType"] == "GPU"


def test_slot_checking():
    """
    Tests the slot checking method.
    :return:
    """
    mocked_content = COLL_QUERY

    slots = collect.collect_slots(mocked_content)

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


def test_slot_result():
    """
    Tests the result slots for correct number of similar jobs based on RAM
    :return:
    """
    mocked_content = COLL_QUERY

    slots = collect.collect_slots(mocked_content)

    ram = 10.0
    result = examine.check_slots(
        examine.filter_slots(slots, "Static"),
        examine.filter_slots(slots, "Partitionable"),
        examine.filter_slots(slots, "GPU"),
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
    mocked_content = COLL_QUERY
    collect.collect_slots(mocked_content)
