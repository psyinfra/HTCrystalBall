"""Gets a user input for job and a condor slot configuration, and checks how the job fits into each slot."""
import math
import my_modules.print_tables as print_slots


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
        print_slots.pretty_print_input(num_cpu, amount_ram, amount_disk, num_gpu,
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
        print_slots.pretty_print_slots(preview_res)
    print_slots.pretty_print_result(preview_res, verbose)

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
