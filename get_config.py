import json


def dict_equals(dict_a: dict, dict_b: dict):
    """
    Compares keys and values of two dictionarys.
    If the number of shared items equals the length of both dictionarys, they are considered as equal.
    :param dict_a:
    :param dict_b:
    :return:
    """
    shared_items = {k: dict_a[k] for k in dict_a if k in dict_b and dict_a[k] == dict_b[k]}
    if len(shared_items) == len(dict_a) and len(shared_items) == len(dict_b):
        return True
    else:
        return False


def slot_in_node(slot_a: dict, slots: list) -> bool:
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
    Formats the dictionary of slots into one similar to the already used keys and values in htcrystal_ball
    :param slots:
    :return:
    """
    formatted = {"slots": []}
    count = 0

    while count < len(slots):
        formatted_slot = {"node": slots[count]["UtsnameNodename"],
                          "total_ram": calc_mem_size(slots[count]["TotalMemory"]),
                          "total_disk": calc_disk_size(slots[count]["TotalDisk"]),
                          "slots_in_use": 0,
                          "ram_in_use": 0,
                          "slot_size": {"cores": int(float(slots[count]["TotalSlotCpus"])),
                                        "disk_amount": calc_disk_size(slots[count]["TotalSlotDisk"]),
                                        "ram_amount": calc_mem_size(slots[count]["TotalSlotMemory"])
                                        }
                          }
        if slots[count]["SlotType"] == "Partitionable" or slots[count]["SlotType"] == "Dynamic":
            if "gpu" in slots[count]["UtsnameNodename"]:
                formatted_slot["type"] = "gpu"
            else:
                formatted_slot["type"] = "dynamic"
            formatted_slot["total_slots"] = int(float(slots[count]["TotalCpus"]))

        elif slots[count]["SlotType"] == "Static":
            formatted_slot["type"] = "static"
            formatted_slot["total_slots"] = int(float(slots[count]["TotalSlots"]))

        if not slot_in_node(formatted_slot, formatted["slots"]):
            formatted["slots"].append(formatted_slot)
        count += 1
    return formatted


def read_slots(filename: str) -> dict:
    """
    Reads the output of condor_status -long line by line and creates a dict
    :param filename:
    :return:
    """
    status = {"slots": []}

    with open(filename) as f:
        content = f.readlines()

    slot = {}
    for line in content:
        line = line.replace("\n", "")
        if line != "":
            pairs = line.split(' = ')
            key = pairs[0].strip().replace("'", "")
            value = pairs[1].strip().replace("'", "")
            if key in ("SlotType", "TotalCpus", "TotalDisk", "UtsnameNodename", "Name", "TotalMemory", "TotalSlotCpus",
                       "TotalSlotDisk", "TotalSlotMemory", "TotalSlots"):
                if key == "Name":
                    value = line.split('@')[0]
                slot[key] = value.replace("\"", "")
        else:
            if not slot_in_node(slot, status["slots"]) and (slot["SlotType"] != "Dynamic" or "gpu" in slot["Name"]):
                status["slots"].append(slot)
            slot = {}

    return status


def write_slots(filename: str, content: dict):
    """
    Writes the output dict into a config file
    :param filename:
    :param content:
    :return:
    """
    with open('config/slots_check.json', 'w') as json_file:
        json.dump(content, json_file)


if __name__ == "__main__":
    in_file = "./htcondor_status_long.txt"
    out_file = "config/slots_check.json"

    slots_in = read_slots(in_file)
    slots_out = format_slots(slots_in["slots"])

    write_slots(out_file, slots_out)

print("DONE")
