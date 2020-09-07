"""Module for testing the htcrystalball module."""
import os
import argparse
import pytest
import htcrystalball as big_balls
import fetch_slots as sloth
import my_modules.check_slots as checker


def test_storage_validator():
    """
    Tests the storage input validator.
    :return:
    """
    assert big_balls.validate_storage_size("20GB") == "20GB"
    with pytest.raises(argparse.ArgumentTypeError):
        assert big_balls.validate_storage_size("20")
        assert big_balls.validate_storage_size("20iGB")
        assert big_balls.validate_storage_size("20GBt")
        assert big_balls.validate_storage_size("20GB3")


def test_time_validator():
    """
    Tests the time input validator.
    :return:
    """
    assert big_balls.validate_duration("20") == "20"
    with pytest.raises(argparse.ArgumentTypeError):
        assert big_balls.validate_duration("20min")
        assert big_balls.validate_duration("20imn")
        assert big_balls.validate_duration("20mint")
        assert big_balls.validate_duration("20hs")


def test_split_storage():
    """
    Tests the splitting method for storage inputs.
    :return:
    """
    number = 10
    unit = "GB"
    assert big_balls.split_number_unit(str(number)) == [number, "GiB"]
    assert big_balls.split_number_unit(str(number) + "GiB") == [number, "GiB"]
    assert big_balls.split_number_unit("0" + unit) == [0.0, "GB"]
    assert big_balls.split_number_unit(str(number)) == [number, "GiB"]


def test_split_time():
    """
    Tests the splitting method for the time input.
    :return:
    """
    number = 10
    unit = "min"
    assert big_balls.split_duration_unit(str(number)) == [number, "min"]
    assert big_balls.split_duration_unit(str(number) + "min") == [number, "min"]
    assert big_balls.split_duration_unit("0" + unit) == [0, unit]
    assert big_balls.split_duration_unit(str(number)) == [number, "min"]


def test_conversions():
    """
    Tests the number conversion methods for storage size and time.
    :return:
    """
    assert big_balls.calc_to_bin(10.0, "GiB") == 10.0
    assert big_balls.calc_to_bin(10.0, "GiB") == 10
    assert big_balls.calc_to_bin(10.0, "GB") == 10.0
    assert big_balls.calc_to_bin(10, "GiB") == 10.0
    assert big_balls.calc_to_bin(10.0, "MiB") == 0.01
    assert big_balls.calc_to_bin(10.0, "KiB") == 1e-05
    assert big_balls.calc_to_bin(1.0, "TiB") == 1000.0
    assert big_balls.calc_to_bin(1.0, "PiB") == 1000000.0

    assert big_balls.calc_to_min(10.0, "h") == 600.0
    assert big_balls.calc_to_min(10.0, "min") == 10
    assert big_balls.calc_to_min(10.0, "min") == 10.0
    assert big_balls.calc_to_min(10, "min") == 10.0
    assert big_balls.calc_to_min(10.0, "s") <= 0.17
    assert big_balls.calc_to_min(1.0, "d") == 1440.0


def test_calc_manager():
    """
    Tests the method for preparing the slot checking.
    :return:
    """
    assert big_balls.prepare_checking(cpu=1, gpu=0, ram="10GB", disk="0", jobs=1,
                                      job_duration="10m", maxnodes=0, verbose=True)
    assert not big_balls.prepare_checking(cpu=0, gpu=1, ram="10GB", disk="0", jobs=1,
                                          job_duration="10m", maxnodes=0, verbose=True)
    assert not big_balls.prepare_checking(cpu=1, gpu=0, ram="0", disk="", jobs=1,
                                          job_duration="", maxnodes=0, verbose=True)
    assert big_balls.prepare_checking(cpu=1, gpu=1, ram="20GB", disk="", jobs=1,
                                      job_duration="10m", maxnodes=0, verbose=True)
    assert big_balls.prepare_checking(cpu=1, gpu=0, ram="10GB", disk="10GB",
                                      jobs=1, job_duration="10m", maxnodes=0, verbose=True)
    assert big_balls.prepare_checking(cpu=1, gpu=0, ram="10GB", disk="10GB",
                                      jobs=128, job_duration="15m", maxnodes=0, verbose=True)
    assert big_balls.prepare_checking(cpu=1, gpu=0, ram="10GB", disk="",
                                      jobs=1, job_duration="10m", maxnodes=1, verbose=True)
    assert big_balls.prepare_checking(cpu=8, gpu=0, ram="10GB", disk="",
                                      jobs=1, job_duration="10m", maxnodes=0, verbose=True)
    assert big_balls.prepare_checking(cpu=8, gpu=0, ram="80GB", disk="",
                                      jobs=4, job_duration="1h", maxnodes=0, verbose=True)
    assert big_balls.prepare_checking(cpu=2, gpu=0, ram="10GB", disk="",
                                      jobs=1, job_duration="10m", maxnodes=3, verbose=True)
    assert big_balls.prepare_checking(cpu=1, gpu=0, ram="20GB", disk="",
                                      jobs=1, job_duration="10m", maxnodes=2, verbose=True)
    assert big_balls.prepare_checking(cpu=2, gpu=0, ram="20GB", disk="",
                                      jobs=1, job_duration="", maxnodes=2, verbose=True)
    assert big_balls.prepare_checking(cpu=2, gpu=0, ram="20GB", disk="",
                                      jobs=32, job_duration="10m", maxnodes=1, verbose=True)
    assert big_balls.prepare_checking(cpu=2, gpu=5, ram="10GB", disk="",
                                      jobs=32, job_duration="10m", maxnodes=1, verbose=True)


def test_slot_config():
    """
    Tests the slot loading method.
    :return:
    """
    slots = big_balls.define_slots()
    assert "SlotType" in slots[0]["slot_size"][0]

    assert "SlotType" in big_balls.filter_slots(slots, "static")[0]
    assert big_balls.filter_slots(slots, "static")[0]["SlotType"] == "static"

    assert "SlotType" in big_balls.filter_slots(slots, "dynamic")[0]
    assert big_balls.filter_slots(slots, "dynamic")[0]["SlotType"] == "dynamic"

    if len(big_balls.filter_slots(slots, "gpu")) > 0:
        assert "SlotType" in big_balls.filter_slots(slots, "gpu")[0]
        assert big_balls.filter_slots(slots, "gpu")[0]["SlotType"] == "gpu"


def test_slot_checking():
    """
    Tests the slot checking method.
    :return:
    """
    slots = big_balls.define_slots()

    assert "preview" in checker.check_slots(big_balls.filter_slots(slots, "static"),
                                            big_balls.filter_slots(slots, "dynamic"),
                                            big_balls.filter_slots(slots, "gpu"),
                                            1, 10.0, 0.0, 0, 1, 0.0, 0, verbose=False)
    assert "slots" in checker.check_slots(big_balls.filter_slots(slots, "static"),
                                          big_balls.filter_slots(slots, "dynamic"),
                                          big_balls.filter_slots(slots, "gpu"),
                                          1, 10.0, 0.0, 0, 1, 0.0, 0, verbose=False)
    assert checker.check_slots(big_balls.filter_slots(slots, "static"),
                               big_balls.filter_slots(slots, "dynamic"),
                               big_balls.filter_slots(slots, "gpu"),
                               0, 10.0, 0.0, 0, 1, 0.0, 0, verbose=False) == {}
    assert checker.check_slots(big_balls.filter_slots(slots, "static"),
                               big_balls.filter_slots(slots, "dynamic"),
                               big_balls.filter_slots(slots, "gpu"),
                               0, 10.0, 0.0, 0, 1, 0.0, 0, verbose=False) == {}


def test_slot_result():
    """
    Tests the result slots for correct number of similar jobs based on RAM
    :return:
    """
    slots = big_balls.define_slots()
    ram = 10.0

    res = checker.check_slots(big_balls.filter_slots(slots, "static"),
                              big_balls.filter_slots(slots, "dynamic"),
                              big_balls.filter_slots(slots, "gpu"),
                              1, ram, 0.0, 0, 1, 0.0, 0, verbose=False)
    slots = res["slots"]
    preview = res["preview"]

    # Go through each result that says "fits"
    for previewed in preview:
        if previewed["fits"] == "YES":
            node_name = previewed["name"]
            # Check the slots for the one that the result references
            # to (same node-name and RAM amount)
            for slot in slots:
                if slot["node"] == node_name and "/" + slot["ram"] in previewed["ram_usage"]:
                    # once we found it we should assume that the number of
                    # similar jobs does NOT exceed the ratio of RAM
                    assert int(previewed["sim_jobs"]) <= int(float(slot["ram"]) / ram)


# ------------------ Test slot fetching -------------------------


def test_slot_in_node():
    """
    test the slot in node function of the slot fetching
    :return:
    """
    slots = [
        {"UtsnameNodename": "cpu2", "slot_size": [{"TotalSlotCpus": 1,
                                                   "TotalSlotDisk": 287.53,
                                                   "TotalSlotMemory": 5.0,
                                                   "SlotType": "static",
                                                   "TotalSlots": 12}]},
        {"UtsnameNodename": "cpu3", "slot_size": [{"TotalSlotCpus": 1,
                                                   "TotalSlotDisk": 287.68,
                                                   "TotalSlotMemory": 5.0,
                                                   "SlotType": "static",
                                                   "TotalSlots": 12}]},
        {"UtsnameNodename": "cpu4", "slot_size": [{"TotalSlotCpus": 1,
                                                   "TotalSlotDisk": 287.68,
                                                   "TotalSlotMemory": 5.0,
                                                   "SlotType": "static",
                                                   "TotalSlots": 12}]}
    ]
    slot_a = {"UtsnameNodename": "cpu4", "slot_size": [{"TotalSlotCpus": 1,
                                                        "TotalSlotDisk": 287.68,
                                                        "TotalSlotMemory": 5.0,
                                                        "SlotType": "static",
                                                        "TotalSlots": 12}]}
    slot_b = {"UtsnameNodename": "cpu5", "slot_size": [{"TotalSlotCpus": 1,
                                                        "TotalSlotDisk": 287.68,
                                                        "TotalSlotMemory": 5.0,
                                                        "SlotType": "static",
                                                        "TotalSlots": 12}]}
    slot_c = {"UtsnameNodename": "cpu4", "slot_size": [{"TotalSlotCpus": 2,
                                                        "TotalSlotDisk": 287.68,
                                                        "TotalSlotMemory": 5.0,
                                                        "SlotType": "static",
                                                        "TotalSlots": 12}]}
    assert slot_a in slots
    assert slot_b not in slots
    assert slot_c not in slots


def test_nodename_in_list():
    """
    test the nodename in list function of the slot fetching
    :return:
    """
    slots = [
        {"UtsnameNodename": "cpu2", "slot_size": [{"TotalSlotCpus": 1,
                                                   "TotalSlotDisk": 287.53,
                                                   "TotalSlotMemory": 5.0,
                                                   "SlotType": "static",
                                                   "TotalSlots": 12}]},
        {"UtsnameNodename": "cpu3", "slot_size": [{"TotalSlotCpus": 1,
                                                   "TotalSlotDisk": 287.68,
                                                   "TotalSlotMemory": 5.0,
                                                   "SlotType": "static",
                                                   "TotalSlots": 12}]},
        {"UtsnameNodename": "cpu4", "slot_size": [{"TotalSlotCpus": 1,
                                                   "TotalSlotDisk": 287.68,
                                                   "TotalSlotMemory": 5.0,
                                                   "SlotType": "static",
                                                   "TotalSlots": 12}]}
    ]

    assert sloth.nodename_in_list("cpu2", slots) != -1
    assert sloth.nodename_in_list("cpu3", slots) != -1
    assert sloth.nodename_in_list("cpu5", slots) == -1
    assert sloth.nodename_in_list("cpu21", slots) == -1
    assert sloth.nodename_in_list("cpU2", slots) == -1


def test__memory_conversions():
    """
    test the memory conversion of the slot fetching
    :return:
    """
    size_disk = 1048576
    size_mem = 1024

    assert sloth.calc_mem_size(size_mem) == 1.0
    assert sloth.calc_mem_size(size_mem * 2) == 2.0
    assert sloth.calc_mem_size(size_mem * 10) == 10.0

    assert sloth.calc_disk_size(size_disk) == 1.0
    assert sloth.calc_disk_size(size_disk * 2) == 2.0
    assert sloth.calc_disk_size(size_disk * 10) == 10.0


def test_slot_reader():
    """
    Testing the slot fetching with an exctract of a condor_status command output
    :return:
    """
    slots_in = sloth.read_slots(os.path.dirname(os.path.abspath(__file__)) + "/htcondor_status_long.txt")
    sloth.format_slots(slots_in["slots"])
