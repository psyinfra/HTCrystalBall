"""Display styling functions for console output."""

from rich.console import Console
from rich.table import Table


def inputs(num_cpu: int, amount_ram: float, amount_disk: float, num_gpu: int,
           num_jobs: int, num_duration: float, max_nodes: int) -> None:
    """
    Print converted user input to console using rich tables.

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
    Print out the slots to the console using rich tables.

    Args:
        result: A dictionary of slot configurations.
    """
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Node", style="dim", width=12)
    table.add_column("Slots", justify="right")
    table.add_column("Cores", justify="right")
    table.add_column("GPUs", justify="right")
    table.add_column("RAM", justify="right")
    table.add_column("DISK", justify="right")

    for slot in result['slots']:
        if slot['type'] == "Static":
            color = 'dark_blue'
            table.add_row(
                f"[{color}]{slot['node']}[/{color}]",
                f"[{color}]1..{slot['sim_slots']}[/{color}]",
                f"[{color}]{slot['cores']}[/{color}]",
                f"[{color}]------[/{color}]",
                f"[{color}]{slot['ram']} GiB[/{color}]",
                f"[{color}]{slot['disk']} GiB[/{color}]"
            )

        elif slot['type'] == "GPU":
            color = 'purple4'
            table.add_row(
                f"[{color}]{slot['node']}[/{color}]",
                f"[{color}]{slot['sim_slots']}[/{color}]",
                f"[{color}]{slot['cores']}[/{color}]",
                f"[{color}]{slot['gpus']}[/{color}]",
                f"[{color}]{slot['ram']} GiB[/{color}]",
                f"[{color}]{slot['disk']} GiB[/{color}]"
            )

        else:
            color = 'dark_red'
            table.add_row(
                f"[{color}]{slot['node']}[/{color}]",
                f"[{color}]{slot['sim_slots']}[/{color}]",
                f"[{color}]{slot['cores']}[/{color}]",
                f"[{color}]------[/{color}]",
                f"[{color}]{slot['ram']} GiB[/{color}]",
                f"[{color}]{slot['disk']} GiB[/{color}]"
            )

    console.print("---------------------- NODES ----------------------")
    console.print(table)


def results(result: dict, verbose: bool, matlab: bool, n_cores: int, n_jobs: int, wall_time: float) -> None:
    """
    Print out the preview result to the console using rich tables.

    Args:
        result: A dictionary of slot configurations including occupancy values
            for the requested job size.
        verbose: A value to extend the generated output.
    """
    console = Console()
    if verbose:
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Jobs", justify="right")
        table.add_column("Node", style="dim", width=12)
        table.add_column("Slot", justify="right")
        table.add_column("Slot usage", justify="right")
        table.add_column("RAM usage", justify="center")
        table.add_column("GPU usage", justify="center")

    total_jobs = 0
    for slot in result['preview']:
        total_jobs += slot['sim_jobs']*slot['sim_slots']
        node_jobs = slot['sim_jobs']*slot['sim_slots']
        if slot["sim_slots"] != 1:
            slot["sim_slots"] = "1.."+str(slot["sim_slots"])
        if slot['fits'] == "YES":
            color = 'green'
            if verbose:
                table.add_row(
                    f"[{color}]{node_jobs}[/{color}]",
                    f"[{color}]{slot['name']}[/{color}]",
                    f"[{color}]{slot['sim_slots']}[/{color}]",
                    f"[{color}]{slot['core_usage']} Cores[/{color}]",
                    f"[{color}]{slot['ram_usage']}[/{color}]",
                    f"[{color}]{slot['gpu_usage']}[/{color}]",
                    f"[{color}]{slot['wall_time_on_idle']} min[/{color}]"
                )
        else:
            color = 'red'
            if verbose or matlab:
                table.add_row(
                    f"[{color}]0[/{color}]",
                    f"[{color}]{slot['name']}[/{color}]",
                    f"[{color}]{slot['sim_slots']}[/{color}]",
                    f"[{color}]{slot['core_usage']} Cores[/{color}]",
                    f"[{color}]{slot['ram_usage']}[/{color}]",
                    f"[{color}]{slot['gpu_usage']}[/{color}]",
                    f"[{color}]{slot['wall_time_on_idle']} min[/{color}]"
                )
    if verbose:
        console.print("---------------------- PREVIEW ----------------------")
        console.print(table)
        console.print("TOTAL MATCHES: "+str(total_jobs))
        console.print("")
        if wall_time > 0.0 and n_jobs > 0:
            time = int(max(n_jobs / total_jobs, 1)*wall_time / 60.0 + 1)
            core_hours = int(n_jobs * wall_time * n_cores / 60.0 + 1)
            console.print("A total of "+str(core_hours)+" core-hour(s) will be used and will complete in about "+str(time)+" hour(s).")
        else:
            console.print("No --jobs or --jobs-time specified. No duration estimate will be given.")
    else:
        if total_jobs == 0:
            console.print("Job size does not fit any compute slots. Use --verbose for details and a per-slot-config analysis.")
        else:
            console.print(str(total_jobs)+" jobs of this size can run on this pool.")
            console.print("")
            if matlab:
                console.print("We suggest using the following nodes:")
                for slot in result['preview']:
                    console.print(slot['name'])
                console.print("")
            if wall_time > 0.0 and n_jobs > 0:
                time = int(max(n_jobs / total_jobs, 1)*wall_time / 60.0 + 1)
                core_hours = int(n_jobs * wall_time * n_cores / 60.0 + 1)
                console.print("A total of "+str(core_hours)+" core-hour(s) will be used and will complete in about "+str(time)+" hour(s).")
            else:
                console.print("No --jobs or --jobs-time specified. No duration estimate will be given.")
            console.print("")
            console.print("The above number(s) are for an idle pool.")
