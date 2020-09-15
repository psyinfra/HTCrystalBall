"""Retrieve, format, and store a system's condor slot configuration."""

from . import SLOTS_CONFIGURATION
from .utils import kib_to_gib, mib_to_gib
from typing import Union
import json
import htcondor


def node_name_in_list(name: str, slots: list) -> Union[int, None]:
    """Check if a node name is already in a list of slots."""
    try:
        return [slot['UtsnameNodename'] for slot in slots].index(name)
    except ValueError:
        return None


def format_slots(slots: list) -> dict:
    """
    Reassign slot values to new keys for compatibility.

    The dictionary of slots is formatted into a new dictionary similar to the
    already used key:value pairs in HTCrystalball.
    """
    formatted = {"slots": []}

    for slot in slots:
        # TODO: Check if float conversion is necessary
        name = slot['UtsnameNodename']
        n_cpus = int(slot.get('TotalSlotCpus', 0))
        n_gpus = int(slot.get('TotalSlotGPUs', 0))
        n_slots = int(slot.get('TotalSlots', 0))
        disk = float(slot.get('TotalSlotDisk', 0.0))
        ram = float(slot.get('TotalSlotMemory', 0.0))
        slot_type = slot['SlotType']

        slot_size = {
            "TotalSlotCpus": n_cpus,
            "TotalSlotDisk": kib_to_gib(disk),
            "TotalSlotMemory": mib_to_gib(ram)
        }

        if slot_type == "Partitionable" or slot_type == "Dynamic":
            if "gpu" in name and n_gpus != 0:
                slot_size["SlotType"] = "gpu"
                slot_size["TotalSlotGPUs"] = n_gpus
            else:
                slot_size["SlotType"] = "dynamic"
                slot_size["TotalSlotGPUs"] = 0

        elif slot_type == "Static":
            slot_size["SlotType"] = "static"

        slot_size["TotalSlots"] = n_slots
        node_in_list = node_name_in_list(
            slot["UtsnameNodename"],
            formatted["slots"]
        )

        if node_in_list is not None:
            if slot_size not in formatted["slots"][node_in_list]["slot_size"]:
                formatted["slots"][node_in_list]["slot_size"].append(slot_size)
        else:
            formatted_slot = {
                'UtsnameNodename': name,
                'slot_size': [slot_size]
            }
            formatted["slots"].append(formatted_slot)

    return formatted


def collect_slots(filename: Union[str, None] = None) -> dict:
    """Get the condor config and creates a dict."""
    status = {"slots": []}
    projection = [
        "SlotType", "UtsnameNodename", "Name", "TotalSlotCpus",
        "TotalSlotDisk", "TotalSlotMemory", "TotalSlots", "TotalSlotGPUs"
    ]

    if filename is None:
        coll = htcondor.Collector()
        content = coll.query(
            htcondor.AdTypes.Startd,
            projection=projection
        )
        for slot in content:
            if "Name" in slot:
                value = slot["Name"].split('@')[0]
                slot["Name"] = value.replace("\"", "")

            if slot not in status["slots"]:
                status["slots"].append(slot)
    else:
        with open(filename) as file:
            lines = file.readlines()

        slot = {}

        for line in lines:
            line = line.replace("\n", "")
            if line != "":
                pairs = line.split(' = ')
                key = pairs[0].strip().replace("'", "")
                value = pairs[1].strip().replace("'", "")

                if key in projection:
                    if key == "Name":
                        value = line.split('@')[0]
                    slot[key] = value.replace("\"", "")
            else:
                if slot not in status["slots"]:
                    status["slots"].append(slot)
                slot = {}

    return status


def write_slots(content: dict):
    """Write the output dict into a config file."""
    with open(SLOTS_CONFIGURATION, 'w+') as json_file:
        json.dump(content, json_file)
