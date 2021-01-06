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
            'TotalSlots': int(slot.get('TotalSlots', 0)),
            'TotalSlotDisk': kib_to_gib(float(slot.get('TotalSlotDisk', 0.0))),
            'TotalSlotMemory': mib_to_gib(float(slot.get('TotalSlotMemory', 0.0))),
            'SlotType': slot['SlotType']
        }
        if slot_as_dict['TotalSlotGPUs'] != 0:
            slot_as_dict['SlotType'] = "GPU"

        if nodename not in unique_slots:
            unique_slots[nodename] = {}
            unique_slots[nodename]['Machine'] = nodename
            unique_slots[nodename]["slot_size"] = []
            unique_slots[nodename]["slot_size"].append(slot_as_dict)
            sim_slot_values.append({'node': nodename, "slot": slot_as_dict, "sim_slots": 1})
        elif slot_as_dict not in unique_slots[nodename]["slot_size"]:
            unique_slots[nodename]["slot_size"].append(slot_as_dict)
            sim_slot_values.append({'node': nodename, "slot": slot_as_dict, "sim_slots": 1})
        elif slot_as_dict in unique_slots[nodename]["slot_size"]:
            for slot_number in range(len(sim_slot_values)):
                if sim_slot_values[slot_number]["node"] == nodename \
                        and sim_slot_values[slot_number]["slot"] == slot_as_dict:
                    sim_slot_values[slot_number]["sim_slots"] += 1

    for elem in sim_slot_values:
        for slot_number in range(len(unique_slots[elem["node"]]["slot_size"])):
            if elem["slot"] == unique_slots[elem["node"]]["slot_size"][slot_number]:
                unique_slots[elem["node"]]["slot_size"][slot_number]["SimSlots"] = elem["sim_slots"]

    return unique_slots
