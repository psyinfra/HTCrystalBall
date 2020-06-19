#!/usr/bin/env python3

import argparse
import re
from rich.console import Console
from rich.table import Column, Table


# define Add K(B), M(B), G(B), T(B) as units for Disk and RAM
def storage_size(arg_value, pat=re.compile(r"^[0-9]+([kKmMgGtT]i?[bB]?)?$")):
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError
    return arg_value


def split_number_unit(user_input):
    if user_input == "":
        return 0, "GiB"

    string_index = 0
    while user_input[:string_index + 1].isnumeric():
        string_index += 1

    amount = int(user_input[:string_index])
    unit = "GiB" if user_input[string_index:] == "" else user_input[string_index:]

    return amount, unit


# Account for base2 units, not base10, converts everything to Gibibytes
def calc_to_bin(number, unit):
    unit_indicator = unit.lower()
    if unit_indicator == "kb" or unit_indicator == "k":
        return number * (10 ** 3) / (2 ** 30)
    elif unit_indicator == "kib":
        return number / (2 ** 20)
    elif unit_indicator == "mb" or unit_indicator == "m":
        return number * (10 ** 6) / (2 ** 30)
    elif unit_indicator == "mib":
        return number / (2 ** 10)
    elif unit_indicator == "gb" or unit_indicator == "g":
        return number * (10 ** 9) / (2 ** 30)
    elif unit_indicator == "tb" or unit_indicator == "t":
        return number * (10 ** 12) / (2 ** 30)
    elif unit_indicator == "tib":
        return number * (2 ** 10)
    # assume it's already GiB
    else:
        return number


def define_environment():
    parser = argparse.ArgumentParser(description="To get a preview for any job you are trying to execute using "
                                                 "HTCondor, please pass at least either the number of CPUs or GPUs and "
                                                 "either the amount of RAM or diskspace to this script according to "
                                                 "the usage example shown above.")
    parser.add_argument("-v", "--verbose", help="Print extended log to stdout", action='store_true')
    parser.add_argument("-c", "--cpu", help="Set number of requested CPU Cores", type=int)
    parser.add_argument("-g", "--gpu", help="Set number of requested GPU Units", type=int)
    parser.add_argument("-d", "--disk", help="Set amount of requested disk storage in GB", type=storage_size)
    parser.add_argument("-r", "--ram", help="Set amount of requested memory storage in GB", type=storage_size)

    p = parser.parse_args()
    return p


# a collection of slots will be defined as a list of dictionarys for each different slot configuration
def define_slots():
    #  define all existing static slot configurations
    static_slots = [{"node": "cpu1", "total_slots": 32, "total_ram": 500, "slots_in_use": 0, "ram_in_use": 0,
                     "single_slot": {"cores": 1, "ram_amount": 15}}]

    #  define all existing partitionable configurations
    partitionable_slots = [{"node": "cpu2", "total_cores": 32, "total_ram": 500, "cores_blocked": 0, "ram_blocked": 0}]

    # TODO: fix help output non-optional without brackets and usage not showing -h
    gpu_slots = [{"node": "gpu1", "total_slots": 8, "total_ram": 500, "slots_in_use": 0, "ram_in_use": 0,
                  "single_slot": {"cores": 1, "ram_amount": 15}}]

    return static_slots, partitionable_slots, gpu_slots


def pretty_print_input(num_cpu, amount_ram, amount_disk, num_gpu):
    #  print out what the user gave as input
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
    console.print("---------------------- INPUT ----------------------")
    console.print(table)


# TODO: how to handle output for twenty nodes? Order by fits and then order by usage.
def pretty_print_slots(result):
    #  print out the nodes
    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Node", style="dim", width=12)
    table.add_column("Slot Type")
    table.add_column("Total Cores/Slots", justify="right")
    table.add_column("Total RAM", justify="right")
    table.add_column("Single Slot Cores", justify="right")
    table.add_column("Single Slot RAM", justify="right")
    table.add_column("Cores/Slots free", justify="right")
    table.add_column("RAM free", justify="right")

    for node in result['nodes']:
        if node['type'] == "static":
            table.add_row("[dark_blue]" + node['name'] + "[/dark_blue]",
                          "[dark_blue]" + node['type'] + "[/dark_blue]",
                          "[dark_blue]" + str(node['workers']) + "[/dark_blue]",
                          "[dark_blue]" + str(node['ram']) + "[/dark_blue]",
                          "[dark_blue]" + str(node['slot_cores']) + "[/dark_blue]",
                          "[dark_blue]" + str(node['slot_ram']) + "[/dark_blue]",
                          "[dark_blue]" + str(node['slot_free']) + "[/dark_blue]",
                          "[dark_blue]" + str(node['ram_free']) + "[/dark_blue]")
        elif node['type'] == "gpu/static":
            table.add_row("[purple4]" + node['name'] + "[/purple4]",
                          "[purple4]" + node['type'] + "[/purple4]",
                          "[purple4]" + str(node['workers']) + "[/purple4]",
                          "[purple4]" + str(node['ram']) + "[/purple4]",
                          "[purple4]" + str(node['slot_cores']) + "[/purple4]",
                          "[purple4]" + str(node['slot_ram']) + "[/purple4]",
                          "[purple4]" + str(node['slot_free']) + "[/purple4]",
                          "[purple4]" + str(node['ram_free']) + "[/purple4]")
        else:
            table.add_row("[dark_red]" + node['name'] + "[/dark_red]",
                          "[dark_red]" + node['type'] + "[/dark_red]",
                          "[dark_red]" + str(node['workers']) + "[/dark_red]",
                          "[dark_red]" + str(node['ram']) + "[/dark_red]",
                          "[dark_red]------[/dark_red]",
                          "[dark_red]------[/dark_red]",
                          "[dark_red]" + str(node['slot_free']) + "[/dark_red]",
                          "[dark_red]" + str(node['ram_free']) + "[/dark_red]")

    console.print("---------------------- NODES ----------------------")
    console.print(table)

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Node", style="dim", width=12)
    table.add_column("Slot Type")
    table.add_column("Job fits", justify="right")
    table.add_column("Core usage", justify="right")
    table.add_column("RAM usage", justify="center")
    table.add_column("Amount of similar jobs", justify="right")

    for node in result['preview']:
        if node['fits'] == "YES":
            table.add_row("[green]" + node['name'] + "[/green]",
                          "[green]" + node['type'] + "[/green]",
                          "[green]" + node['fits'] + "[/green]",
                          "[green]" + node['core_usage'] + "[/green]",
                          "[green]" + node['ram_usage'] + "[/green]",
                          "[green]" + str(node['sim_jobs']) + "[/green]")
        else:
            table.add_row("[red]" + node['name'] + "[/red]",
                          "[red]" + node['type'] + "[/red]",
                          "[red]" + node['fits'] + "[/red]",
                          "[red]" + node['core_usage'] + "[/red]",
                          "[red]" + node['ram_usage'] + "[/red]",
                          "[red]" + str(node['sim_jobs']) + "[/red]")

    console.print("---------------------- PREVIEW ----------------------")
    console.print(table)


def check_slots(static, dynamic, gpu, num_cpu=0, amount_ram=0, amount_disk=0, num_gpu=0):
    pretty_print_input(num_cpu, amount_ram, amount_disk, num_gpu)

    preview_res = {'nodes': [], 'preview': []}

    if num_cpu != 0:
        #  Check all DYNAMIC nodes
        for node in dynamic:
            available_cores = node["total_cores"] - node["cores_blocked"]
            available_ram = node["total_ram"] - node["ram_blocked"]
            node_dict = {'name': node["node"],
                         'type': 'dynamic',
                         'workers': str(node["total_cores"]),
                         'ram': str(node["total_ram"]) + " GiB",
                         'slot_free': str(available_cores),
                         'ram_free': str(available_ram) + " GiB"}
            preview_res['nodes'].append(node_dict)
            # if the job fits, calculate and return the usage
            preview_node = {'name': node["node"], 'type': 'dynamic', 'fits': 'NO',
                            'core_usage': '------', 'ram_usage': '------', 'sim_jobs': '------'}
            if num_cpu <= available_cores and amount_ram <= available_ram:
                preview_node['core_usage'] = str(num_cpu) + "/" + str(node["total_cores"]) + " (" + \
                    str(int(round((num_cpu / node["total_cores"]) * 100))) + "%)"
                preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(node["total_ram"]) + " GiB (" + \
                    str(int(round((amount_ram / node["total_ram"]) * 100))) + "%)"
                preview_node['fits'] = 'YES'
                preview_node['sim_jobs'] = str(int(available_cores / num_cpu))
            preview_res['preview'].append(preview_node)

        #  Check all STATIC nodes
        for node in static:
            available_slots = node["total_slots"] - node["slots_in_use"]
            single_slot = node["single_slot"]
            node_dict = {'name': node["node"], 'type': 'static',
                         'workers': str(node["total_slots"]),
                         'ram': str(node["total_ram"]) + " GiB",
                         'slot_cores': str(single_slot["cores"]),
                         'slot_ram': str(single_slot["ram_amount"]) + " GiB",
                         'slot_free': str(available_slots),
                         'ram_free': '---'}
            preview_res['nodes'].append(node_dict)
            # if the job fits, calculate and return the usage
            preview_node = {'name': node["node"],
                            'type': 'static',
                            'fits': 'NO',
                            'core_usage': '------',
                            'ram_usage': '------',
                            'sim_jobs': '------'}
            if num_cpu <= single_slot["cores"] and amount_ram <= single_slot["ram_amount"]:
                #  On STATIC nodes it's like ALL or NOTHING, when there are more than one CPUs requested
                preview_node['core_usage'] = str(num_cpu) + "/" + str(single_slot["cores"]) + " (" + str(
                    int(round((num_cpu / single_slot["cores"]) * 100)) if num_cpu == 1 else 0) + "%)"
                preview_node['sim_jobs'] = str(available_slots if num_cpu == 1 else 0)
                preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(
                    single_slot["ram_amount"]) + " GiB (" \
                    + str(int(round((amount_ram / single_slot["ram_amount"]) * 100)) if num_cpu == 1 else 0) + "%)"
                preview_node['fits'] = 'YES'
            preview_res['preview'].append(preview_node)
    elif num_gpu != 0:
        #  Check all GPU nodes
        for node in gpu:
            available_slots = node["total_slots"] - node["slots_in_use"]
            available_ram = node["total_ram"] - node["ram_in_use"]
            single_slot = node["single_slot"]
            node_dict = {'name': node["node"], 'type': 'gpu/static',
                         'workers': str(node["total_slots"]),
                         'ram': str(node["total_ram"]) + " GiB",
                         'slot_cores': str(single_slot["cores"]),
                         'slot_ram': str(single_slot["ram_amount"]) + " GiB",
                         'slot_free': str(available_slots),
                         'ram_free': str(available_ram) + " GiB"}
            preview_res['nodes'].append(node_dict)
            # if the job fits, calculate and return the usage
            preview_node = {'name': node["node"],
                            'type': 'gpu',
                            'fits': 'NO',
                            'core_usage': '------',
                            'ram_usage': '------',
                            'sim_jobs': '------'}
            if num_gpu <= single_slot["cores"] and amount_ram <= single_slot["ram_amount"]:
                #  On STATIC nodes it's like ALL or NOTHING, when there are more than one CPUs requested
                preview_node['core_usage'] = str(num_gpu) + "/" + str(single_slot["cores"]) + " (" + str(
                    int(round((num_gpu / single_slot["cores"]) * 100)) if num_gpu == 1 else 0) + "%)"
                preview_node['sim_jobs'] = str(available_slots if num_gpu == 1 else 0)
                preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(single_slot["ram_amount"]) + " GiB (" + str(
                    int(round((amount_ram / single_slot["ram_amount"]) * 100)) if num_gpu == 1 else 0) + "%)"
                preview_node['fits'] = 'YES'
            preview_res['preview'].append(preview_node)

    pretty_print_slots(preview_res)


def manage_calculation(cpu, gpu, ram, disk):
    ram, ram_unit = split_number_unit(ram)
    ram = calc_to_bin(ram, ram_unit)

    disk, disk_unit = split_number_unit(disk)
    disk = calc_to_bin(disk, disk_unit)

    if args.verbose:
        print("verbosity turned on")
    if cpu == 0:
        print("No number of CPU workers given --- ABORTING")
    elif ram == 0.0 and disk == 0.0:
        print("No RAM or DISK amount given --- ABORTING")
    else:
        check_slots(static_slots, dynamic_slots, gpu_slots, cpu, ram, disk, gpu)
        print("Check finished!")


# TODO: Add TESTING, account for different slot sizes on the same node
def run_tests():
    # single cpu, ram in GB
    cpu_test = 1
    ram_test = "10GB"
    gpu_test = 0
    disk_test = ""

    manage_calculation(cpu_test, gpu_test, ram_test, disk_test)


if __name__ == "__main__":
    static_slots, dynamic_slots, gpu_slots = define_slots()
    test = True
    args = define_environment()

    if test:
        run_tests()
    else:
        cpu_in = args.cpu
        if cpu_in is None:
            cpu_in = 0
        gpu_in = args.gpu
        if gpu_in is None:
            gpu_in = 0

        ram_in = args.ram
        disk_in = args.disk

        manage_calculation(cpu_in, gpu_in, ram_in, disk_in)
