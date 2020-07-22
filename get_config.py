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


def nodename_in_list(name: str, slots: list) -> int:
    count = 0
    while count < len(slots):
        if name == slots[count]["node"]:
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
    Formats the dictionary of slots into one similar to the already used keys and values in htcrystalball
    :param slots:
    :return:
    """
    formatted = {"slots": []}
    count = 0

    while count < len(slots):
        slot = slots[count]

        slot_size = {"cores": int(float(slot["TotalSlotCpus"])),
                     "disk": calc_disk_size(slot["TotalSlotDisk"]),
                     "ram": calc_mem_size(slot["TotalSlotMemory"])}

        if slot["SlotType"] == "Partitionable" or slot["SlotType"] == "Dynamic":
            if "gpu" in slot["UtsnameNodename"]:
                slot_size["type"] = "gpu"
                slot_size["total_slots"] = int(int(slot["TotalSlots"]))
                slot_size["gpus"] = int(float(slot["TotalSlotGPUs"]))
            else:
                slot_size["type"] = "dynamic"
                slot_size["total_slots"] = int(float(slot["TotalSlots"]))

        elif slot["SlotType"] == "Static":
            slot_size["type"] = "static"
            slot_size["total_slots"] = int(float(slot["TotalSlots"]))

        node_in_list = nodename_in_list(slot["UtsnameNodename"], formatted["slots"])

        if node_in_list != -1:
            if not slot_in_node(slot_size, formatted["slots"][node_in_list]["slot_size"]):
                formatted["slots"][node_in_list]["slot_size"].append(slot_size)
        else:
            formatted_slot = {"node": slot["UtsnameNodename"],
                              "slot_size": [slot_size]}
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
                       "TotalSlotDisk", "TotalSlotMemory", "TotalSlots", "TotalGPUs", "TotalSlotGPUs"):
                if key == "Name":
                    value = line.split('@')[0]
                slot[key] = value.replace("\"", "")
        else:
            if not slot_in_node(slot, status["slots"]):
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
    with open('config/slots_check3.json', 'w') as json_file:
        json.dump(content, json_file)


if __name__ == "__main__":
    in_file = "./htcondor_status_long.txt"
    out_file = "config/slots_check.json"

    slots_in = read_slots(in_file)
    slots_out = format_slots(slots_in["slots"])

    write_slots(out_file, slots_out)

print("DONE")
