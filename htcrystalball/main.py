"""Entry point for HTCrystalBall examination and collection."""

import argparse
import sys

import htcondor

from htcrystalball import __version__, examine
from htcrystalball.utils import validate_storage_size, validate_duration


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
        '%(prog)s peek -c CPU -r RAM [-g GPU] [-d DISK] [-j JOBS] '
        '[-t JOB_DURATION] [-m MAX_NODES] [-v]'
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
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%s' % __version__
    )

    # Sub command (peek)
    subcommands = parser.add_subparsers(
        title="htcrystalball commands",
        description="Entry points for htcrystalball"
    )
    peek_cmd = subcommands.add_parser(
        'peek',
        help='Peek into the crystal ball to see the future'
    )
    peek_cmd.set_defaults(run=peek)
    peek_cmd.add_argument(
        "-v", "--verbose",
        help="Print extended log to stdout",
        action='store_true',
        dest='verbose'
    )
    peek_cmd.add_argument(
        "-c", "--cpu",
        help="Set number of requested CPU Cores",
        type=int,
        required=True,
        default=0,
        dest='cpu'
    )
    peek_cmd.add_argument(
        "-g", "--gpu",
        help="Set number of requested GPU Units",
        type=int,
        default=0,
        dest='gpu'
    )
    peek_cmd.add_argument(
        "-j", "--jobs",
        help="Set number of jobs to be executed",
        type=int,
        default=1,
        dest='jobs'
    )
    peek_cmd.add_argument(
        "-t", "--time",
        help="Set the duration for one job to be executed",
        type=validate_duration,
        dest='time'
    )
    peek_cmd.add_argument(
        "-d", "--disk",
        help="Set amount of requested disk storage",
        type=validate_storage_size,
        dest='disk'
    )
    peek_cmd.add_argument(
        "-r", "--ram",
        help="Set amount of requested memory storage",
        type=validate_storage_size,
        required=True,
        dest='ram'
    )
    peek_cmd.add_argument(
        "-m", "--maxnodes",
        help="Set maximum of nodes to run jobs on",
        type=int,
        default=0,
        dest='maxnodes'
    )

    # Sub command (configure)
    configure_cmd = subcommands.add_parser(
        'configure',
        help='Generate a slots configuration file for the current system'
    )
    configure_cmd.set_defaults(run=configure)

    # Parse arguments
    args = parser.parse_args()

    if len(sys.argv) <= 1:
        parser.print_help()
    else:
        args.run(args, parsers=[peek_cmd, configure_cmd])


def peek(params, parsers):
    """Peek into the crystal ball to see the future."""
    query_data = ["SlotType", "UtsnameNodename", "TotalSlotCpus", "TotalSlotDisk", "TotalSlotMemory", "TotalSlots",
                  "TotalSlotGPUs"]
    coll = htcondor.Collector()
    # Ignore dynamic slots, which are the ephemeral children of partitionable slots, and thus noise.
    # Partitionable slot definitions remain unaltered by the process of dynamic slot creation.
    content = coll.query(htcondor.AdTypes.Startd, constraint='SlotType != "Dynamic"', projection=query_data)

    examine.prepare(
        cpu=params.cpu, gpu=params.gpu, ram=params.ram, disk=params.disk,
        jobs=params.jobs, job_duration=params.time, maxnodes=params.maxnodes,
        verbose=params.verbose, content=content)
    sys.exit(0)


def configure(params, parsers):
    print('Not yet implemented')
    sys.exit(0)
