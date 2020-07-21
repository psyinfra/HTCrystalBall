import json


def dict_equals(dict_a: dict, dict_b: dict):
    shared_items = {k: dict_a[k] for k in dict_a if k in dict_b and dict_a[k] == dict_b[k]}
    print(len(shared_items))
    if len(shared_items) == 9:
        return True
    else:
        return False


def slot_in_node(slot_a: dict, slots: list) -> bool:
    count = 0
    while count < len(slots):
        if dict_equals(slot_a, slots[count]):
            return True
        count += 1
    return False


def calc_disk_size(size: str) -> float:
    return float("{0:.2f}".format(float(size) / 2 ** 20))


def calc_mem_size(size: str) -> float:
    return float("{0:.2f}".format(float(size) / 2 ** 10))


def format_slots(slots: list) -> dict:
    formatted = {"slots": []}
    count = 0

    while count < len(slots):
        formatted_slot = {"node": slots[count]["UtsnameNodename"],
                          "total_ram": calc_mem_size(slots[count]["TotalMemory"]),
                          "total_disk": calc_disk_size(slots[count]["TotalDisk"]),
                          "slots_in_use": 0,
                          "ram_in_use": 0}
        if slots[count]["SlotType"] == "Partitionable" or slots[count]["SlotType"] == "Dynamic":
            if "gpu" in slots[count]["UtsnameNodename"]:
                formatted_slot["type"] = "gpu"
            else:
                formatted_slot["type"] = "dynamic"
            number = slots[count]["TotalCpus"]
            formatted_slot["total_slots"] = int(float(number))
            formatted_slot["slot_size"] = {}
            number = slots[count]["TotalSlotCpus"]
            formatted_slot["slot_size"]["cores"] = int(float(number))
            formatted_slot["slot_size"]["disk_amount"] = calc_disk_size(slots[count]["TotalSlotDisk"])
            formatted_slot["slot_size"]["ram_amount"] = calc_mem_size(slots[count]["TotalSlotMemory"])
        elif slots[count]["SlotType"] == "Static":
            formatted_slot["type"] = "static"
            number = slots[count]["TotalSlots"]
            formatted_slot["total_slots"] = int(float(number))
            formatted_slot["slot_size"] = {}
            number = slots[count]["TotalSlotCpus"]
            formatted_slot["slot_size"]["cores"] = int(float(number))
            formatted_slot["slot_size"]["disk_amount"] = calc_disk_size(slots[count]["TotalSlotDisk"])
            formatted_slot["slot_size"]["ram_amount"] = calc_mem_size(slots[count]["TotalSlotMemory"])

        if not slot_in_node(slot, formatted["slots"]):
            formatted["slots"].append(formatted_slot)
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
        if not slot_in_node(slot, status["slots"]) and (slot["SlotType"] != "Dynamic" or "gpu" in slot["Name"]):
            status["slots"].append(slot)
        slot = {}

status = format_slots(status["slots"])

with open('config/slots_check.json', 'w') as json_file:
    json.dump(status, json_file)

print("DONE")
