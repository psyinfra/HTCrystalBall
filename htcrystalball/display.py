from rich.console import Console
from rich.table import Table


def inputs(num_cpu: int, amount_ram: float, amount_disk: float, num_gpu: int,
           num_jobs: int, num_duration: float, max_nodes: int) -> None:
    """
    Prints out the already converted user input to the console using rich
    tables.

    Args:
        num_cpu: The requested number CPU cores
        amount_ram: The requested amount of RAM
        amount_disk: The requested amount of disk space
        num_gpu: The requested number of GPU units
        num_jobs: The user-defined amount of similar jobs
        num_duration: The user-defined estimated duration per job
        max_nodes: The user-defined maximum number of simultaneous occupied
            nodes
    """
    console = Console()
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Parameter", style="dim")
    table.add_column("Input Value", justify="right")
    table.add_row("CPUS", str(num_cpu))
    table.add_row("RAM", f'{amount_ram:.2f} GiB')
    table.add_row("STORAGE", f'{amount_disk:.2f} GiB')
    table.add_row("GPUS", str(num_gpu))
    table.add_row("JOBS", str(num_jobs))
    table.add_row("JOB DURATION", f'{num_duration:.2f} min')
    table.add_row("MAXIMUM NODES", str(max_nodes))
    console.print("---------------------- INPUT ----------------------")
    console.print(table)


def slots(result: dict) -> None:
    """
    Prints out the slots to the console using rich tables.

    Args:
        result: A dictionary of slot configurations.
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
            color = 'dark_blue'
            table.add_row(
                f"[{color}]{slot['node']}[/{color}]",
                f"[{color}]{slot['type']}[/{color}]",
                f"[{color}]{slot['total_slots']}[/{color}]",
                f"[{color}]{slot['cores']}[/{color}]",
                f"[{color}]------[/{color}]",
                f"[{color}]{slot['ram']} GiB[/{color}]",
                f"[{color}]{slot['disk']} GiB[/{color}]"
            )

        elif slot['type'] == "gpu":
            color = 'purple4'
            table.add_row(
                f"[{color}]{slot['node']}[/{color}]",
                f"[{color}]{slot['type']}[/{color}]",
                f"[{color}]{slot['total_slots']}[/{color}]",
                f"[{color}]{slot['cores']}[/{color}]",
                f"[{color}]{slot['gpus']}[/{color}]",
                f"[{color}]{slot['ram']} GiB[/{color}]",
                f"[{color}]{slot['disk']} GiB[/{color}]"
            )

        else:
            color = 'dark_red'
            table.add_row(
                f"[{color}]{slot['node']}[/{color}]",
                f"[{color}]{slot['type']}[/{color}]",
                f"[{color}]{slot['total_slots']}[/{color}]",
                f"[{color}]{slot['cores']}[/{color}]",
                f"[{color}]------[/{color}]",
                f"[{color}]{slot['ram']} GiB[/{color}]",
                f"[{color}]{slot['disk']} GiB[/{color}]"
            )

    console.print("---------------------- NODES ----------------------")
    console.print(table)


def results(result: dict, verbose: bool) -> None:
    """
    Prints out the preview result to the console using rich tables.

    Args:
        result: A dictionary of slot configurations including occupancy values
            for the requested job size.
        verbose: A value to extend the generated output.
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
            color = 'green'
            if verbose:
                table.add_row(
                    f"[{color}]{slot['name']}[/{color}]",
                    f"[{color}]{slot['type']}[/{color}]",
                    f"[{color}]{slot['fits']}[/{color}]",
                    f"[{color}]{slot['core_usage']} Cores[/{color}]",
                    f"[{color}]{slot['ram_usage']}[/{color}]",
                    f"[{color}]{slot['gpu_usage']}[/{color}]",
                    f"[{color}]{slot['sim_jobs']}[/{color}]",
                    f"[{color}]{slot['wall_time_on_idle']} min[/{color}]"
                )
            else:
                table.add_row(
                    f"[{color}]{slot['type']}[/{color}]",
                    f"[{color}]{slot['fits']}[/{color}]",
                    f"[{color}]{slot['sim_jobs']}[/{color}]",
                    f"[{color}]{slot['wall_time_on_idle']} min[/{color}]"
                )
        else:
            color = 'red'
            if verbose:
                table.add_row(
                    f"[{color}]{slot['name']}[/{color}]",
                    f"[{color}]{slot['type']}[/{color}]",
                    f"[{color}]{slot['fits']}[/{color}]",
                    f"[{color}]{slot['core_usage']} Cores[/{color}]",
                    f"[{color}]{slot['ram_usage']}[/{color}]",
                    f"[{color}]{slot['gpu_usage']}[/{color}]",
                    f"[{color}]{slot['sim_jobs']}[/{color}]",
                    f"[{color}]{slot['wall_time_on_idle']} min[/{color}]"
                )
            else:
                table.add_row(
                    f"[{color}]{slot['type']}[/{color}]",
                    f"[{color}]{slot['fits']}[/{color}]",
                    f"[{color}]{slot['sim_jobs']}[/{color}]",
                    f"[{color}]{slot['wall_time_on_idle']} min[/{color}]"
                )

    console.print("---------------------- PREVIEW ----------------------")
    console.print(table)
