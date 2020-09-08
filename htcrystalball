#!/usr/bin/env python3

"""Gives users a preview on how and where they can execute their HTcondor compatible scripts."""
import argparse
import json
import re
import logging
import my_modules.check_slots as slot_checker
import fetch_slots as sloth

# External (root level) logging level
logging.basicConfig(level=logging.ERROR)

# Internal logging level
logger = logging.getLogger('crystal_balls')
logger.setLevel(level=logging.DEBUG)

SLOTS_CONFIGURATION = "config/slots.json"


def validate_storage_size(arg_value: str) -> str:
    """
    Defines and checks valid storage inputs.

    Args:
        arg_value: The given storage input string

    Returns:
        The valid storage string or raises an exception if it doesn't match the regex.
    """

    pat = re.compile(r"^[0-9]+([kKmMgGtTpP]i?[bB]?)$")

    if not pat.match(arg_value):
        logger.error(f'Invalid storage value given: {arg_value}')
        raise argparse.ArgumentTypeError
    return arg_value


def validate_duration(arg_value: str) -> str:
    """
    Defines and checks valid time inputs.

    Args:
        arg_value: The given duration input string

    Returns:
        The valid duration string or raises an exception if it doesn't match the regex.
    """
    pat = re.compile(r"^([0-9]+([dDhHmMsS]?))?$")

    if not pat.match(arg_value):
        logger.error(f'Invalid time value given: {arg_value}')
        raise argparse.ArgumentTypeError
    return arg_value


def split_number_unit(user_input: str) -> [float, str]:
    """
    Splits the user input for storage sizes into number and storage unit.
    If no value or unit is given, the unit is set to GiB.

    Args:
        user_input: The given number string

    Returns:
        The amount and unit string separated in a list.
    """
    if not user_input:
        return [0.0, "GiB"]

    splitted = re.split(r'(\d*\.?\d+)', user_input.replace(' ', ''))

    amount = float(splitted[1])
    if splitted[2] == "":
        unit = "GiB"
        logger.info("No storage unit given, using GiB as default.")
    else:
        unit = splitted[2]

    return [amount, unit]


def split_duration_unit(user_input: str) -> [float, str]:
    """
    Splits the user input for time into number and time unit.
    If no value or unit is given, the unit is set to minutes.

    Args:
        user_input: The given duration string

    Returns:
        The duration and unit string separated in a list.
    """
    if user_input == "" or user_input is None:
        return [0.0, "min"]

    splitted = re.split(r'(\d*\.?\d+)', user_input.replace(' ', ''))

    amount = float(splitted[1])
    if splitted[2] == "":
        unit = "min"
        logger.info("No duration unit given, using MIN as default.")
    else:
        unit = splitted[2]

    return [amount, unit]


def calc_to_bin(number: float, unit: str) -> float:
    """
    Converts a storage value to GiB and accounts for base2 and base10 units.

    Args:
        number: The storage size number
        unit: The storage unit string

    Returns:
        The storage size number converted to GiB
    """
    unit_indicator = unit.lower()
    if unit_indicator in ("kb", "k", "kib"):
        return number / (10 ** 6)
    if unit_indicator in ("mb", "m", "mib"):
        return number / (10 ** 3)
    if unit_indicator in ("tb", "t", "tib"):
        return number * (10 ** 3)
    if unit_indicator in ("pb", "p", "pib"):
        return number * (10 ** 6)
    return number


def calc_to_min(number: float, unit: str) -> float:
    """
    Converts a time value to minutes, according to the given unit.

    Args:
        number: The duration number
        unit: The duration unit string

    Returns:
        The duration number converted to minutes
    """
    unit_indicator = unit.lower()
    if unit_indicator in ("d", "dd"):
        return number * 24 * 60
    if unit_indicator in ("h", "hh"):
        return number * 60
    if unit_indicator in ("s", "ss"):
        return number / 60
    return number


def define_environment():
    """
    Defines the command line arguments and required formats.

    Returns:

    """
    parser = argparse.ArgumentParser(
        description="To get a preview for any job you are trying to execute using "
                    "HTCondor, please pass at least the number of CPUs and "
                    "the amount of RAM "
                    "(including units eg. 100MB, 90M, 10GB, 15G) to this script "
                    "according to the usage example shown above. For JOB Duration please "
                    "use d, h, m or s", prog='htcrystalball.py',
        usage='%(prog)s -c CPU -r RAM [-g GPU] [-d DISK] [-j JOBS] [-d DURATION] [-v]',
        epilog="PLEASE NOTE: HTCondor always uses binary storage "
               "sizes (1 GiB = 1024 MiB, 1 GB = 1000 MB), so inputs "
               "will automatically be treated that way.")
    parser.add_argument("-v", "--verbose", help="Print extended log to stdout",
                        action='store_true')
    parser.add_argument("-c", "--cpu", help="Set number of requested CPU Cores",
                        type=int, required=True)
    parser.add_argument("-g", "--gpu", help="Set number of requested GPU Units",
                        type=int)
    parser.add_argument("-j", "--jobs", help="Set number of jobs to be executed",
                        type=int)
    parser.add_argument("-t", "--time", help="Set the duration for one job "
                                             "to be executed", type=validate_duration)
    parser.add_argument("-d", "--disk", help="Set amount of requested disk "
                                             "storage", type=validate_storage_size)
    parser.add_argument("-r", "--ram", help="Set amount of requested memory "
                                            "storage", type=validate_storage_size, required=True)
    parser.add_argument("-m", "--maxnodes", help="Set maximum of nodes to "
                                                 "run jobs on", type=int)

    cmd_parser = parser.parse_args()
    return cmd_parser


def define_slots() -> dict:
    """
    Loads the slot configuration.

    Returns:

    """
    with open(SLOTS_CONFIGURATION) as config_file:
        data = json.load(config_file)
    return data["slots"]


def filter_slots(slots: dict, slot_type: str) -> list:
    """
    Filters the slots stored in a dictionary according to their type.

    Args:
        slots: Dictionary of slots
        slot_type: requested Slot Type for filtering

    Returns:
        A filtered dictionary of slots
    """
    res = []
    for node in slots:
        for slot in node["slot_size"]:
            if slot["SlotType"] == slot_type:
                slot["UtsnameNodename"] = node["UtsnameNodename"]
                res.append(slot)
    return res


def prepare_checking(cpu: int, gpu: int, ram: str, disk: str,
                     jobs: int, job_duration: str, maxnodes: int, verbose: bool) -> bool:
    """
    Loads the Slot configuration, handles storage and time inputs,
    and invokes the checking for given job request if the request is valid.

    Args:
        cpu: User input of CPU cores
        gpu: User input of GPU units
        ram: User input of the amount of RAM
        disk: User input of the amount of disk space
        jobs: User input of the number of similar jobs
        job_duration: User input of the duration time for a single job
        maxnodes:
        verbose:

    Returns:
        If all needed parameters were given
    """

    slot_config = define_slots()
    static_slts = filter_slots(slot_config, "static")
    dynamic_slts = filter_slots(slot_config, "dynamic")
    gpu_slts = filter_slots(slot_config, "gpu")

    [ram, ram_unit] = split_number_unit(ram)
    ram = calc_to_bin(ram, ram_unit)
    [disk, disk_unit] = split_number_unit(disk)
    disk = calc_to_bin(disk, disk_unit)

    [job_duration, duration_unit] = split_duration_unit(job_duration)
    job_duration = calc_to_min(job_duration, duration_unit)

    if cpu == 0:
        logger.warning("No number of CPU workers given --- ABORTING")
    elif ram == 0.0:
        logger.warning("No RAM amount given --- ABORTING")
    else:
        slot_checker.check_slots(static_slts, dynamic_slts, gpu_slts, cpu, ram, disk, gpu,
                                 jobs, job_duration, maxnodes, verbose)
        return True

    return False


if __name__ == "__main__":
    cmd_args = define_environment()
    cpu_workers = cmd_args.cpu
    if cpu_workers is None:
        cpu_workers = 0
    gpu_workers = cmd_args.gpu
    if gpu_workers is None:
        gpu_workers = 0

    ram_amount = cmd_args.ram
    disk_space = cmd_args.disk

    job_amount = cmd_args.jobs
    if job_amount is None:
        job_amount = 1
    job_duration = cmd_args.time

    matlab_nodes = cmd_args.maxnodes
    if matlab_nodes is None:
        matlab_nodes = 0

    # fetch current slot configuration
    sloth.run()

    prepare_checking(cpu_workers, gpu_workers, ram_amount, disk_space,
                     job_amount, job_duration, matlab_nodes, cmd_args.verbose)
