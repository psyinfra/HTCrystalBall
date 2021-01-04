"""Entry point for HTCrystalBall examination and collection."""

import argparse
import sys

import htcondor

from htcrystalball import examine
from htcrystalball.utils import validate_storage_size, validate_duration

QUERY_DATA = ["SlotType", "Machine", "TotalSlotCpus", "TotalSlotDisk",
              "TotalSlotMemory", "TotalSlotGPUs"]


def main() -> None:
    """
    Defines the command line parser and argument properties
    """
    description = (
        '%(prog)s - A crystal ball that lets you peek into the future. '
        'To get a preview for any job you are trying ot execute using '
        'HTCondor, please pass at least the number of CPUs and the amount of '
        'RAM including units (e.g. 100MB, 90M, 10GB, 15g) according to the '
        'usage example shown above. For JOB duration please use d, h, m, or s'
    )
    usage = (
        '%(prog)s -c CPU -r RAM [-g GPU] [-d DISK] [-j JOBS] '
        '[-t TIME] [-m MAX_NODES] [-v]'
    )
    epilog = (
        'PLEASE NOTE: HTCondor always uses binary storage sizes (1 GiB = '
        '1024 MiB, 1 GB = 1000 MB), so inputs will automatically be treated '
        'that way.'
    )

    # Main command
    parser = argparse.ArgumentParser(
        prog='htcrystalball',
        description=description,
        usage=usage,
        epilog=epilog
    )

    parser.set_defaults(run=peek)

    parser.add_argument(
        "-v", "--verbose",
        help="Print extended log to stdout",
        action='store_true',
        dest='verbose'
    )
    parser.add_argument(
        "-c", "--cpu",
        help="Set number of requested CPU Cores",
        type=int,
        required=True,
        default=0,
        dest='cpu'
    )
    parser.add_argument(
        "-g", "--gpu",
        help="Set number of requested GPU Units",
        type=int,
        default=0,
        dest='gpu'
    )
    parser.add_argument(
        "-j", "--jobs",
        help="Set number of jobs to be executed",
        type=int,
        default=1,
        dest='jobs'
    )
    parser.add_argument(
        "-t", "--time",
        help="Set the duration for one job to be executed",
        type=validate_duration,
        dest='time'
    )
    parser.add_argument(
        "-d", "--disk",
        help="Set amount of requested disk storage",
        type=validate_storage_size,
        dest='disk'
    )
    parser.add_argument(
        "-r", "--ram",
        help="Set amount of requested memory storage",
        type=validate_storage_size,
        required=True,
        dest='ram'
    )
    parser.add_argument(
        "-m", "--maxnodes",
        help="Set maximum of nodes to run jobs on",
        type=int,
        default=0,
        dest='maxnodes'
    )

    # Parse arguments
    args = parser.parse_args()

    if len(sys.argv) <= 1:
        parser.print_help()
    else:
        args.run(args, parsers=[parser])


def peek(params, parsers):
    """Peek into the crystal ball to see the future."""

    coll = htcondor.Collector()
    # Ignore dynamic slots, which are the ephemeral children of partitionable slots, and thus noise.
    # Partitionable slot definitions remain unaltered by the process of dynamic slot creation.
    content = coll.query(htcondor.AdTypes.Startd,
                         constraint='SlotType != "Dynamic"', projection=QUERY_DATA)

    examine.prepare(
        cpu=params.cpu, gpu=params.gpu, ram=params.ram, disk=params.disk,
        jobs=params.jobs, job_duration=params.time, maxnodes=params.maxnodes,
        verbose=params.verbose, content=content)
    sys.exit(0)
