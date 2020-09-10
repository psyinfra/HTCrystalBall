"""Examines user input on the HTCondor slot configuration."""

from . import display, SLOTS_CONFIGURATION, logger
from .utils import split_num_str, to_minutes, to_binary_gigabyte
import math
import json


def filter_slots(slots: dict, slot_type: str) -> list:
    """Filters the slots stored in a dictionary according to the given type."""
    result = []
    for node in slots:
        for slot in node["slot_size"]:
            if slot["SlotType"] == slot_type:
                slot["UtsnameNodename"] = node["UtsnameNodename"]
                result.append(slot)

    return result


def prepare(cpu: int, gpu: int, ram: str, disk: str, jobs: int,
            job_duration: str, maxnodes: int, verbose: bool,
            config_file: str = SLOTS_CONFIGURATION) -> bool:
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
        config_file: optional, alternative file path for slots configuration

    Returns:
        If all needed parameters were given
    """

    with open(config_file) as f:
        config = json.load(f)['slots']

    slots_static = filter_slots(config, 'static')
    slots_dynamic = filter_slots(config, 'dynamic')
    slots_gpu = filter_slots(config, "gpu")

    [ram, ram_unit] = split_num_str(ram, 0.0, 'GiB')
    ram = to_binary_gigabyte(ram, ram_unit)
    [disk, disk_unit] = split_num_str(disk, 0.0, 'GiB')
    disk = to_binary_gigabyte(disk, disk_unit)

    [job_duration, duration_unit] = split_num_str(job_duration, 0.0, 'min')
    job_duration = to_minutes(job_duration, duration_unit)

    if cpu == 0:
        logger.warning("No number of CPU workers given --- ABORTING")
        return False

    elif ram == 0.0:
        logger.warning("No RAM amount given --- ABORTING")
        return False

    else:
        check_slots(
            slots_static, slots_dynamic, slots_gpu, cpu, ram, disk, gpu, jobs,
            job_duration, maxnodes, verbose
        )
        return True


def check_slots(static: list, dynamic: list, gpu: list, n_cpus: int,
                ram: float, disk_space: float, n_gpus: int,
                n_jobs: int, job_duration: float, max_nodes: int,
                verbose: bool) -> dict:
    """
    Handles the checking for all node/slot types and invokes the output
    methods.

    Args:
        static: A list of static slot configurations
        dynamic: A list of dynamic slot configurations
        gpu: A list of gpu slot configurations
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

    if n_cpus != 0 and n_gpus == 0:
        for node in dynamic:
            node_dict, preview_node = check_slot_by_type(
                slot=node,
                n_cpu=n_cpus,
                ram=ram,
                job_duration=job_duration,
                n_jobs=n_jobs,
                slot_type='dynamic'
            )

            results['slots'].append(node_dict)
            results['preview'].append(preview_node)

        for node in static:
            node_dict, preview_node = check_slot_by_type(
                slot=node,
                n_cpu=n_cpus,
                ram=ram,
                job_duration=job_duration,
                n_jobs=n_jobs,
                slot_type='static'
            )
            results['slots'].append(node_dict)
            results['preview'].append(preview_node)

    elif n_cpus != 0 and n_gpus != 0:
        for node in gpu:
            node_dict, preview_node = check_slot_by_type(
                slot=node,
                n_cpu=n_cpus,
                n_gpu=n_gpus,
                ram=ram,
                job_duration=job_duration,
                n_jobs=n_jobs,
                slot_type='gpu'
            )
            results['slots'].append(node_dict)
            results['preview'].append(preview_node)
    else:
        return {}

    results['preview'] = order_node_preview(results['preview'])

    if max_nodes != 0 and len(results['preview']) > max_nodes:
        results['preview'] = results['preview'][:max_nodes]

    if verbose:
        display.slots(results)

    display.results(results, verbose)

    return results


def default_preview(slot_name: str, slot_type: str) -> dict:
    return {
        'name': slot_name,
        'type': slot_type,
        'fits': 'NO',
        'gpu_usage': '------',
        'core_usage': '------',
        'ram_usage': '------',
        'sim_jobs': '------',
        'wall_time_on_idle': 0
    }


def rename_slot_keys(slot: dict) -> dict:
    renamed = {
        'node': slot["UtsnameNodename"],
        'type': slot["SlotType"],
        'total_slots': slot["TotalSlots"],
        'cores': slot["TotalSlotCpus"],
        'disk': slot["TotalSlotDisk"],
        'ram': slot["TotalSlotMemory"]
    }

    if slot.get('TotalSlotGPUs', None):
        renamed['gpus'] = slot['TotalSlotGPUs']

    return renamed


def check_slot_by_type(slot: dict, n_cpu: int, ram: float,
                       job_duration: float, n_jobs: int, slot_type: str,
                       n_gpu: int = 0) -> (dict, dict):
    """
    Checks all dynamic slots if they fit the job.

    Args:
        slot: The slot to be checked for running the specified job.
        n_cpu: The number of CPU cores for a single job
        ram: The amount of RAM for a single job
        job_duration: The duration for a single job to execute
        n_jobs: The number of similar jobs to be executed
        slot_type: The type of slot, allowed {'static', 'dynamic', 'gpu'}
        n_gpu: Optional. The number of GPU units for a single job

    Returns:
        A dictionary of the checked slot and a dictionary with the occupancy
        details of the slot.
    """
    if slot_type not in ['static', 'dynamic', 'gpu']:
        raise ValueError(f'slot_type must be static, dynamic, or gpu, '
                         f'not {slot_type}')

    preview = default_preview(slot['UtsnameNodename'], slot_type)

    total_cpus = slot['TotalSlotCpus']
    total_ram = slot['TotalSlotMemory']
    total_slots = slot['TotalSlots'] if slot_type == 'static' else 1
    total_gpus = slot['TotalSlotGPUs'] if slot_type == 'gpu' else 0
    pct_cpus = int(round((n_cpu / total_cpus) * 100, 0))
    pct_ram = int(round((ram / total_ram) * 100, 0))
    fits_job = n_cpu <= total_cpus and ram <= total_ram

    if slot_type == 'gpu':
        pct_gpu = int(round((n_gpu / total_gpus) * 100, 0))
        fits_job = fits_job and n_gpu <= total_gpus

        if total_gpus >= 1:
            preview['gpu_usage'] = f'{n_gpu}/{total_gpus} ({pct_gpu})%'
        else:
            preview['gpu_usage'] = 'No GPU resource!'

    preview['core_usage'] = f'{n_cpu}/{total_cpus} ({pct_cpus}%)'
    preview['ram_usage'] = f'{ram:.2f}/{total_ram} GiB ({pct_ram}%)'

    if fits_job:
        preview['fits'] = 'YES'

        if slot_type == 'dynamic':
            preview['sim_jobs'] = min(
                int(total_cpus / n_cpu),
                int(total_ram / ram)
            )
        elif slot_type == 'gpu':
            preview['sim_jobs'] = min(
                int(total_gpus / n_gpu),
                int(total_cpus / n_cpu),
                int(total_ram / ram)
            )
        elif slot_type == 'static':
            preview['sim_jobs'] = total_cpus

        if job_duration != 0:
            cpu_fit = int(total_cpus / n_cpu)
            ram_fit = int(total_ram / ram)

            if slot_type == 'gpu':
                gpu_fit = int(total_gpus / n_gpu)

                if ram == 0:
                    jobs = min(cpu_fit, gpu_fit)
                else:
                    jobs = min(min(cpu_fit, gpu_fit), ram_fit)

                preview['wall_time_on_idle'] = math.ceil(
                    (n_jobs / jobs / total_cpus) * job_duration
                )

            elif slot_type in ['static', 'dynamic']:
                jobs = cpu_fit if ram == 0 else min(cpu_fit, ram_fit)
                preview['wall_time_on_idle'] = math.ceil(
                    (n_jobs / jobs / total_slots) * job_duration
                )

    else:
        preview['fits'] = 'NO'
        preview['sim_jobs'] = 0

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
