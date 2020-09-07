"""Gets a user input for job and a condor slot configuration, and checks how the job fits into each slot."""
import math
from rich.console import Console
from rich.table import Table


def check_slots(static: list, dynamic: list, gpu: list, num_cpu: int,
                amount_ram: float, amount_disk: float, num_gpu: int,
                num_jobs: int, job_duration: float, maxnodes: int, verbose: bool) -> dict:
    """
    Handles the checking for all node/slot types and invokes the output methods.

    Args:
        static: A list of static slot configurations
        dynamic: A list of dynamic slot configurations
        gpu: A list of gpu slot configurations
        num_cpu: The requested number of CPU cores
        amount_ram: The requested amount of RAM
        amount_disk: The requested amount of disk space
        num_gpu: The requested number of GPUs
        num_jobs: The amount of similar jobs to execute
        job_duration: The duration for each job to execute
        maxnodes: The maximum number of nodes to execute the jobs
        verbose: Flag to extend the output.

    Returns:

    """
    if verbose:
        pretty_print_input(num_cpu, amount_ram, amount_disk, num_gpu,
                           num_jobs, job_duration, maxnodes)

    preview_res = {'slots': [], 'preview': []}

    if num_cpu != 0 and num_gpu == 0:
        for node in dynamic:
            [node_dict, preview_node] = check_dynamic_slots(node, num_cpu,
                                                            amount_ram, job_duration, num_jobs)
            preview_res['slots'].append(node_dict)
            preview_res['preview'].append(preview_node)

        for node in static:
            [node_dict, preview_node] = check_static_slots(node, num_cpu,
                                                           amount_ram, job_duration, num_jobs)
            preview_res['slots'].append(node_dict)
            preview_res['preview'].append(preview_node)
    elif num_cpu != 0 and num_gpu != 0:
        for node in gpu:
            [node_dict, preview_node] = check_gpu_slots(node, num_cpu, num_gpu,
                                                        amount_ram, job_duration, num_jobs)
            preview_res['slots'].append(node_dict)
            preview_res['preview'].append(preview_node)
    else:
        return {}

    preview_res['preview'] = order_node_preview(preview_res['preview'])
    if maxnodes != 0 and len(preview_res['preview']) > maxnodes:
        preview_res['preview'] = preview_res['preview'][:maxnodes]

    if verbose:
        pretty_print_slots(preview_res)
    pretty_print_result(preview_res, verbose)

    return preview_res


def check_dynamic_slots(slot: dict, num_cpu: int, amount_ram: float,
                        job_duration: float, num_jobs: int) -> [dict, dict]:
    """
    Checks all dynamic slots if they fit the job.

    Args:
        slot: The slot to be checked for running the specified job.
        num_cpu: The number of CPU cores for a single job
        amount_ram: The amount of RAM for a single job
        job_duration: The duration for a single job to execute
        num_jobs: The number of similar jobs to be executed

    Returns:
        A dictionary of the checked slot and a dictionary with the occupancy details of the slot.
    """
    available_cores = slot["TotalSlotCpus"]
    node_dict = {'node': slot["UtsnameNodename"],
                 'type': slot["SlotType"],
                 'total_slots': str(slot["TotalSlots"]),
                 'cores': str(slot["TotalSlotCpus"]),
                 'disk': str(slot["TotalSlotDisk"]),
                 'ram': str(slot["TotalSlotMemory"])}

    # if the job fits, calculate and return the usage
    preview_node = {'name': slot["UtsnameNodename"],
                    'type': "dynamic",
                    'fits': 'NO',
                    'core_usage': '------',
                    'gpu_usage': '------',
                    'ram_usage': '------',
                    'sim_jobs': '------',
                    'wall_time_on_idle': 0}
    if num_cpu <= available_cores and amount_ram <= slot["TotalSlotMemory"]:
        preview_node['core_usage'] = str(num_cpu) + "/" + \
                                     str(slot["TotalSlotCpus"]) + " (" + \
                                     str(int(round((num_cpu / slot["TotalSlotCpus"]) * 100))) \
                                     + "%)"
        preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + \
                                    str(slot["TotalSlotMemory"]) + " GiB (" + \
                                    str(int(round((amount_ram / slot["TotalSlotMemory"]) * 100))) \
                                    + "%)"
        preview_node['fits'] = 'YES'
        preview_node['sim_jobs'] = min(int(available_cores / num_cpu),
                                       int(slot["TotalSlotMemory"] / amount_ram))
    else:
        preview_node['core_usage'] = str(num_cpu) + "/" + \
                                     str(slot["TotalSlotCpus"]) + " (" + str(
                                         int(round((num_cpu / slot["TotalSlotCpus"])
                                                   * 100))) + "%)"
        preview_node['sim_jobs'] = 0
        preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(
            slot["TotalSlotMemory"]) + " GiB (" \
            + str(int(round((amount_ram / slot["TotalSlotMemory"]) * 100))) + "%)"
        preview_node['fits'] = 'NO'

    if num_cpu <= slot["TotalSlotCpus"] and amount_ram <= slot["TotalSlotMemory"] \
            and job_duration != 0:
        cpu_fits = int(slot["TotalSlotCpus"] / num_cpu)
        jobs_parallel = cpu_fits \
            if amount_ram == 0 \
            else min(cpu_fits, int(slot["TotalSlotMemory"] / amount_ram))
        preview_node['wall_time_on_idle'] = str(math.ceil(num_jobs /
                                                          jobs_parallel) * job_duration)
    return [node_dict, preview_node]


def check_static_slots(slot: dict, num_cores: int, amount_ram: float,
                       job_duration: float, num_jobs: int) -> [dict, dict]:
    """
    Checks all static slots if they fit the job.

    Args:
        slot: The slot to be checked for running the specified job.
        num_cores: The number of CPU cores for a single job
        amount_ram: The amount of RAM for a single job
        job_duration: The duration for a single job to execute
        num_jobs: The number of similar jobs to be executed

    Returns:
        A dictionary of the checked slot and a dictionary with the occupancy details of the slot.
    """
    available_slots = slot["TotalSlotCpus"]
    node_dict = {'node': slot["UtsnameNodename"],
                 'type': slot["SlotType"],
                 'total_slots': str(slot["TotalSlots"]),
                 'cores': str(slot["TotalSlotCpus"]),
                 'disk': str(slot["TotalSlotDisk"]),
                 'ram': str(slot["TotalSlotMemory"])}

    # if the job fits, calculate and return the usage
    preview_node = {'name': slot["UtsnameNodename"],
                    'type': 'static',
                    'fits': 'NO',
                    'core_usage': '------',
                    'gpu_usage': '------',
                    'ram_usage': '------',
                    'sim_jobs': '------',
                    'wall_time_on_idle': 0}
    if num_cores <= slot["TotalSlotCpus"] and amount_ram <= slot["TotalSlotMemory"]:
        preview_node['core_usage'] = str(num_cores) + "/" + \
                                     str(slot["TotalSlotCpus"]) + " (" + str(
                                         int(round((num_cores / slot["TotalSlotCpus"])
                                                   * 100))) + "%)"
        preview_node['sim_jobs'] = available_slots
        preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(
            slot["TotalSlotMemory"]) + " GiB (" \
            + str(int(round((amount_ram / slot["TotalSlotMemory"]) * 100))) + "%)"
        preview_node['fits'] = 'YES'
        if job_duration != 0:
            cpu_fits = int(slot["TotalSlotCpus"] / num_cores)
            jobs_on_idle_slot = cpu_fits \
                if amount_ram == 0 \
                else min(cpu_fits, int(slot["TotalSlotMemory"] / amount_ram))
            preview_node['wall_time_on_idle'] = str(
                math.ceil(num_jobs / jobs_on_idle_slot / slot["TotalSlots"]) *
                job_duration)
    else:
        preview_node['core_usage'] = str(num_cores) + "/" + \
                                     str(slot["TotalSlotCpus"]) + " (" + str(
                                         int(round((num_cores / slot["TotalSlotCpus"])
                                                   * 100))) + "%)"
        preview_node['sim_jobs'] = 0
        preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(
            slot["TotalSlotMemory"]) + " GiB (" \
            + str(int(round((amount_ram / slot["TotalSlotMemory"]) * 100))) + "%)"
        preview_node['fits'] = 'NO'
    return [node_dict, preview_node]


def check_gpu_slots(slot: dict, num_cores: int, num_gpu: int, amount_ram: float,
                    job_duration: float, num_jobs: int) -> [dict, dict]:
    """
    Checks all gpu slots if they fit the job.

    Args:
        slot: The slot to be checked for running the specified job.
        num_cores: The number of CPU cores for a single job
        num_gpu: The number of GPU units for a single job
        amount_ram: The amount of RAM for a single job
        job_duration: The duration for a single job to execute
        num_jobs: The number of similar jobs to be executed

    Returns:
        A dictionary of the checked slot and a dictionary with the occupancy details of the slot.
    """
    available_slots = slot["TotalSlotCpus"]
    node_dict = {'node': slot["UtsnameNodename"],
                 'type': slot["SlotType"],
                 'total_slots': str(slot["TotalSlots"]),
                 'cores': str(slot["TotalSlotCpus"]),
                 'gpus': str(slot["TotalSlotGPUs"]),
                 'disk': str(slot["TotalSlotDisk"]),
                 'ram': str(slot["TotalSlotMemory"])}

    # if the job fits, calculate and return the usage
    preview_node = {'name': slot["UtsnameNodename"],
                    'type': 'gpu',
                    'fits': 'NO',
                    'gpu_usage': '------',
                    'core_usage': '------',
                    'ram_usage': '------',
                    'sim_jobs': '------',
                    'wall_time_on_idle': 0}
    if num_cores <= slot["TotalSlotCpus"] and amount_ram <= slot["TotalSlotMemory"] \
            and num_gpu <= slot["TotalSlotGPUs"]:
        preview_node['core_usage'] = str(num_cores) + "/" + \
                                     str(slot["TotalSlotCpus"]) + " (" + str(
                                         int(round((num_cores / slot["TotalSlotCpus"])
                                                   * 100))) + "%)"
        preview_node['gpu_usage'] = str(num_gpu) + "/" + \
            str(slot["TotalSlotGPUs"]) + " (" + str(
                int(round((num_gpu / slot["TotalSlotGPUs"])
                          * 100))) + "%)"
        preview_node['sim_jobs'] = min(int(slot["TotalSlotGPUs"] / num_gpu),
                                       int(available_slots / num_cores),
                                       int(slot["TotalSlotMemory"] / amount_ram))
        preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(
            slot["TotalSlotMemory"]) + " GiB (" \
            + str(int(round((amount_ram / slot["TotalSlotMemory"]) * 100))) + "%)"
        preview_node['fits'] = 'YES'
        if job_duration != 0:
            cpu_fits = int(slot["TotalSlotCpus"] / num_cores)
            gpu_fits = int(slot["TotalSlotGPUs"] / num_gpu)
            jobs_on_idle_slot = min(cpu_fits, gpu_fits) \
                if amount_ram == 0 \
                else min(min(cpu_fits, gpu_fits), int(slot["TotalSlotMemory"] / amount_ram))
            preview_node['wall_time_on_idle'] = str(
                math.ceil(num_jobs / jobs_on_idle_slot / slot["TotalSlotGPUs"]) *
                job_duration)
    else:
        preview_node['core_usage'] = str(num_cores) + "/" + \
                                     str(slot["TotalSlotCpus"]) + " (" + str(
                                         int(round((num_cores / slot["TotalSlotCpus"])
                                                   * 100))) + "%)"
        if slot["TotalSlotGPUs"] == 0:
            preview_node['gpu_usage'] = "No GPU ressource!"
        else:
            preview_node['gpu_usage'] = str(num_gpu) + "/" + \
                str(slot["TotalSlotGPUs"]) + " (" + str(
                    int(round((num_gpu / slot["TotalSlotGPUs"])
                              * 100))) + "%)"
        preview_node['sim_jobs'] = 0
        preview_node['ram_usage'] = "{0:.2f}".format(amount_ram) + "/" + str(
            slot["TotalSlotMemory"]) + " GiB (" \
            + str(int(round((amount_ram / slot["TotalSlotMemory"]) * 100))) + "%)"
        preview_node['fits'] = 'NO'
    return [node_dict, preview_node]


def order_node_preview(node_preview: list) -> list:
    """
    Order the list of checked nodes by fits/fits not and number of similar jobs descending.

    Args:
        node_preview: the list of checked nodes

    Returns:
        A list of checked nodes sorted by number of similar executable jobs.
    """
    return sorted(node_preview, key=lambda nodes: (nodes["sim_jobs"]), reverse=True)


#  print out what the user gave as input
def pretty_print_input(num_cpu: int, amount_ram: float, amount_disk: float, num_gpu: int,
                       num_jobs: int, num_duration: float, max_nodes: int):
    """
    Prints out the already converted user input to the console using rich tables.

    Args:
        num_cpu: The requested number CPU cores
        amount_ram: The requested amount of RAM
        amount_disk: The requested amount of disk space
        num_gpu: The requested number of GPU units
        num_jobs: The user-defined amount of similar jobs
        num_duration: The user-defined estimated duration per job
        max_nodes: The user-defined maximum number of simultaneous occupied nodes

    Returns:

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


def pretty_print_slots(result: dict):
    """
    Prints out the slots to the console using rich tables.

    Args:
        result: A dictionary of slot configurations.

    Returns:

    """
    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Node", style="dim", width=12)
    table.add_column("Slot Type")
    table.add_column("Total Slots", justify="right")
    table.add_column("Cores", justify="right")
    table.add_column("GPUs", justify="right")
    table.add_column("RAM", justify="right")
    table.add_column("DISK", justify="right")

    for slot in result['slots']:
        if slot['type'] == "static":
            color_val = 'dark_blue'
            table.add_row(f"[{color_val}]{slot['node']}[/{color_val}]",
                          f"[{color_val}]{slot['type']}[/{color_val}]",
                          f"[{color_val}]{slot['total_slots']}[/{color_val}]",
                          f"[{color_val}]{slot['cores']}[/{color_val}]",
                          f"[{color_val}]------[/{color_val}]",
                          f"[{color_val}]{slot['ram']} GiB[/{color_val}]",
                          f"[{color_val}]{slot['disk']} GiB[/{color_val}]")
        elif slot['type'] == "gpu":
            color_val = 'purple4'
            table.add_row(f"[{color_val}]{slot['node']}[/{color_val}]",
                          f"[{color_val}]{slot['type']}[/{color_val}]",
                          f"[{color_val}]{slot['total_slots']}[/{color_val}]",
                          f"[{color_val}]{slot['cores']}[/{color_val}]",
                          f"[{color_val}]{slot['gpus']}[/{color_val}]",
                          f"[{color_val}]{slot['ram']} GiB[/{color_val}]",
                          f"[{color_val}]{slot['disk']} GiB[/{color_val}]")
        else:
            color_val = 'dark_red'
            table.add_row(f"[{color_val}]{slot['node']}[/{color_val}]",
                          f"[{color_val}]{slot['type']}[/{color_val}]",
                          f"[{color_val}]{slot['total_slots']}[/{color_val}]",
                          f"[{color_val}]{slot['cores']}[/{color_val}]",
                          f"[{color_val}]------[/{color_val}]",
                          f"[{color_val}]{slot['ram']} GiB[/{color_val}]",
                          f"[{color_val}]{slot['disk']} GiB[/{color_val}]")

    console.print("---------------------- NODES ----------------------")
    console.print(table)


def pretty_print_result(result: dict, verbose: bool):
    """
    Prints out the preview result to the console using rich tables.

    Args:
        result: A dictionary of slot configurations including occupancy values for
        the requested job size.
        verbose: A value to extend the generated output.

    Returns:

    """
    console = Console()

    table = Table(show_header=True, header_style="bold cyan")
    if verbose:
        table.add_column("Node", style="dim", width=12)
    table.add_column("Slot Type")
    table.add_column("Job fits", justify="right")
    if verbose:
        table.add_column("Slot usage", justify="right")
        table.add_column("RAM usage", justify="center")
        table.add_column("GPU usage", justify="center")
    table.add_column("Amount of similar jobs", justify="right")
    table.add_column("Wall Time on IDLE", justify="right")

    for slot in result['preview']:
        if slot['fits'] == "YES":
            color_val = 'green'
            if verbose:
                table.add_row(f"[{color_val}]{slot['name']}[/{color_val}]",
                              f"[{color_val}]{slot['type']}[/{color_val}]",
                              f"[{color_val}]{slot['fits']}[/{color_val}]",
                              f"[{color_val}]{slot['core_usage']} Cores[/{color_val}]",
                              f"[{color_val}]{slot['ram_usage']}[/{color_val}]",
                              f"[{color_val}]{slot['gpu_usage']}[/{color_val}]",
                              f"[{color_val}]{slot['sim_jobs']}[/{color_val}]",
                              f"[{color_val}]{slot['wall_time_on_idle']} min[/{color_val}]")
            else:
                table.add_row(f"[{color_val}]{slot['type']}[/{color_val}]",
                              f"[{color_val}]{slot['fits']}[/{color_val}]",
                              f"[{color_val}]{slot['sim_jobs']}[/{color_val}]",
                              f"[{color_val}]{slot['wall_time_on_idle']} min[/{color_val}]")
        else:
            color_val = 'red'
            if verbose:
                table.add_row(f"[{color_val}]{slot['name']}[/{color_val}]",
                              f"[{color_val}]{slot['type']}[/{color_val}]",
                              f"[{color_val}]{slot['fits']}[/{color_val}]",
                              f"[{color_val}]{slot['core_usage']} Cores[/{color_val}]",
                              f"[{color_val}]{slot['ram_usage']}[/{color_val}]",
                              f"[{color_val}]{slot['gpu_usage']}[/{color_val}]",
                              f"[{color_val}]{slot['sim_jobs']}[/{color_val}]",
                              f"[{color_val}]{slot['wall_time_on_idle']} min[/{color_val}]")
            else:
                table.add_row(f"[{color_val}]{slot['type']}[/{color_val}]",
                              f"[{color_val}]{slot['fits']}[/{color_val}]",
                              f"[{color_val}]{slot['sim_jobs']}[/{color_val}]",
                              f"[{color_val}]{slot['wall_time_on_idle']} min[/{color_val}]")

    console.print("---------------------- PREVIEW ----------------------")
    console.print(table)
