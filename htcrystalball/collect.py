"""Retrieve, format, and store a system's condor slot configuration."""

from htcrystalball.utils import kib_to_gib, mib_to_gib


def collect_slots(content: object) -> dict:
    """Get the condor config and create a dict."""
    unique_slots = {}
    sim_slot_values = []

    for slot in content:
        nodename = slot['Machine']

        slot_as_dict = {
            'TotalSlotCpus': int(slot.get('TotalSlotCpus', 0)),
            'TotalSlotGPUs': int(slot.get('TotalSlotGPUs', 0)),
            'TotalSlotDisk': kib_to_gib(float(slot.get('TotalSlotDisk', 0.0))),
            'TotalSlotMemory': mib_to_gib(float(slot.get('TotalSlotMemory', 0.0))),
            'SlotType': slot['SlotType']
        }

        if nodename not in unique_slots:
            unique_slots[nodename] = []
            unique_slots[nodename].append(slot_as_dict)
            unique_slots[nodename][0]["SimSlots"] = 1
            sim_slot_values.append({'node': nodename, "slot": slot_as_dict, "sim_slots": 1})
        elif slot_as_dict not in unique_slots[nodename]:
            slot_as_dict["SimSlots"] = 1
            unique_slots[nodename].append(slot_as_dict)
        elif slot_as_dict in unique_slots[nodename]:
            for slot_number in range(len(unique_slots[nodename])):
                if slot_as_dict == unique_slots[nodename][slot_number]:
                    unique_slots[nodename][slot_number]["SimSlots"] += 1

    return unique_slots
