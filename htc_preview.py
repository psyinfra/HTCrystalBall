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


class TestPreview:
    """
    Test class for use with pytest.
    """
    def test_storage_validator(self):
        """
        Tests the storage input validator.
        :return:
        """
        assert validate_storage_size("20GB") == "20GB"
        assert validate_storage_size("20") == "20"
        assert validate_storage_size("20iGB") == "20GiB"
        assert validate_storage_size("20GBt") == "20GB"
        assert validate_storage_size("20GB3") == "20GB"

    def test_time_validator(self):
        """
        Tests the time input validator.
        :return:
        """
        assert validate_storage_size("20min") == "20min"
        assert validate_storage_size("20") == "20"
        assert validate_storage_size("20imn") == "20min"
        assert validate_storage_size("20mint") == "20min"
        assert validate_storage_size("20hs") == "20min"

    def test_split_storage(self):
        """
        Tests the splitting method for storage inputs.
        :return:
        """
        number = 10
        unit = "GB"
        assert split_number_unit(str(number)) == [number, "GiB"]
        assert split_number_unit(str(number) + "GiB") == [number, "GiB"]
        assert split_number_unit("0" + unit) == "GiB"
        assert split_number_unit(str(number)) == number

    def test_split_time(self):
        """
        Tests the splitting method for the time input.
        :return:
        """
        number = 10
        unit = "min"
        assert split_duration_unit(str(number)) == [number, "min"]
        assert split_duration_unit(str(number) + "min") == [number, "min"]
        assert split_duration_unit("0" + unit) == "min"
        assert split_duration_unit(str(number)) == number

    def test_conversions(self):
        """
        Tests the number conversion methods for storage size and time.
        :return:
        """
        assert calc_to_bin(10.0, "GiB") == 10.0
        assert calc_to_bin(10.0, "GiB") == 10
        assert calc_to_bin(10.0, "GB") == 10.0
        assert calc_to_bin(10, "GiB") == 10.0
        assert calc_to_bin(10.0, "MiB") == 10.0

        assert calc_to_min(10.0, "h") == 10.0
        assert calc_to_min(10.0, "min") == 10
        assert calc_to_min(10.0, "min") == 10.0
        assert calc_to_min(10, "min") == 10.0
        assert calc_to_min(10.0, "s") == 10.0

    def test_calc_manager(self):
        """
        Tests the method for preparing the slot checking.
        :return:
        """
        assert prepare_checking(None, cpu=1, gpu=0, ram="10GB", disk="0", jobs=1,
                                job_duration="10m", maxnodes=0)
        assert prepare_checking(None, cpu=0, gpu=1, ram="10GB", disk="0", jobs=1,
                                job_duration="10m", maxnodes=0)
        assert prepare_checking(None, cpu=1, gpu=0, ram="0", disk="", jobs=1,
                                job_duration="", maxnodes=0)
        assert prepare_checking(None, cpu=1, gpu=1, ram="20GB", disk="", jobs=1,
                                job_duration="10m", maxnodes=0)
        assert prepare_checking(None, cpu=1, gpu=0, ram="10GB", disk="10GB",
                                jobs=1, job_duration="10m", maxnodes=0)
        assert prepare_checking(None, cpu=1, gpu=0, ram="10GB", disk="10GB",
                                jobs=128, job_duration="15m", maxnodes=0)
        assert prepare_checking(None, cpu=1, gpu=0, ram="10GB", disk="",
                                jobs=1, job_duration="10m", maxnodes=1)
        assert prepare_checking(None, cpu=8, gpu=0, ram="10GB", disk="",
                                jobs=1, job_duration="10m", maxnodes=0)
        assert prepare_checking(None, cpu=8, gpu=0, ram="80GB", disk="",
                                jobs=4, job_duration="1h", maxnodes=0)
        assert prepare_checking(None, cpu=2, gpu=0, ram="10GB", disk="",
                                jobs=1, job_duration="10m", maxnodes=3)
        assert prepare_checking(None, cpu=1, gpu=0, ram="20GB", disk="",
                                jobs=1, job_duration="10m", maxnodes=2)
        assert prepare_checking(None, cpu=2, gpu=0, ram="20GB", disk="",
                                jobs=1, job_duration="", maxnodes=2)
        assert prepare_checking(None, cpu=2, gpu=0, ram="20GB", disk="",
                                jobs=32, job_duration="10m", maxnodes=1)

    def test_slot_config(self):
        """
        Tests the slot loading method.
        :return:
        """
        slots = define_slots()
        assert "static" in slots
        assert "dynamic" in slots
        assert "gpu" in slots

    def test_slot_checking(self):
        """
        Tests the slot checking method.
        :return:
        """
        slots = define_slots()

        assert "preview" in check_slots(slots["static"], slots["dynamic"],
                                        slots["gpu"], 1, 10.0, 0.0, 0, 1, 0.0, 0)
        assert "nodes" in check_slots(slots["static"], slots["dynamic"],
                                      slots["gpu"], 1, 10.0, 0.0, 0, 1, 0.0, 0)
        assert "preview" in check_slots(slots["static"], slots["dynamic"],
                                        slots["gpu"], 0, 10.0, 0.0, 0, 1, 0.0, 0)
        assert "nodes" in check_slots(slots["static"], slots["dynamic"],
                                      slots["gpu"], 0, 10.0, 0.0, 0, 1, 0.0, 0)


def validate_storage_size(arg_value, pat=re.compile(r"^[0-9]+([kKmMgGtT]i?[bB]?)?$")):
    """
    Defines and checks for valid storage inputs.
    :param arg_value:
    :param pat:
    :return:
    """
    if not pat.match(arg_value):
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
    if unit_indicator in ("kb", "k"):
        number = number * (10 ** 3) / (2 ** 30)
    elif unit_indicator == "kib":
        number = number / (2 ** 20)
    elif unit_indicator in ("mb", "m"):
        number = number * (10 ** 6) / (2 ** 30)
    elif unit_indicator == "mib":
        number = number / (2 ** 10)
    elif unit_indicator in ("gb", "g"):
        number = number * (10 ** 9) / (2 ** 30)
    elif unit_indicator in ("tb", "t"):
        number = number * (10 ** 12) / (2 ** 30)
    elif unit_indicator == "tib":
        number = number * (2 ** 10)
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
                    "use d, h, m or s", prog='htc_preview.py',
        usage='%(prog)s -c CPU -r RAM [-g GPU] [-D DISK] [-j JOBS] [-d DURATION] [-v]',
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
    parser.add_argument("-d", "--duration", help="Set the duration for one job "
                                                 "to be executed", type=validate_duration)
    parser.add_argument("-D", "--Disk", help="Set amount of requested disk "
                                             "storage in GB", type=validate_storage_size)
    parser.add_argument("-r", "--ram", help="Set amount of requested memory "
                                            "storage in GB", type=validate_storage_size, required=True)
    parser.add_argument("-m", "--maxnodes", help="Set maximum of nodes to "
                                                 "run jobs on", type=int)

    cmd_parser = parser.parse_args()
    return cmd_parser


def define_slots() -> dict:
    """
    Loads the slot configuration.
    :return:
    """
    with open('config/slots.json') as config_file:
        data = json.load(config_file)
    return data


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
        "{0:.2f}".format(amount_ram) + " GiB (converted)"
    )
    table.add_row(
        "STORAGE",
        "{0:.2f}".format(amount_disk) + " GiB (converted)"
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
        "{0:.2f}".format(num_duration) + " min (converted)"
    )
    table.add_row(
        "MAXIMUM NODES",
        str(max_nodes)
    )
    console.print("---------------------- INPUT ----------------------")
    console.print(table)


def pretty_print_slots(result: dict):
    """
    Prints out the nodes and the preview result to the console using rich tables.
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
                          "[dark_blue]" + str(node['slot_ram']) + " GiB[/dark_blue]",
                          "[dark_blue]" + str(node['slot_free']) + "[/dark_blue]",
                          "[dark_blue]" + str(node['ram_free']) + " GiB[/dark_blue]")
        elif node['type'] == "gpu/static":
            table.add_row("[purple4]" + node['name'] + "[/purple4]",
                          "[purple4]" + node['type'] + "[/purple4]",
                          "[purple4]" + str(node['workers']) + "[/purple4]",
                          "[purple4]" + str(node['ram']) + " GiB[/purple4]",
                          "[purple4]" + str(node['slot_cores']) + "[/purple4]",
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
                          "[dark_red]" + str(node['slot_free']) + "[/dark_red]",
                          "[dark_red]" + str(node['ram_free']) + " GiB[/dark_red]")

    console.print("---------------------- NODES ----------------------")
    console.print(table)

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Node", style="dim", width=12)
    table.add_column("Slot Type")
    table.add_column("Job fits", justify="right")
    table.add_column("Slot usage", justify="right")
    table.add_column("RAM usage", justify="center")
    table.add_column("Amount of similar jobs", justify="right")
    table.add_column("Wall Time on IDLE", justify="right")

    for node in result['preview']:
        if node['fits'] == "YES":
            table.add_row("[green]" + node['name'] + "[/green]",
                          "[green]" + node['type'] + "[/green]",
                          "[green]" + node['fits'] + "[/green]",
                          "[green]" + node['core_usage'] + " Cores[/green]",
                          "[green]" + node['ram_usage'] + "[/green]",
                          "[green]" + str(node['sim_jobs']) + "[/green]",
                          "[green]" + str(node['wall_time_on_idle']) + " min[/green]")
        else:
            table.add_row("[red]" + node['name'] + "[/red]",
                          "[red]" + node['type'] + "[/red]",
                          "[red]" + node['fits'] + "[/red]",
                          "[red]" + node['core_usage'] + " Cores[/red]",
                          "[red]" + node['ram_usage'] + "[/red]",
                          "[red]" + str(node['sim_jobs']) + "[/red]",
                          "[red]" + str(node['wall_time_on_idle']) + " min[/red]")

    console.print("---------------------- PREVIEW ----------------------")
    console.print(table)


def check_slots(static: list, dynamic: list, gpu: list, num_cpu: int,
                amount_ram: float, amount_disk: float, num_gpu: int,
                num_jobs: int, job_duration: float, maxnodes: int) -> dict:
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
    :return:
    """
    pretty_print_input(num_cpu, amount_ram, amount_disk, num_gpu, num_jobs, job_duration, maxnodes)

    preview_res = {'nodes': [], 'preview': []}

    if num_cpu != 0 and num_gpu == 0:
        #  Check all DYNAMIC nodes
        for node in dynamic:
            available_cores = node["total_cores"] - node["cores_blocked"]
            available_ram = node["total_ram"] - node["ram_blocked"]
            node_dict = {'name': node["node"],
                         'type': 'dynamic',
                         'workers': str(node["total_cores"]),
                         'ram': str(node["total_ram"]),
                         'slot_free': str(available_cores),
                         'ram_free': str(available_ram)}
            preview_res['nodes'].append(node_dict)
            # if the job fits, calculate and return the usage
            preview_node = {'name': node["node"],
                            'type': 'dynamic',
                            'fits': 'NO',
                            'core_usage': '------',
                            'ram_usage': '------',
                            'sim_jobs': '------',
                            'wall_time_on_idle': 0}
            if num_cpu <= available_cores and amount_ram <= available_ram:
                preview_node['core_usage'] = str(num_cpu) + "/" + \
                                             str(node["total_cores"]) + " (" + \
                                             str(int(round((num_cpu / node["total_cores"]) * 100)))\
                                             + "%)"
                preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + \
                                            str(node["total_ram"]) + " GiB (" + \
                                            str(int(round((amount_ram / node["total_ram"]) * 100)))\
                                            + "%)"
                preview_node['fits'] = 'YES'
                preview_node['sim_jobs'] = int(available_cores / num_cpu)
            else:
                preview_node['core_usage'] = str(num_cpu) + "/" + \
                                             str(node["total_cores"]) + " (" + str(
                                                 int(round((num_cpu / node["total_cores"])
                                                           * 100))) + "%)"
                preview_node['sim_jobs'] = 0
                preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(
                    node["total_ram"]) + " GiB (" \
                    + str(int(round((amount_ram / node["total_ram"]) * 100))) + "%)"
                preview_node['fits'] = 'NO'

            if num_cpu <= node["total_cores"] and job_duration != 0:
                cpu_fits = int(node["total_cores"] / num_cpu)
                jobs_parallel = cpu_fits \
                    if amount_ram == 0 \
                    else min(cpu_fits, int(node["total_ram"] / amount_ram))
                preview_node['wall_time_on_idle'] = str(math.ceil(num_jobs /
                                                                  jobs_parallel) * job_duration)

            preview_res['preview'].append(preview_node)

        #  Check all STATIC nodes
        for node in static:
            available_slots = node["total_slots"] - node["slots_in_use"]
            slot_size = node["slot_size"]
            node_dict = {'name': node["node"], 'type': 'static',
                         'workers': str(node["total_slots"]),
                         'ram': str(node["total_ram"]),
                         'slot_cores': str(slot_size["cores"]),
                         'slot_ram': str(slot_size["ram_amount"]),
                         'slot_free': str(available_slots),
                         'ram_free': '---'}
            preview_res['nodes'].append(node_dict)
            # if the job fits, calculate and return the usage
            preview_node = {'name': node["node"],
                            'type': 'static',
                            'fits': 'NO',
                            'core_usage': '------',
                            'ram_usage': '------',
                            'sim_jobs': '------',
                            'wall_time_on_idle': 0}
            if num_cpu <= slot_size["cores"] and amount_ram <= slot_size["ram_amount"]:
                preview_node['core_usage'] = str(num_cpu) + "/" + \
                                             str(slot_size["cores"]) + " (" + str(
                                                 int(round((num_cpu / slot_size["cores"])
                                                           * 100))) + "%)"
                preview_node['sim_jobs'] = available_slots
                preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(
                    slot_size["ram_amount"]) + " GiB (" \
                    + str(int(round((amount_ram / slot_size["ram_amount"]) * 100))) + "%)"
                preview_node['fits'] = 'YES'
                if job_duration != 0:
                    cpu_fits = int(slot_size["cores"] / num_cpu)
                    jobs_on_idle_slot = cpu_fits \
                        if amount_ram == 0 \
                        else min(cpu_fits, int(slot_size["ram_amount"] / amount_ram))
                    preview_node['wall_time_on_idle'] = str(
                        math.ceil(num_jobs / jobs_on_idle_slot / node["total_slots"]) *
                        job_duration)
            else:
                preview_node['core_usage'] = str(num_cpu) + "/" + \
                                             str(slot_size["cores"]) + " (" + str(
                                                 int(round((num_cpu / slot_size["cores"])
                                                           * 100))) + "%)"
                preview_node['sim_jobs'] = 0
                preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(
                    slot_size["ram_amount"]) + " GiB (" \
                    + str(int(round((amount_ram / slot_size["ram_amount"]) * 100))) + "%)"
                preview_node['fits'] = 'NO'
            preview_res['preview'].append(preview_node)
    elif num_gpu != 0:
        #  Check all GPU nodes
        for node in gpu:
            available_slots = node["total_slots"] - node["slots_in_use"]
            available_ram = node["total_ram"] - node["ram_in_use"]
            slot_size = node["slot_size"]
            node_dict = {'name': node["node"], 'type': 'gpu/static',
                         'workers': str(node["total_slots"]),
                         'ram': str(node["total_ram"]),
                         'slot_cores': str(slot_size["cores"]),
                         'slot_ram': str(slot_size["ram_amount"]),
                         'slot_free': str(available_slots),
                         'ram_free': str(available_ram)}
            preview_res['nodes'].append(node_dict)
            # if the job fits, calculate and return the usage
            preview_node = {'name': node["node"],
                            'type': 'gpu',
                            'fits': 'NO',
                            'core_usage': '------',
                            'ram_usage': '------',
                            'sim_jobs': '------',
                            'wall_time_on_idle': 0}
            if num_gpu <= slot_size["cores"] and amount_ram <= slot_size["ram_amount"]:
                preview_node['core_usage'] = str(num_gpu) + "/" + \
                                             str(slot_size["cores"]) + " (" + str(
                                                 int(round((num_gpu / slot_size["cores"])
                                                           * 100))) + "%)"
                preview_node['sim_jobs'] = available_slots
                preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(
                    slot_size["ram_amount"]) + " GiB (" + str(
                        int(round((amount_ram / slot_size["ram_amount"]) * 100))) + "%)"
                preview_node['fits'] = 'YES'
                if job_duration != 0:
                    gpu_fits = int(slot_size["cores"] / num_gpu)
                    jobs_on_idle_slot = gpu_fits \
                        if amount_ram == 0 \
                        else min(gpu_fits, int(slot_size["ram_amount"] / amount_ram))
                    preview_node['wall_time_on_idle'] = str(
                        math.ceil(num_jobs / jobs_on_idle_slot / node["total_slots"]) *
                        job_duration)
            else:
                preview_node['core_usage'] = str(num_gpu) + "/" + \
                                             str(slot_size["cores"]) + " (" + str(
                                                 int(round((num_gpu / slot_size["cores"])
                                                           * 100))) + "%)"
                preview_node['sim_jobs'] = 0
                preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(
                    slot_size["ram_amount"]) + " GiB (" \
                    + str(int(round((amount_ram / slot_size["ram_amount"]) * 100))) + "%)"
                preview_node['fits'] = 'NO'
            preview_res['preview'].append(preview_node)
    else:
        return {}

    preview_res['preview'] = order_node_preview(preview_res['preview'])
    if maxnodes != 0 and len(preview_res['preview']) > maxnodes:
        preview_res['preview'] = preview_res['preview'][:maxnodes]

    pretty_print_slots(preview_res)
    return preview_res


def order_node_preview(node_preview: list) -> list:
    """
    Order the list of checked nodes by fits/fits not and number of similar jobs descending.
    :param node_preview:
    :return:
    """
    return sorted(node_preview, key=lambda nodes: (nodes["sim_jobs"]), reverse=True)


def prepare_checking(arg_values, cpu: int, gpu: int, ram: str, disk: str,
                     jobs: int, job_duration: str, maxnodes: int) -> bool:
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
    :return:
    """
    slot_config = define_slots()
    static_slts = slot_config["static"]
    dynamic_slts = slot_config["dynamic"]
    gpu_slts = slot_config["gpu"]

    [ram, ram_unit] = split_number_unit(ram)
    ram = calc_to_bin(ram, ram_unit)
    [disk, disk_unit] = split_number_unit(disk)
    disk = calc_to_bin(disk, disk_unit)

    [job_duration, duration_unit] = split_duration_unit(job_duration)
    job_duration = calc_to_min(job_duration, duration_unit)

    if arg_values is not None and arg_values.verbose:
        print("verbosity turned on")
    if cpu == 0:
        print("No number of CPU workers given --- ABORTING")
    elif ram == 0.0:
        print("No RAM amount given --- ABORTING")
    else:
        check_slots(static_slts, dynamic_slts, gpu_slts, cpu, ram, disk, gpu,
                    jobs, job_duration, maxnodes)
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
    DISK_SPACE = CMD_ARGS.Disk

    JOB_AMOUNT = CMD_ARGS.jobs
    if JOB_AMOUNT is None:
        JOB_AMOUNT = 1
    JOB_DURATION = CMD_ARGS.duration

    MATLAB_NODES = CMD_ARGS.maxnodes
    if MATLAB_NODES is None:
        MATLAB_NODES = 0
    prepare_checking(CMD_ARGS, CPU_WORKERS, GPU_WORKERS, RAM_AMOUNT, DISK_SPACE,
                     JOB_AMOUNT, JOB_DURATION, MATLAB_NODES)
