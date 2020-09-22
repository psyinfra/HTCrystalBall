"""Retrieve, format, and store a system's condor slot configuration."""

import htcondor

from typing import Union

from htcrystalball.utils import kib_to_gib, mib_to_gib


def collect_slots(filename: Union[str, None] = None) -> dict:
    """Get the condor config and creates a dict."""
    projection = ["SlotType", "UtsnameNodename", "TotalSlotCpus", "TotalSlotDisk", "TotalSlotMemory", "TotalSlots",
                  "TotalSlotGPUs"]
    unique_slots = {}

    if filename is None:
        coll = htcondor.Collector()
        content = coll.query(htcondor.AdTypes.Startd, constraint='SlotType != "Dynamic"', projection=projection)
        for slot in content:
            nodename = slot['UtsnameNodename']
            slot_as_dict = {
                            'TotalSlotCpus': int(slot.get('TotalSlotCpus', 0)),
                            'TotalSlotGPUs': int(slot.get('TotalSlotGPUs', 0)),
                            'TotalSlots': int(slot.get('TotalSlots', 0)),
                            'TotalSlotDisk': kib_to_gib(float(slot.get('TotalSlotDisk', 0.0))),
                            'TotalSlotMemory': mib_to_gib(float(slot.get('TotalSlotMemory', 0.0))),
                            'SlotType': slot['SlotType']
                            }
            if slot_as_dict['TotalSlotGPUs'] != 0:
                slot_as_dict['SlotType'] = "GPU"

            if nodename not in unique_slots:
                unique_slots[nodename] = {}
                unique_slots[nodename]['UtsnameNodename'] = nodename
                unique_slots[nodename]["slot_size"] = []
                unique_slots[nodename]["slot_size"].append(slot_as_dict)
            elif slot_as_dict not in unique_slots[nodename]["slot_size"]:
                unique_slots[nodename]["slot_size"].append(slot_as_dict)

    else:
        with open(filename) as file:
            lines = file.readlines()

        slot = {}
        nodename = ""

        for line in lines:
            line = line.replace("\n", "")
            if line != "":
                pairs = line.split(' = ')
                key = pairs[0].strip().replace("'", "")
                value = pairs[1].strip().replace("'", "")

                if key in projection:
                    if key == "UtsnameNodename":
                        nodename = value.replace("\"", "")
                        if nodename not in unique_slots:
                            unique_slots[nodename] = {}
                            unique_slots[nodename]['UtsnameNodename'] = nodename
                            unique_slots[nodename]["slot_size"] = []
                        continue

                    slot[key] = value.replace("\"", "")
            else:
                if slot['TotalSlotGPUs'] != 0:
                    slot['SlotType'] = "GPU"
                if slot not in unique_slots[nodename]["slot_size"]:
                    unique_slots[nodename]["slot_size"].append(slot)
                slot = {}

    return unique_slots
