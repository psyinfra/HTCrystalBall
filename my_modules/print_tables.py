from rich.console import Console
from rich.table import Table


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
