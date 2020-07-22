#!/usr/bin/env python3
"""
Gives users a preview on how and where they can execute their HTcondor compatible scripts
"""
import argparse
import json
import re
import math
from rich.console import Console
from rich.table import Table


def validate_storage_size(arg_value, pat=re.compile(r"^[0-9]+([kKmMgGtTpP]i?[bB]?)$")):
    """
    Defines and checks for valid storage inputs.
    :param arg_value:
    :param pat:
    :return:
    """
    if not pat.match(arg_value):
        print("ERROR: Invalid storage value given: '"+arg_value+"'\n")
        raise argparse.ArgumentTypeError
    return arg_value


def validate_duration(arg_value, pat=re.compile(r"^([0-9]+([dDhHmMsS]?))?$")):
    """
    Defines and checks for valid time inputs.
    :param arg_value:
    :param pat:
    :return:
    """
    if not pat.match(arg_value):
        print("ERROR: Invalid time value given: '"+arg_value+"'\n")
        raise argparse.ArgumentTypeError
    return arg_value


def split_number_unit(user_input: str) -> [float, str]:
    """
    Splits the user input for storage sizes into number and storage unit.
    If no value or unit is given, the unit is set to GiB.
    :param user_input:
    :return:
    """
    if user_input == "" or user_input is None:
        return [0.0, "GiB"]

    string_index = 0
    while user_input[:string_index + 1].isnumeric() and string_index < len(user_input):
        string_index += 1

    amount = float(user_input[:string_index])
    unit = "GiB" if user_input[string_index:] == "" else user_input[string_index:]

    return [amount, unit]


def split_duration_unit(user_input: str) -> [float, str]:
    """
    Splits the user input for time into number and time unit.
    If no value or unit is given, the unit is set to minutes.
    :param user_input:
    :return:
    """
    if user_input == "" or user_input is None:
        return [0.0, "min"]

    string_index = 0
    while user_input[:string_index + 1].isnumeric() and string_index < len(user_input):
        string_index += 1

    amount = float(user_input[:string_index])
    unit = "min" if user_input[string_index:] == "" else user_input[string_index:]

    return [amount, unit]


def calc_to_bin(number: float, unit: str) -> float:
    """
    Converts a storage value to GiB and accounts for base2 and base10 units.
    :param number:
    :param unit:
    :return:
    """
    unit_indicator = unit.lower()
    if unit_indicator in ("kb", "k", "kib"):
        number = number / (10 ** 6)
    elif unit_indicator in ("mb", "m", "mib"):
        number = number / (10 ** 3)
    elif unit_indicator in ("tb", "t", "tib"):
        number = number * (10 ** 3)
    elif unit_indicator in ("pb", "p", "pib"):
        number = number * (10 ** 6)
    return number


def calc_to_min(number: float, unit: str) -> float:
    """
    Converts a time value to minutes, according to the given unit.
    :param number:
    :param unit:
    :return:
    """
    unit_indicator = unit.lower()
    if unit_indicator in ("d", "dd"):
        number = number * 24 * 60
    elif unit_indicator in ("h", "hh"):
        number = number * 60
    elif unit_indicator in ("s", "ss"):
        number = number / 60
    return number


# fixed help output non-optional without brackets and usage not showing -h
def define_environment():
    """
    Defines the command line arguments and required formats.
    :return:
    """
    parser = argparse.ArgumentParser(
        description="To get a preview for any job you are trying to execute using "
                    "HTCondor, please pass at least the number of CPUs and "
                    "either the amount of RAM or diskspace "
                    "(including units eg. 100MB, 90MiB, 10GB, 15GiB) to this script "
                    "according to the usage example shown above. For JOB Duration please "
                    "use d, h, m or s", prog='htcrystalball.py',
        usage='%(prog)s -c CPU -r RAM [-g GPU] [-d DISK] [-j JOBS] [-d DURATION] [-v]',
        epilog="PLEASE NOTE: HTCondor always uses binary storage "
               "sizes, so 10GB will be converted to 9.31 GiB.")
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
    Loads the slot configuration. TODO: Add filters for slot types
    :return:
    """
    with open('config/slots.json') as config_file:
        data = json.load(config_file)
    return data["slots"]


def filter_slots(slots: dict, slot_type: str) -> list:
    """
    Filter the slots stored in a dictionary according to their type
    :param slots:
    :param slot_type:
    :return:
    """
    res = []
    for node in slots:
        for slot in node["slot_size"]:
            if slot["type"] == slot_type:
                slot["node"] = node["node"]
                res.append(slot)
    return res


#  print out what the user gave as input
def pretty_print_input(num_cpu: int, amount_ram: float, amount_disk: float, num_gpu: int,
                       num_jobs: int, num_duration: float, max_nodes: int):
    """
    Prints out the already converted user input to the console using rich tables.
    :param num_cpu:
    :param amount_ram:
    :param amount_disk:
    :param num_gpu:
    :param num_jobs:
    :param num_duration:
    :param max_nodes:
    :return:
    """
    console = Console()

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Parameter", style="dim")
    table.add_column("Input Value", justify="right")
    table.add_row(
        "CPUS",
        str(num_cpu)
    )
    table.add_row(
        "RAM",
        "{0:.2f}".format(amount_ram) + " GiB"
    )
    table.add_row(
        "STORAGE",
        "{0:.2f}".format(amount_disk) + " GiB"
    )
    table.add_row(
        "GPUS",
        str(num_gpu)
    )
    table.add_row(
        "JOBS",
        str(num_jobs)
    )
    table.add_row(
        "JOB DURATION",
        "{0:.2f}".format(num_duration) + " min"
    )
    table.add_row(
        "MAXIMUM NODES",
        str(max_nodes)
    )
    console.print("---------------------- INPUT ----------------------")
    console.print(table)


def pretty_print_nodes(result: dict):
    """
    Prints out the nodes to the console using rich tables.
    :param result:
    :return:
    """
    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Node", style="dim", width=12)
    table.add_column("Slot Type")
    table.add_column("Total Cores/Slots", justify="right")
    table.add_column("Total RAM", justify="right")
    table.add_column("Slot Cores", justify="right")
    table.add_column("Slot GPUs", justify="right")
    table.add_column("Slot RAM", justify="right")
    table.add_column("Cores/Slots free", justify="right")
    table.add_column("RAM free", justify="right")

    for node in result['nodes']:
        if node['type'] == "static":
            table.add_row("[dark_blue]" + node['name'] + "[/dark_blue]",
                          "[dark_blue]" + node['type'] + "[/dark_blue]",
                          "[dark_blue]" + str(node['workers']) + "[/dark_blue]",
                          "[dark_blue]" + str(node['ram']) + " GiB[/dark_blue]",
                          "[dark_blue]" + str(node['slot_cores']) + "[/dark_blue]",
                          "[dark_blue]" + str(node['slot_gpus']) + "[/dark_blue]",
                          "[dark_blue]" + str(node['slot_ram']) + " GiB[/dark_blue]",
                          "[dark_blue]" + str(node['slot_free']) + "[/dark_blue]",
                          "[dark_blue]" + str(node['ram_free']) + " GiB[/dark_blue]")
        elif node['type'] == "gpu/static":
            table.add_row("[purple4]" + node['name'] + "[/purple4]",
                          "[purple4]" + node['type'] + "[/purple4]",
                          "[purple4]" + str(node['workers']) + "[/purple4]",
                          "[purple4]" + str(node['ram']) + " GiB[/purple4]",
                          "[purple4]" + str(node['slot_cores']) + "[/purple4]",
                          "[purple4]" + str(node['slot_gpus']) + "[/purple4]",
                          "[purple4]" + str(node['slot_ram']) + " GiB[/purple4]",
                          "[purple4]" + str(node['slot_free']) + "[/purple4]",
                          "[purple4]" + str(node['ram_free']) + " GiB[/purple4]")
        else:
            table.add_row("[dark_red]" + node['name'] + "[/dark_red]",
                          "[dark_red]" + node['type'] + "[/dark_red]",
                          "[dark_red]" + str(node['workers']) + "[/dark_red]",
                          "[dark_red]" + str(node['ram']) + " GiB[/dark_red]",
                          "[dark_red]------[/dark_red]",
                          "[dark_red]------[/dark_red]",
                          "[dark_red]------[/dark_red]",
                          "[dark_red]" + str(node['slot_free']) + "[/dark_red]",
                          "[dark_red]" + str(node['ram_free']) + " GiB[/dark_red]")

    console.print("---------------------- NODES ----------------------")
    console.print(table)


def pretty_print_slots(result: dict, verbose: bool):
    """
    Prints out the preview result to the console using rich tables.
    :param result:
    :param verbose:
    :return:
    """
    console = Console()

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Node", style="dim", width=12)
    table.add_column("Slot Type")
    table.add_column("Job fits", justify="right")
    if verbose:
        table.add_column("Slot usage", justify="right")
        table.add_column("RAM usage", justify="center")
    table.add_column("Amount of similar jobs", justify="right")
    table.add_column("Wall Time on IDLE", justify="right")

    for node in result['preview']:
        if node['fits'] == "YES":
            if verbose:
                table.add_row("[green]" + node['name'] + "[/green]",
                              "[green]" + node['type'] + "[/green]",
                              "[green]" + node['fits'] + "[/green]",
                              "[green]" + node['core_usage'] + " Cores[/green]",
                              "[green]" + node['ram_usage'] + "[/green]",
                              "[green]" + str(node['sim_jobs']) + "[/green]",
                              "[green]" + str(node['wall_time_on_idle']) + " min[/green]")
            else:
                table.add_row("[green]" + node['name'] + "[/green]",
                              "[green]" + node['type'] + "[/green]",
                              "[green]" + node['fits'] + "[/green]",
                              "[green]" + str(node['sim_jobs']) + "[/green]",
                              "[green]" + str(node['wall_time_on_idle']) + " min[/green]")
        else:
            if verbose:
                table.add_row("[red]" + node['name'] + "[/red]",
                              "[red]" + node['type'] + "[/red]",
                              "[red]" + node['fits'] + "[/red]",
                              "[red]" + node['core_usage'] + " Cores[/red]",
                              "[red]" + node['ram_usage'] + "[/red]",
                              "[red]" + str(node['sim_jobs']) + "[/red]",
                              "[red]" + str(node['wall_time_on_idle']) + " min[/red]")
            else:
                table.add_row("[red]" + node['name'] + "[/red]",
                              "[red]" + node['type'] + "[/red]",
                              "[red]" + node['fits'] + "[/red]",
                              "[red]" + str(node['sim_jobs']) + "[/red]",
                              "[red]" + str(node['wall_time_on_idle']) + " min[/red]")

    console.print("---------------------- PREVIEW ----------------------")
    console.print(table)


def check_slots(static: list, dynamic: list, gpu: list, num_cpu: int,
                amount_ram: float, amount_disk: float, num_gpu: int,
                num_jobs: int, job_duration: float, maxnodes: int, verbose: bool) -> dict:
    """
    Handles the checking for all node/slot types and invokes the output methods.

    :param static:
    :param dynamic:
    :param gpu:
    :param num_cpu:
    :param amount_ram:
    :param amount_disk:
    :param num_gpu:
    :param num_jobs:
    :param job_duration:
    :param maxnodes:
    :param verbose:
    :return:
    """
    if verbose:
        pretty_print_input(num_cpu, amount_ram, amount_disk, num_gpu, num_jobs, job_duration, maxnodes)

    preview_res = {'nodes': [], 'preview': []}

    if num_cpu != 0 and num_gpu == 0:
        for node in dynamic:
            [node_dict, preview_node] = check_dynamic_slots(node, num_cpu,
                                                            amount_ram, job_duration, num_jobs)
            preview_res['nodes'].append(node_dict)
            preview_res['preview'].append(preview_node)

        for node in static:
            [node_dict, preview_node] = check_static_slots(node, "static", num_cpu,
                                                           amount_ram, job_duration, num_jobs)
            preview_res['nodes'].append(node_dict)
            preview_res['preview'].append(preview_node)
    elif num_cpu != 0 and num_gpu != 0:
        for node in gpu:
            [node_dict, preview_node] = check_gpu_slots(node, "gpu/static", num_cpu, num_gpu,
                                                        amount_ram, job_duration, num_jobs)
            preview_res['nodes'].append(node_dict)
            preview_res['preview'].append(preview_node)
    else:
        return {}

    preview_res['preview'] = order_node_preview(preview_res['preview'])
    if maxnodes != 0 and len(preview_res['preview']) > maxnodes:
        preview_res['preview'] = preview_res['preview'][:maxnodes]

    if verbose:
        pretty_print_nodes(preview_res)
    pretty_print_slots(preview_res, verbose)

    return preview_res


def check_dynamic_slots(node: dict, num_cpu: int, amount_ram: float,
                        job_duration: float, num_jobs: int) -> [dict, dict]:
    """
    Checks all dynamic slots if they fit the job.
    :param node:
    :param num_cpu:
    :param amount_ram:
    :param job_duration:
    :param num_jobs:
    :return:
    """
    available_cores = node["total_slots"] - node["slots_in_use"]
    available_ram = node["total_ram"] - node["ram_in_use"]
    node_dict = {'name': node["node"],
                 'type': 'dynamic',
                 'workers': str(node["total_slots"]),
                 'ram': str(node["total_ram"]),
                 'slot_free': str(available_cores),
                 'ram_free': str(available_ram)}

    # if the job fits, calculate and return the usage
    preview_node = {'name': node["node"],
                    'type': "dynamic",
                    'fits': 'NO',
                    'core_usage': '------',
                    'gpu_usage': '------',
                    'ram_usage': '------',
                    'sim_jobs': '------',
                    'wall_time_on_idle': 0}
    if num_cpu <= available_cores and amount_ram <= available_ram:
        preview_node['core_usage'] = str(num_cpu) + "/" + \
                                     str(node["total_slots"]) + " (" + \
                                     str(int(round((num_cpu / node["total_slots"]) * 100))) \
                                     + "%)"
        preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + \
                                    str(node["total_ram"]) + " GiB (" + \
                                    str(int(round((amount_ram / node["total_ram"]) * 100))) \
                                    + "%)"
        preview_node['fits'] = 'YES'
        preview_node['sim_jobs'] = int(available_cores / num_cpu)
    else:
        preview_node['core_usage'] = str(num_cpu) + "/" + \
                                     str(node["total_slots"]) + " (" + str(
                                         int(round((num_cpu / node["total_slots"])
                                                   * 100))) + "%)"
        preview_node['sim_jobs'] = 0
        preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(
            node["total_ram"]) + " GiB (" \
            + str(int(round((amount_ram / node["total_ram"]) * 100))) + "%)"
        preview_node['fits'] = 'NO'

    if num_cpu <= node["total_slots"] and job_duration != 0:
        cpu_fits = int(node["total_slots"] / num_cpu)
        jobs_parallel = cpu_fits \
            if amount_ram == 0 \
            else min(cpu_fits, int(node["total_ram"] / amount_ram))
        preview_node['wall_time_on_idle'] = str(math.ceil(num_jobs /
                                                          jobs_parallel) * job_duration)
    return [node_dict, preview_node]


def check_static_slots(node: dict, slot_type: str, num_cores: int, amount_ram: float,
                       job_duration: float, num_jobs: int) -> [dict, dict]:
    """
    Checks all static slots (gpu is also static) if the job fits
    :param node:
    :param slot_type:
    :param num_cores:
    :param amount_ram:
    :param job_duration:
    :param num_jobs:
    :return:
    """
    available_slots = node["total_slots"] - node["slots_in_use"]
    available_ram = node["total_ram"] - node["ram_in_use"]
    slot_size = node["slot_size"]
    node_dict = {'name': node["node"],
                 'type': slot_type,
                 'workers': str(node["total_slots"]),
                 'ram': str(node["total_ram"]),
                 'slot_cores': str(slot_size["cores"]),
                 'slot_gpus': "------",
                 'slot_ram': str(slot_size["ram_amount"]),
                 'slot_free': str(available_slots),
                 'ram_free': str(available_ram)}

    # if the job fits, calculate and return the usage
    preview_node = {'name': node["node"],
                    'type': slot_type,
                    'fits': 'NO',
                    'core_usage': '------',
                    'gpu_usage': '------',
                    'ram_usage': '------',
                    'sim_jobs': '------',
                    'wall_time_on_idle': 0}
    if num_cores <= slot_size["cores"] and amount_ram <= slot_size["ram_amount"]:
        preview_node['core_usage'] = str(num_cores) + "/" + \
                                     str(slot_size["cores"]) + " (" + str(
                                         int(round((num_cores / slot_size["cores"])
                                                   * 100))) + "%)"
        preview_node['sim_jobs'] = available_slots
        preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(
            slot_size["ram_amount"]) + " GiB (" \
            + str(int(round((amount_ram / slot_size["ram_amount"]) * 100))) + "%)"
        preview_node['fits'] = 'YES'
        if job_duration != 0:
            cpu_fits = int(slot_size["cores"] / num_cores)
            jobs_on_idle_slot = cpu_fits \
                if amount_ram == 0 \
                else min(cpu_fits, int(slot_size["ram_amount"] / amount_ram))
            preview_node['wall_time_on_idle'] = str(
                math.ceil(num_jobs / jobs_on_idle_slot / node["total_slots"]) *
                job_duration)
    else:
        preview_node['core_usage'] = str(num_cores) + "/" + \
                                     str(slot_size["cores"]) + " (" + str(
                                         int(round((num_cores / slot_size["cores"])
                                                   * 100))) + "%)"
        preview_node['sim_jobs'] = 0
        preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(
            slot_size["ram_amount"]) + " GiB (" \
            + str(int(round((amount_ram / slot_size["ram_amount"]) * 100))) + "%)"
        preview_node['fits'] = 'NO'
    return [node_dict, preview_node]


def check_gpu_slots(node: dict, slot_type: str, num_cores: int, num_gpu: int, amount_ram: float,
                    job_duration: float, num_jobs: int) -> [dict, dict]:
    """
    Checks all static slots (gpu is also static) if the job fits
    :param num_gpu:
    :param node:
    :param slot_type:
    :param num_cores:
    :param amount_ram:
    :param job_duration:
    :param num_jobs:
    :return:
    """
    available_slots = node["total_slots"] - node["slots_in_use"]
    available_ram = node["total_ram"] - node["ram_in_use"]
    slot_size = node["slot_size"]
    node_dict = {'name': node["node"],
                 'type': slot_type,
                 'workers': str(node["total_slots"]),
                 'ram': str(node["total_ram"]),
                 'slot_cores': str(slot_size["cores"]),
                 'slot_gpus': str(slot_size["gpus"]),
                 'slot_ram': str(slot_size["ram_amount"]),
                 'slot_free': str(available_slots),
                 'ram_free': str(available_ram)}

    # if the job fits, calculate and return the usage
    preview_node = {'name': node["node"],
                    'type': slot_type,
                    'fits': 'NO',
                    'gpu_usage': '------',
                    'core_usage': '------',
                    'ram_usage': '------',
                    'sim_jobs': '------',
                    'wall_time_on_idle': 0}
    if num_cores <= slot_size["cores"] and amount_ram <= slot_size["ram_amount"] \
            and num_gpu <= slot_size["gpus"]:
        preview_node['core_usage'] = str(num_cores) + "/" + \
                                     str(slot_size["cores"]) + " (" + str(
                                         int(round((num_cores / slot_size["cores"])
                                                   * 100))) + "%)"
        preview_node['gpu_usage'] = str(num_gpu) + "/" + \
            str(slot_size["gpus"]) + " (" + str(
            int(round((num_gpu / slot_size["gpus"])
                      * 100))) + "%)"
        preview_node['sim_jobs'] = min(available_slots, slot_size["gpus"])
        preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(
            slot_size["ram_amount"]) + " GiB (" \
            + str(int(round((amount_ram / slot_size["ram_amount"]) * 100))) + "%)"
        preview_node['fits'] = 'YES'
        if job_duration != 0:
            cpu_fits = int(slot_size["cores"] / num_cores)
            gpu_fits = int(slot_size["gpus"] / num_gpu)
            jobs_on_idle_slot = min(cpu_fits, gpu_fits) \
                if amount_ram == 0 \
                else min(min(cpu_fits, gpu_fits), int(slot_size["ram_amount"] / amount_ram))
            preview_node['wall_time_on_idle'] = str(
                math.ceil(num_jobs / jobs_on_idle_slot / slot_size["gpus"]) *
                job_duration)
    else:
        preview_node['core_usage'] = str(num_cores) + "/" + \
                                     str(slot_size["cores"]) + " (" + str(
                                         int(round((num_cores / slot_size["cores"])
                                                   * 100))) + "%)"
        preview_node['gpu_usage'] = str(num_gpu) + "/" + \
            str(slot_size["gpus"]) + " (" + str(
            int(round((num_gpu / slot_size["gpus"])
                      * 100))) + "%)"
        preview_node['sim_jobs'] = 0
        preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(
            slot_size["ram_amount"]) + " GiB (" \
            + str(int(round((amount_ram / slot_size["ram_amount"]) * 100))) + "%)"
        preview_node['fits'] = 'NO'
    return [node_dict, preview_node]


def order_node_preview(node_preview: list) -> list:
    """
    Order the list of checked nodes by fits/fits not and number of similar jobs descending.
    :param node_preview:
    :return:
    """
    return sorted(node_preview, key=lambda nodes: (nodes["sim_jobs"]), reverse=True)


def prepare_checking(arg_values, cpu: int, gpu: int, ram: str, disk: str,
                     jobs: int, job_duration: str, maxnodes: int, verbose: bool) -> bool:
    """
    Loads the Slot configuration, handles storage and time inputs,
    and invokes the checking for given job request if the request is valid.
    :param arg_values:
    :param cpu:
    :param gpu:
    :param ram:
    :param disk:
    :param jobs:
    :param job_duration:
    :param maxnodes:
    :param verbose:
    :return:
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

    if arg_values is not None and verbose:
        print("verbosity turned on")
    if cpu == 0:
        print("No number of CPU workers given --- ABORTING")
    elif ram == 0.0:
        print("No RAM amount given --- ABORTING")
    else:
        check_slots(static_slts, dynamic_slts, gpu_slts, cpu, ram, disk, gpu,
                    jobs, job_duration, maxnodes, verbose)
        return True

    return False


if __name__ == "__main__":
    CMD_ARGS = define_environment()
    CPU_WORKERS = CMD_ARGS.cpu
    if CPU_WORKERS is None:
        CPU_WORKERS = 0
    GPU_WORKERS = CMD_ARGS.gpu
    if GPU_WORKERS is None:
        GPU_WORKERS = 0

    RAM_AMOUNT = CMD_ARGS.ram
    DISK_SPACE = CMD_ARGS.disk

    JOB_AMOUNT = CMD_ARGS.jobs
    if JOB_AMOUNT is None:
        JOB_AMOUNT = 1
    JOB_DURATION = CMD_ARGS.time

    MATLAB_NODES = CMD_ARGS.maxnodes
    if MATLAB_NODES is None:
        MATLAB_NODES = 0
    prepare_checking(CMD_ARGS, CPU_WORKERS, GPU_WORKERS, RAM_AMOUNT, DISK_SPACE,
                     JOB_AMOUNT, JOB_DURATION, MATLAB_NODES, CMD_ARGS.verbose)
