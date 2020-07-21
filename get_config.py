import json


def slot_equals(slot_a: dict, slot_b: dict) -> bool:
    """

    :param slot_a:
    :param slot_b:
    :return:
    """
    equals = slot_a["SlotType"] == slot_b["SlotType"] and slot_a["SlotType"] == "Static" \
        and slot_a["TotalCpus"] == slot_b["TotalCpus"] \
        and slot_a["TotalDisk"] == slot_b["TotalDisk"] \
        and slot_a["UtsnameNodename"] == slot_b["UtsnameNodename"] \
        and slot_a["TotalMemory"] == slot_b["TotalMemory"] \
        and slot_a["TotalSlotCpus"] == slot_b["TotalSlotCpus"] \
        and slot_a["TotalSlotDisk"] == slot_b["TotalSlotDisk"] \
        and slot_a["TotalSlotMemory"] == slot_b["TotalSlotMemory"] \
        and slot_a["TotalSlots"] == slot_b["TotalSlots"]
    return equals


def slot_in_node(slot_a: dict, slots: dict) -> bool:
    count = 0
    while count < len(slots):
        if slot_equals(slot_a, slots[count]):
            return True
        count += 1
    return False


def calc_disk_size(size: str) -> float:
    return float("{0:.2f}".format(float(size)/2**20))


def calc_mem_size(size: str) -> float:
    return float("{0:.2f}".format(float(size)/2**10))


def format_slots(slots: dict) -> dict:
    formatted = {"slots": []}
    count = 0

    while count < len(slots):
        slot = {"node": slots[count]["UtsnameNodename"],
                "total_ram": calc_mem_size(slots[count]["TotalMemory"]),
                "total_disk": calc_disk_size(slots[count]["TotalDisk"]),
                "slots_in_use": 0,
                "ram_in_use": 0}
        if slots[count]["SlotType"] == "Partitionable":
            slot["type"] = "dynamic"
            number = slots[count]["TotalCpus"]
            slot["total_slots"] = int(float(number))
        elif slots[count]["SlotType"] == "Static":
            slot["type"] = "static"
            number = slots[count]["TotalSlots"]
            slot["total_slots"] = int(float(number))
            slot["slot_size"] = {}
            number = slots[count]["TotalSlotCpus"]
            slot["slot_size"]["cores"] = int(float(number))
            slot["slot_size"]["disk_amount"] = calc_disk_size(slots[count]["TotalSlotDisk"])
            slot["slot_size"]["ram_amount"] = calc_mem_size(slots[count]["TotalSlotMemory"])
        else:
            slot["type"] = "gpu"
            print("GPU!")

        formatted["slots"].append(slot)
        count += 1
    return formatted


status = {"slots": []}

with open("./htcondor_status_long.txt") as f:
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
        if not slot_in_node(slot, status["slots"]) and slot["SlotType"] != "Dynamic":
            status["slots"].append(slot)
        slot = {}

status = format_slots(status["slots"])

with open('config/slots_check.json', 'w') as json_file:
    json.dump(status, json_file)

print("DONE")
