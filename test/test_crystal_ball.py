#!/usr/bin/env python3
"""
Module for testing the htcrystal_ball module
"""
import os
import sys
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')
import htcrystal_ball as big_balls


def test_storage_validator():
    """
    Tests the storage input validator.
    :return:
    """
    assert big_balls.validate_storage_size("20GB") == "20GB"
    assert big_balls.validate_storage_size("20") == "20"
    assert big_balls.validate_storage_size("20iGB") == "20GiB"
    assert big_balls.validate_storage_size("20GBt") == "20GB"
    assert big_balls.validate_storage_size("20GB3") == "20GB"


def test_time_validator():
    """
    Tests the time input validator.
    :return:
    """
    assert big_balls.validate_storage_size("20min") == "20min"
    assert big_balls.validate_storage_size("20") == "20"
    assert big_balls.validate_storage_size("20imn") == "20min"
    assert big_balls.validate_storage_size("20mint") == "20min"
    assert big_balls.validate_storage_size("20hs") == "20min"


def test_split_storage():
    """
    Tests the splitting method for storage inputs.
    :return:
    """
    number = 10
    unit = "GB"
    assert big_balls.split_number_unit(str(number)) == [number, "GiB"]
    assert big_balls.split_number_unit(str(number) + "GiB") == [number, "GiB"]
    assert big_balls.split_number_unit("0" + unit) == "GiB"
    assert big_balls.split_number_unit(str(number)) == number


def test_split_time():
    """
    Tests the splitting method for the time input.
    :return:
    """
    number = 10
    unit = "min"
    assert big_balls.split_duration_unit(str(number)) == [number, "min"]
    assert big_balls.split_duration_unit(str(number) + "min") == [number, "min"]
    assert big_balls.split_duration_unit("0" + unit) == "min"
    assert big_balls.split_duration_unit(str(number)) == number


def test_conversions():
    """
    Tests the number conversion methods for storage size and time.
    :return:
    """
    assert big_balls.calc_to_bin(10.0, "GiB") == 10.0
    assert big_balls.calc_to_bin(10.0, "GiB") == 10
    assert big_balls.calc_to_bin(10.0, "GB") == 10.0
    assert big_balls.calc_to_bin(10, "GiB") == 10.0
    assert big_balls.calc_to_bin(10.0, "MiB") == 10.0

    assert big_balls.calc_to_min(10.0, "h") == 10.0
    assert big_balls.calc_to_min(10.0, "min") == 10
    assert big_balls.calc_to_min(10.0, "min") == 10.0
    assert big_balls.calc_to_min(10, "min") == 10.0
    assert big_balls.calc_to_min(10.0, "s") == 10.0


def test_calc_manager():
    """
    Tests the method for preparing the slot checking.
    :return:
    """
    assert big_balls.prepare_checking(None, cpu=1, gpu=0, ram="10GB", disk="0", jobs=1,
                                      job_duration="10m", maxnodes=0)
    assert big_balls.prepare_checking(None, cpu=0, gpu=1, ram="10GB", disk="0", jobs=1,
                                      job_duration="10m", maxnodes=0)
    assert big_balls.prepare_checking(None, cpu=1, gpu=0, ram="0", disk="", jobs=1,
                                      job_duration="", maxnodes=0)
    assert big_balls.prepare_checking(None, cpu=1, gpu=1, ram="20GB", disk="", jobs=1,
                                      job_duration="10m", maxnodes=0)
    assert big_balls.prepare_checking(None, cpu=1, gpu=0, ram="10GB", disk="10GB",
                                      jobs=1, job_duration="10m", maxnodes=0)
    assert big_balls.prepare_checking(None, cpu=1, gpu=0, ram="10GB", disk="10GB",
                                      jobs=128, job_duration="15m", maxnodes=0)
    assert big_balls.prepare_checking(None, cpu=1, gpu=0, ram="10GB", disk="",
                                      jobs=1, job_duration="10m", maxnodes=1)
    assert big_balls.prepare_checking(None, cpu=8, gpu=0, ram="10GB", disk="",
                                      jobs=1, job_duration="10m", maxnodes=0)
    assert big_balls.prepare_checking(None, cpu=8, gpu=0, ram="80GB", disk="",
                                      jobs=4, job_duration="1h", maxnodes=0)
    assert big_balls.prepare_checking(None, cpu=2, gpu=0, ram="10GB", disk="",
                                      jobs=1, job_duration="10m", maxnodes=3)
    assert big_balls.prepare_checking(None, cpu=1, gpu=0, ram="20GB", disk="",
                                      jobs=1, job_duration="10m", maxnodes=2)
    assert big_balls.prepare_checking(None, cpu=2, gpu=0, ram="20GB", disk="",
                                      jobs=1, job_duration="", maxnodes=2)
    assert big_balls.prepare_checking(None, cpu=2, gpu=0, ram="20GB", disk="",
                                      jobs=32, job_duration="10m", maxnodes=1)


def test_slot_config():
    """
    Tests the slot loading method.
    :return:
    """
    slots = big_balls.define_slots()
    assert "static" in slots
    assert "dynamic" in slots
    assert "gpu" in slots


def test_slot_checking():
    """
    Tests the slot checking method.
    :return:
    """
    slots = big_balls.define_slots()

    assert "preview" in big_balls.check_slots(slots["static"], slots["dynamic"],
                                              slots["gpu"], 1, 10.0, 0.0, 0, 1, 0.0, 0)
    assert "nodes" in big_balls.check_slots(slots["static"], slots["dynamic"],
                                            slots["gpu"], 1, 10.0, 0.0, 0, 1, 0.0, 0)
    assert "preview" in big_balls.check_slots(slots["static"], slots["dynamic"],
                                              slots["gpu"], 0, 10.0, 0.0, 0, 1, 0.0, 0)
    assert "nodes" in big_balls.check_slots(slots["static"], slots["dynamic"],
                                            slots["gpu"], 0, 10.0, 0.0, 0, 1, 0.0, 0)
