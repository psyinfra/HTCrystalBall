"""Display styling functions for console output."""

from rich.console import Console
from rich.table import Table


def results(result: dict, verbose: bool, matlab: bool,
            n_cores: int, n_jobs: int, wall_time: float) -> None:
    """
    Print out the preview result to the console using rich tables.

    Args:
        result: A dictionary of slot configurations including occupancy values
            for the requested job size.
        verbose: A value to extend the generated output.
        matlab: A bool telling whether matlab mode output is needed
        n_cores: number of requested cores for wall-time calculation
        n_jobs: number of requested jobs for wall-time execution
        wall_time: time per job, needed for total wall-time execution
    """
    console = Console()

    # create table headers for verbose output
    if verbose:
        table = Table(show_header=True, header_style="bold cyan", show_edge=False)
        table.add_column("Jobs", justify="right")
        table.add_column("Node", style="dim", width=12)
        table.add_column("Slot", justify="right")
        table.add_column("CPUs", justify="right")
        table.add_column("RAM", justify="center")
        table.add_column("Disk", justify="center")
        table.add_column("GPUs", justify="center")

    total_jobs = 0
    for slot in result['preview']:
        total_jobs += slot['sim_jobs']*slot['sim_slots']

        if int(slot['sim_jobs']) == 0:
            node_jobs = 0
        else:
            node_jobs = slot['sim_jobs']*slot['sim_slots']
        # create table row for verbose output
        if verbose:
            if slot["sim_slots"] != 1:
                slot["sim_slots"] = "1.."+str(slot["sim_slots"])
            if slot['fits'] == "YES":
                color = 'green'
            else:
                color = 'red'

            table.add_row(
                f"[{color}]{node_jobs}[/{color}]",
                f"[{color}]{slot['name']}[/{color}]",
                f"[{color}]{slot['sim_slots']}[/{color}]",
                f"[{color}]{slot['core_usage']}[/{color}]",
                f"[{color}]{slot['ram_usage']}[/{color}]",
                f"[{color}]{slot['disk_usage']}[/{color}]",
                f"[{color}]{slot['gpu_usage']}[/{color}]"
            )
    # write table and wall-time info to console
    if verbose:
        console.print("---------------------- PREVIEW ----------------------")
        console.print(table)
        console.print("")
        console.print("TOTAL MATCHES: "+str(total_jobs))
        console.print("")
    # write slot and wall-time info to console
    else:
        if total_jobs == 0:
            console.print("Job size does not fit any compute slots. "
                          "Use --verbose for details and a per-slot-config analysis.")
        else:
            console.print(str(total_jobs)+" jobs of this size can run on this pool.")
            console.print("")
            if matlab:
                console.print("We suggest using the following nodes:")
                for slot in result['preview']:
                    console.print(slot['name'])
                console.print("")

    if wall_time > 0.0 and n_jobs > 0 and total_jobs > 0:
        time = int(max(n_jobs / total_jobs, 1)*wall_time / 60.0 + 1)
        core_hours = int(n_jobs * wall_time * n_cores / 60.0 + 1)
        console.print("A total of "+str(core_hours)+" core-hour(s) "
                      "will be used and will complete in about " +
                      str(time)+" hour(s).")
    else:
        console.print("No --jobs or --jobs-time specified. No duration estimate will be given.")

    console.print("")
    console.print("The above number(s) are for an idle pool.")
