"""Display styling functions for console output."""

from rich.console import Console
from rich.table import Table

from htcrystalball.utils import minutes_to_hours, hours_to_days, compare_requested_available


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
    color_node = "#add8e6"
    # create table headers for verbose output
    if verbose:
        table = Table(caption="Prediction per node", show_header=True, header_style="bold cyan", show_edge=False)
        table.add_column("Jobs", justify="right")
        table.add_column("Node", style="dim", width=12)
        table.add_column("Slot", justify="right")
        table.add_column("CPUs", justify="right")
        table.add_column("RAM", justify="center")
        table.add_column("Disk", justify="center")
        table.add_column("GPUs", justify="center")

    total_jobs = 0
    for slot in result['preview']:
        total_jobs += slot['sim_jobs']*slot['SimSlots']

        if int(slot['sim_jobs']) == 0:
            node_jobs = 0
        else:
            node_jobs = slot['sim_jobs']*slot['SimSlots']
        # create table row for verbose output
        if verbose:
            if slot["SimSlots"] != 1:
                slot["SimSlots"] = "1.."+str(slot["SimSlots"])

            color_cpu = compare_requested_available(slot['requested_cpu'], slot['TotalSlotCpus'])
            color_ram = compare_requested_available(slot['requested_ram'], slot['TotalSlotMemory'])
            color_disk = compare_requested_available(slot['requested_disk'], slot['TotalSlotDisk'])
            color_gpu = compare_requested_available(slot['requested_gpu'], slot['TotalSlotGPUs'])

            table.add_row(
                f"{node_jobs}",
                f"[{color_node}]{slot['Machine']}[/{color_node}]",
                f"{slot['SimSlots']}",
                f"[{color_cpu}]{slot['requested_cpu']}/{slot['TotalSlotCpus']}[/{color_cpu}]",
                f"[{color_ram}]{slot['requested_ram']}/{slot['TotalSlotMemory']}G[/{color_ram}]",
                f"[{color_disk}]{slot['requested_disk']}/{slot['TotalSlotDisk']}G[/{color_disk}]",
                f"[{color_gpu}]{slot['requested_gpu']}/{slot['TotalSlotGPUs']}[/{color_gpu}]"
            )
    # write table and wall-time info to console
    if verbose:
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
                    console.print(slot['Machine'], style=color_node)
                console.print("")

    if wall_time > 0.0 and n_jobs > 0 and total_jobs > 0:
        time = int(max(n_jobs / total_jobs, 1)*wall_time + 0.5)
        unit = "minute(s)"
        if time > 100:
            time = minutes_to_hours(time)
            unit = "hours"
        if time > 100:
            time = hours_to_days(time)
            unit = "days"
        core_hours = int(n_jobs * wall_time * n_cores / 60.0)
        console.print("A total of "+str(core_hours)+" core-hour(s) "
                      "will be used and will complete in about " +
                      str(time)+" "+unit+".")
    else:
        console.print("No --jobs or --jobs-time specified. No duration estimate will be given.")

    console.print("")
    console.print("The above number(s) are for an idle pool.")
