"""Examines user input on the HTCondor slot configuration."""

from natsort import natsorted

from htcrystalball import display, collect, LOGGER
from htcrystalball.utils import split_num_str, to_minutes, to_binary_gigabyte


def filter_slots(slots: dict, slot_type: str) -> list:
    """Filters the slots stored in a dictionary according to the given type."""
    result = []
    for node in slots:
        for slot in slots[node]["slot_size"]:
            if slot["SlotType"] == slot_type:
                slot["Machine"] = slots[node]["Machine"]
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
    elif job_duration > 0.0 and jobs == 0:
        LOGGER.warning("No Job amount for wall-time calculation given --- ABORTING")
    elif jobs > 1 and job_duration == 0.0:
        LOGGER.warning("No execution time for Jobs has been given --- ABORTING")
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

    results['preview'] = natsorted(results['preview'], key=lambda y: y["Machine"].lower())
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
        'Machine': slot_name,
        'SlotType': slot_type,
        'fits': 'NO',
        'TotalSlotCpus': 0,
        'requested_cpu': 0,
        'TotalSlotGPUs': 0,
        'requested_gpu': 0,
        'TotalSlotMemory': 0,
        'requested_ram': 0,
        'TotalSlotDisk': 0,
        'requested_disk': 0,
        'sim_jobs': 0
    }


def check_slot_by_type(slot: dict, n_cpu: int, ram: float, disk: float,
                       slot_type: str, n_gpu: int = 0) -> (dict, dict):
    """
    Checks all Partitionable slots if they fit the job.

    Args:
        slot: The slot to be checked for running the specified job.
        n_cpu: The number of CPU cores for a single job
        ram: The amount of RAM for a single job
        disk: The amount of disk space for a single job
        slot_type: The type of slot, allowed {'Static', 'Partitionable'}
        n_gpu: Optional. The number of GPU units for a single job

    Returns:
        A dictionary of the checked slot and a dictionary with the occupancy
        details of the slot.
    """
    if slot_type not in ['Static', 'Partitionable']:
        raise ValueError(f'slot_type must be Static or Partitionable'
                         f'not {slot_type}')

    preview = default_preview(slot['Machine'], slot_type)
    preview['TotalSlotCpus'] = slot['TotalSlotCpus']
    preview['TotalSlotMemory'] = slot['TotalSlotMemory']
    preview['TotalSlotDisk'] = slot['TotalSlotDisk']
    preview['TotalSlotGPUs'] = slot['TotalSlotGPUs']

    preview['requested_cpu'] = n_cpu
    preview['requested_gpu'] = n_gpu
    preview['requested_ram'] = ram
    preview['requested_disk'] = disk

    fits_job = n_cpu <= slot['TotalSlotCpus'] and ram <= slot['TotalSlotMemory'] \
        and disk <= slot["TotalSlotDisk"] and n_gpu <= slot['TotalSlotGPUs']

    if fits_job:
        preview['fits'] = 'YES'

        sim_jobs = int(preview['TotalSlotCpus'] / n_cpu) if n_cpu > 0 else 0
        sim_jobs = min(sim_jobs, int(preview['TotalSlotMemory'] / ram)) if ram > 0.0 else sim_jobs
        sim_jobs = min(sim_jobs, int(preview['TotalSlotDisk'] / disk)) if disk > 0.0 else sim_jobs
        sim_jobs = min(sim_jobs, int(preview['TotalSlotGPUs'] / n_gpu)) if n_gpu > 0 else sim_jobs
        preview['sim_jobs'] = sim_jobs

        preview['requested_cpu'] = n_cpu*sim_jobs
        preview['requested_gpu'] = n_gpu*sim_jobs
        preview['requested_ram'] = ram*sim_jobs
        preview['requested_disk'] = disk*sim_jobs
        # pct_gpu = int(round((n_gpu / total_gpus) * 100 * preview['sim_jobs'], 0))

    else:
        preview['fits'] = 'NO'
        preview['sim_jobs'] = 0
    # add number of similar slots to the result
    preview['SimSlots'] = slot['SimSlots']
    return [slot, preview]


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
