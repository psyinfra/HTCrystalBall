#!/usr/bin/env python3

"""Gets a systems condor slot configuration, formats it and writes it to a JSON file."""
import json
import htcondor

SLOTS_CONFIGURATION = "config/slots.json"


def dict_equals(dict_a: dict, dict_b: dict):
    """

    Compares keys and values of two dictionarys.
    If the number of shared items equals the length of
    both dictionarys, they are considered as equal.
    :param dict_a:
    :param dict_b:
    :return:
    """
    shared_items = {k: dict_a[k] for k in dict_a if k in dict_b and dict_a[k] == dict_b[k]}
    if len(shared_items) == len(dict_a) and len(shared_items) == len(dict_b):
        return True

    return False


def slot_exists(slot_a: dict, slots: list) -> bool:
    """
    Checks if a slot is already in a dictionary by checking whether
    it is equal to any already present slot.
    :param slot_a:
    :param slots:
    :return:
    """
    count = 0
    while count < len(slots):
        if dict_equals(slot_a, slots[count]):
            return True
        count += 1
    return False


def nodename_in_list(name: str, slots: list) -> int:
    """
    Check if a nodename is already in a list
    :param name:
    :param slots:
    :return:
    """
    count = 0
    while count < len(slots):
        if name == slots[count]["UtsnameNodename"]:
            return count
        count += 1
    return -1


def calc_disk_size(size: str) -> float:
    """
    Calculates the disk space in GiB (condor_status returns it in KiB not in GiB)
    :param size:
    :return:
    """
    return float("{0:.2f}".format(float(size) / 2 ** 20))


def calc_mem_size(size: str) -> float:
    """
    Calculates the memory in GiB (condor_status returns it in MiB not in GiB)
    :param size:
    :return:
    """
    return float("{0:.2f}".format(float(size) / 2 ** 10))


def format_slots(slots: list) -> dict:
    """
    Formats the dictionary of slots into one similar to the
    already used keys and values in htcrystalball
    :param slots:
    :return:
    """
    formatted = {"slots": []}
    count = 0

    while count < len(slots):
        slot = slots[count]

        slot_size = {"TotalSlotCpus": int(float(slot["TotalSlotCpus"])),
                     "TotalSlotDisk": calc_disk_size(slot["TotalSlotDisk"]),
                     "TotalSlotMemory": calc_mem_size(slot["TotalSlotMemory"])}

        if slot["SlotType"] == "Partitionable" or slot["SlotType"] == "Dynamic":
            if "gpu" in slot["UtsnameNodename"] and int(slot["TotalSlotGPUs"]) != 0:
                slot_size["SlotType"] = "gpu"
                slot_size["TotalSlotGPUs"] = int(float(slot["TotalSlotGPUs"]))
            else:
                slot_size["SlotType"] = "dynamic"
                slot_size["TotalSlotGPUs"] = 0

        elif slot["SlotType"] == "Static":
            slot_size["SlotType"] = "static"

        slot_size["TotalSlots"] = int(float(slot["TotalSlots"]))

        node_in_list = nodename_in_list(slot["UtsnameNodename"], formatted["slots"])

        if node_in_list != -1:
            if not slot_exists(slot_size, formatted["slots"][node_in_list]["slot_size"]):
                formatted["slots"][node_in_list]["slot_size"].append(slot_size)
        else:
            formatted_slot = {"UtsnameNodename": slot["UtsnameNodename"],
                              "slot_size": [slot_size]}
            formatted["slots"].append(formatted_slot)

        count += 1
    return formatted


def read_slots(filename: str) -> dict:
    """
    Gets the condor config and creates a dict
    :return:
    """
    status = {"slots": []}

    if filename == " ":
        coll = htcondor.Collector()
        content = coll.query(htcondor.AdTypes.Startd, projection=["SlotType",
                                                                  "UtsnameNodename",
                                                                  "Name",
                                                                  "TotalSlotCpus",
                                                                  "TotalSlotDisk",
                                                                  "TotalSlotMemory",
                                                                  "TotalSlots",
                                                                  "TotalSlotGPUs"])
        for slot in content:
            if "Name" in slot:
                value = slot["Name"].split('@')[0]
                slot["Name"] = value.replace("\"", "")

            if not slot_exists(slot, status["slots"]):
                status["slots"].append(slot)
    else:
        with open(filename) as file:
            content = file.readlines()

        slot = {}
        for line in content:
            line = line.replace("\n", "")
            if line != "":
                pairs = line.split(' = ')
                key = pairs[0].strip().replace("'", "")
                value = pairs[1].strip().replace("'", "")
                if key in ("SlotType", "UtsnameNodename", "Name", "TotalSlotCpus",
                           "TotalSlotDisk", "TotalSlotMemory", "TotalSlots", "TotalSlotGPUs"):
                    if key == "Name":
                        value = line.split('@')[0]
                    slot[key] = value.replace("\"", "")
            else:
                if not slot_exists(slot, status["slots"]):
                    status["slots"].append(slot)
                slot = {}

    return status


def write_slots(content: dict):
    """
    Writes the output dict into a config file
    :param content:
    :return:
    """
    with open(SLOTS_CONFIGURATION, 'w') as json_file:
        json.dump(content, json_file)


if __name__ == "__main__":
    SLOTS_IN = read_slots(" ")
    SLOTS_OUT = format_slots(SLOTS_IN["slots"])

    write_slots(SLOTS_OUT)
