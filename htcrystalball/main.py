"""Entry point for HTCrystalBall examination and collection."""

import argparse
import sys

import htcondor

from htcrystalball import examine, LOGGER
from htcrystalball.utils import validate_storage_size, validate_duration

QUERY_DATA = ["SlotType", "Machine", "TotalSlotCpus", "TotalSlotDisk",
              "TotalSlotMemory", "TotalSlotGPUs"]


def main() -> None:
    """
    Defines the command line parser and argument properties
    """
    description = (
        '%(prog)s - calculates how many jobs (of a user‐specified number and '
        'size) can run on an HTCondor pool. It also can estimate runtime (core '
        'hours and wall time) and node‐specific matching (aiding those with '
        'node‐level licensing restrictions).'
    )
    usage = (
        '%(prog)s -c CPU -r RAM [-g GPU] [-d DISK] [-j JOBS] '
        '[-t TIME] [-m MAX_NODES] [-v]'
    )

    # Main command
    parser = argparse.ArgumentParser(
        prog='htcrystalball',
        description=description,
        usage=usage
    )

    parser.set_defaults(run=peek)

    parser.add_argument(
        "-c", "--cpu",
        help="The number of CPU cores per job.",
        type=int,
        default=0,
        dest='cpu'
    )
    parser.add_argument(
        "-r", "--ram",
        help="The amount of RAM per job, including a unit (e.g. 10G).",
        type=validate_storage_size,
        dest='ram'
    )
    parser.add_argument(
        "-g", "--gpu",
        help="The number of GPUs per job.",
        type=int,
        default=0,
        dest='gpu'
    )
    parser.add_argument(
        "-d", "--disk",
        help="The disk space per job, including a unit (e.g. 50G).",
        type=validate_storage_size,
        dest='disk'
    )
    parser.add_argument(
        "-j", "--jobs",
        help="The number of jobs to be executed.",
        type=int,
        default=1,
        dest='jobs'
    )
    parser.add_argument(
        "-t", "--time",
        help="The estimated time for one job to be executed, including a unit (e.g. 1h).",
        type=validate_duration,
        dest='time'
    )
    parser.add_argument(
        "-m", "--maxnodes",
        help="The maximum number of nodes jobs can be executed on. Sometimes necessary due to software license restrictions.",
        type=int,
        default=0,
        dest='maxnodes'
    )
    parser.add_argument(
        "-f", "--file",
        help="A path to an htcondor .submit-file. Results in not having to provide additional hardware parameters.",
        type=str,
        default=0,
        dest='file'
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Prints a table listing each node, its resources, and proposed usage.",
        action='store_true',
        dest='verbose'
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
    try:
        content = coll.query(htcondor.AdTypes.Startd,
                             constraint='SlotType != "Dynamic"', projection=QUERY_DATA)
    except htcondor.HTCondorLocateError as e:
        LOGGER.error(str(e)+"\n You seem to run HTCrystalBall on a system that has no htcondor pool.\n"
                            "For information about htcondor pools, you can go to\n"
                            "https://htcondor.readthedocs.io/en/latest/admin-manual/introduction-admin-manual.html")
        sys.exit(0)

    examine.prepare(
        cpu=params.cpu, gpu=params.gpu, ram=params.ram, disk=params.disk,
        jobs=params.jobs, job_duration=params.time, maxnodes=params.maxnodes, file=params.file,
        verbose=params.verbose, content=content)
    sys.exit(0)
