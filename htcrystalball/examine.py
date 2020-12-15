"""Examines user input on the HTCondor slot configuration."""

from operator import itemgetter
from htcrystalball import display, collect, LOGGER
from htcrystalball.utils import split_num_str, to_minutes, to_binary_gigabyte


def filter_slots(slots: dict, slot_type: str) -> list:
    """Filters the slots stored in a dictionary according to the given type."""
    result = []
    for node in slots:
        for slot in slots[node]["slot_size"]:
            if slot["SlotType"] == slot_type:
                slot["UtsnameNodename"] = slots[node]["UtsnameNodename"]
                result.append(slot)

    return result


def prepare(cpu: int, gpu: int, ram: str, disk: str, jobs: int,
            job_duration: str, maxnodes: int, verbose: bool,
            content: object) -> bool:
    """
    Prepares for the examination of job requests.

    Loads the slot configuration, handles user input, and invokes checks for a
    given job request provided the request is valid.

    Args:
        cpu: User input of CPU cores
        gpu: User input of GPU units
        ram: User input of the amount of RAM
        disk: User input of the amount of disk space
        jobs: User input of the number of similar jobs
        job_duration: User input of the duration time for a single job
        maxnodes:
        verbose:
        content: the loaded HTCondor slots configuration

    Returns:
        If all needed parameters were given
    """
    config = collect.collect_slots(content)

    slots_static = filter_slots(config, 'Static')
    slots_partitionable = filter_slots(config, 'Partitionable')

    [ram, ram_unit] = split_num_str(ram, 0.0, 'GiB')
    ram = to_binary_gigabyte(ram, ram_unit)
    [disk, disk_unit] = split_num_str(disk, 0.0, 'GiB')
    disk = to_binary_gigabyte(disk, disk_unit)

    [job_duration, duration_unit] = split_num_str(job_duration, 0.0, 'min')
    job_duration = to_minutes(job_duration, duration_unit)

    if cpu == 0:
        LOGGER.warning("No number of CPU workers given --- ABORTING")

    elif ram == 0.0:
        LOGGER.warning("No RAM amount given --- ABORTING")

    else:
        check_slots(
            slots_static, slots_partitionable, cpu, ram, disk, gpu, jobs,
            job_duration, maxnodes, verbose
        )
        return True
    return False


def check_slots(static: list, partitionable: list, n_cpus: int,
                ram: float, disk_space: float, n_gpus: int,
                n_jobs: int, job_duration: float, max_nodes: int,
                verbose: bool) -> dict:
    """
    Handles the checking for all node/slot types and invokes the output
    methods.

    Args:
        static: A list of Static slot configurations
        partitionable: A list of Partitionable slot configurations
        n_cpus: The requested number of CPU cores
        ram: The requested amount of RAM
        disk_space: The requested amount of disk space
        n_gpus: The requested number of GPUs
        n_jobs: The amount of similar jobs to execute
        job_duration: The duration for each job to execute
        max_nodes: The maximum number of nodes to execute the jobs
        verbose: Flag to extend the output.

    Returns:

    """
    if verbose:
        display.inputs(
            n_cpus, ram, disk_space, n_gpus, n_jobs, job_duration,
            max_nodes
        )

    results = {'slots': [], 'preview': []}

    for node in partitionable:
        node_dict, preview_node = check_slot_by_type(
            slot=node,
            n_cpu=n_cpus,
            n_gpu=n_gpus,
            ram=ram,
            disk=disk_space,
            slot_type='Partitionable'
        )

        results['slots'].append(node_dict)
        results['preview'].append(preview_node)

    for node in static:
        node_dict, preview_node = check_slot_by_type(
            slot=node,
            n_cpu=n_cpus,
            n_gpu=n_gpus,
            ram=ram,
            disk=disk_space,
            slot_type='Static'
        )
        results['slots'].append(node_dict)
        results['preview'].append(preview_node)

    results['preview'] = order_node_preview(results['preview'])

    if max_nodes != 0 and len(results['preview']) > max_nodes:
        results['preview'] = results['preview'][:max_nodes]

    if verbose:
        results['slots'] = sorted(results['slots'], key=itemgetter('node'))
        display.slots(results)

    results['preview'] = sorted(results['preview'], key=itemgetter('name'))
    display.results(results, verbose, max_nodes != 0, n_cpus, n_jobs, job_duration)

    return results


def default_preview(slot_name: str, slot_type: str) -> dict:
    """
    Defines the default dictionary for slots that don't fit the job.

    Args:
        slot_name (str): the name of the slot, e.g. "cpu1"
        slot_type (str): the type of slot, allowed {'Partitionable', 'Static'}

    Returns:
        dict: default values for a previewed slot

    """
    return {
        'name': slot_name,
        'type': slot_type,
        'fits': 'NO',
        'gpu_usage': '0/0',
        'core_usage': '------',
        'ram_usage': '------',
        'disk_usage': '------',
        'sim_jobs': '------'
    }


def rename_slot_keys(slot: dict) -> dict:
    """
    Renames the keys for the slot dictionary
    Args:
        slot: the slot dictionary to have renamed keys

    Returns:
        renamed: the slot dictionary with renamed keys
    """
    renamed = {
        'node': slot["UtsnameNodename"],
        'type': slot["SlotType"],
        'total_slots': slot["TotalSlots"],
        'cores': slot["TotalSlotCpus"],
        'disk': slot["TotalSlotDisk"],
        'ram': slot["TotalSlotMemory"],
        'sim_slots': slot["SimSlots"]
    }

    if slot.get('TotalSlotGPUs', None):
        renamed['gpus'] = slot['TotalSlotGPUs']

    return renamed


def check_slot_by_type(slot: dict, n_cpu: int, ram: float, disk: float,
                       slot_type: str, n_gpu: int = 0) -> (dict, dict):
    """
    Checks all Partitionable slots if they fit the job.

    Args:
        slot: The slot to be checked for running the specified job.
        n_cpu: The number of CPU cores for a single job
        ram: The amount of RAM for a single job
        job_duration: The duration for a single job to execute
        n_jobs: The number of similar jobs to be executed
        slot_type: The type of slot, allowed {'Static', 'Partitionable', 'GPU'}
        n_gpu: Optional. The number of GPU units for a single job

    Returns:
        A dictionary of the checked slot and a dictionary with the occupancy
        details of the slot.
    """
    if slot_type not in ['Static', 'Partitionable']:
        raise ValueError(f'slot_type must be Static or Partitionable'
                         f'not {slot_type}')

    preview = default_preview(slot['UtsnameNodename'], slot_type)

    total_cpus = slot['TotalSlotCpus']
    total_ram = slot['TotalSlotMemory']
    total_disk = slot["TotalSlotDisk"]
    total_gpus = slot['TotalSlotGPUs'] if slot_type == 'GPU' else 0
    percentage_used_cores = int(round((n_cpu / total_cpus) * 100, 0))
    percentage_used_ram = int(round((ram / total_ram) * 100, 0))
    percentage_used_disk = 0
    if disk >= 0.1:
        used_disk = int(total_disk / disk)
        percentage_used_disk = int(round((disk / total_disk) * 100, 0))
    else:
        disk = 0.0
        used_disk = int(total_disk / 0.0001)
    fits_job = n_cpu <= total_cpus and ram <= total_ram and disk <= total_disk

    if slot_type == 'GPU':
        pct_gpu = int(round((n_gpu / total_gpus) * 100, 0))
        fits_job = fits_job and n_gpu <= total_gpus

        if total_gpus >= 1:
            preview['gpu_usage'] = f'{n_gpu}/{total_gpus} ({pct_gpu}%)'
        else:
            preview['gpu_usage'] = 'No GPU resource!'

    preview['core_usage'] = f'{n_cpu}/{total_cpus} ({percentage_used_cores}%)'
    preview['ram_usage'] = f'{ram:.0f}/{total_ram:.0f}G ({percentage_used_ram}%)'
    preview['disk_usage'] = f'{disk:.0f}/{total_disk:.0f}G ({percentage_used_disk}%)'
    if fits_job:
        preview['fits'] = 'YES'

        if slot_type == 'Partitionable':
            preview['sim_jobs'] = min(
                int(total_cpus / n_cpu),
                int(total_ram / ram),
                used_disk
            )
        elif slot_type == 'GPU':
            preview['sim_jobs'] = min(
                int(total_gpus / n_gpu),
                int(total_cpus / n_cpu),
                int(total_ram / ram),
                used_disk
            )
            tgpu = n_gpu*preview['sim_jobs']
            pct_gpu = int(round((n_gpu / total_gpus) * 100*preview['sim_jobs'], 0))
            preview['gpu_usage'] = f'{tgpu}/{total_gpus} ({pct_gpu}%)'
        elif slot_type == 'Static':
            preview['sim_jobs'] = min(
                int(total_cpus / n_cpu),
                int(total_ram / ram),
                used_disk
            )

        total_used_cores = n_cpu * int(preview['sim_jobs'])
        total_used_ram = ram * preview['sim_jobs']
        total_used_disk = disk * preview['sim_jobs']
        percentage_used_cores = int(round((n_cpu / total_cpus) * 100 * preview['sim_jobs'], 0))
        percentage_used_ram = int(round((ram / total_ram) * 100 * preview['sim_jobs'], 0))
        percentage_used_disk = int(round((disk / total_disk) * 100 * preview['sim_jobs'], 0))

        preview['core_usage'] = f'{total_used_cores}/{total_cpus} ({percentage_used_cores}%)'
        preview['ram_usage'] = f'{total_used_ram:.0f}/{total_ram:.0f}G ({percentage_used_ram}%)'
        preview['disk_usage'] = f'{total_used_disk:.0f}/{total_disk:.0f}G ({percentage_used_disk}%)'

    else:
        preview['core_usage'] = f'{n_cpu}/{total_cpus} ({percentage_used_cores}%)'
        preview['ram_usage'] = f'{ram:.0f}/{total_ram:.0f}G ({percentage_used_ram}%)'
        preview['disk_usage'] = f'{disk:.0f}/{total_disk:.0f}G ({percentage_used_disk}%)'
        preview['fits'] = 'NO'
        preview['sim_jobs'] = 0
    # add number of similar slots to the result
    preview['sim_slots'] = slot['SimSlots']
    return [rename_slot_keys(slot), preview]


def order_node_preview(node_preview: list) -> list:
    """
    Order the list of checked nodes by fits/fits not and number of similar
    jobs descending.

    Args:
        node_preview: the list of checked nodes

    Returns:
        A list of checked nodes sorted by number of similar executable jobs.
    """
    return sorted(
        node_preview, key=lambda nodes: (nodes["sim_jobs"]), reverse=True
    )
