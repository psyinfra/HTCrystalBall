# HTCrystalBall

[![Build Status](https://travis-ci.org/psyinfra/HTCrystalBall.svg?branch=master)](https://travis-ci.org/psyinfra/HTCrystalBall)
[![codecov](https://codecov.io/gh/psyinfra/HTCrystalBall/branch/master/graph/badge.svg)](https://codecov.io/gh/psyinfra/HTCrystalBall)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/a3f2efd33ff14ab9af91e5a367b6d0ff)](https://www.codacy.com/gh/psyinfra/HTCrystalBall?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=psyinfra/HTCrystalBall&amp;utm_campaign=Badge_Grade)

**HTCrystalBall** calculates the runtime and maximum number of jobs that can run
on an [HTCondor](https://research.cs.wisc.edu/htcondor/) pool. It queries a
live HTCondor pool to determine the available resources.

HTCrystalBall is designed for both new and experienced users. Its primary
use-cases are:

* A quick calculator to estimate the core-hours and wall-time of a job-cluster
  on a pool.

* An educational tool to help those new to job schedulers better understand
  the concept of throughput and how jobs, job-sizes, and slots match.

* When only a fixed number of compute nodes should be used (for example:
  floating software license restrictions), the `--maxnodes` flag presents a
  list of nodes that enable the highest job throughput while remaining withing
  the node-budget.

## Installation

**NOTE:** HTCrystalBall requires Python 3.6 or greater.

**NOTE:** Querying a live HTCondor pool requires the `htcondor` Python module
which (currently) only runs on Linux.

This software can be installed directly from GitHub.
```shell
pip3 install git+https://github.com/psyinfra/HTCrystalBall.git
```

The use of virtual environments is highly encouraged. If you are not already
familiar with
[Python virtual environments](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/),
we recommend that you read up on them.

### Optional configuration

If you want to include or exclude `condor_status` attributes to be fetched from
the HTCondor pool, you can adjust the parameter `QUERY_DATA` in `main.py`; it
is a list of strings that represent the keys of the attributes. For example:

```python
QUERY_DATA = ["SlotType", "Machine", "TotalSlotCpus", "TotalSlotDisk", "TotalSlotMemory", "TotalSlotGPUs"]
```

## Usage

```
usage: htcrystalball -c CPU -r RAM [-g GPU] [-d DISK] [-j JOBS] [-t TIME] [-m MAX_NODES] [-f FILE] [-v]

htcrystalball - calculates how many jobs (of a user‐specified number and size)
can run on an HTCondor pool. It also can estimate runtime (core hours and wall
time) and node‐specific matching (aiding those with node‐level licensing
restrictions).

optional arguments:
  -h, --help            show this help message and exit
  -c CPU, --cpu CPU     The number of CPU cores per job.
  -r RAM, --ram RAM     The amount of RAM per job, including a unit (e.g.
                        10G).
  -g GPU, --gpu GPU     The number of GPUs per job.
  -d DISK, --disk DISK  The disk space per job, including a unit (e.g. 50G).
  -j JOBS, --jobs JOBS  The number of jobs to be executed.
  -t TIME, --time TIME  The estimated time for one job to be executed,
                        including a unit (e.g. 1h).
  -m MAXNODES, --maxnodes MAXNODES
                        The maximum number of nodes where jobs can be executed on.
                        Sometimes necessary due to software license
                        restrictions.
  -f FILE, --file FILE  A path to an htcondor .submit-file. Uses parsed requirements instead of typed hardware
                        requirements for CPU, GPU, RAM and DISK.
  -v, --verbose         Prints a table listing each node, its resources, and
                        proposed usage.
```

  **NOTE**

    If a path to an `HTCondor` submit-file is provided in `--file`, `htcrystalball` will parse the file and
    use the resource parameters provided by the file instead of typed parameters. Until now the parameters that can be replaced by parsed ones
    are `CPU`, `GPU`, `RAM` and `DISK`.

## Examples

### Basic Output

HTCrystalBall at its simplest.
```
$ htcb --cpu 1 --ram 7500M --jobs 1

632 jobs of this size can run on this pool.

No --jobs or --time specified. No duration estimate will be given.

The above number(s) are for an idle pool.
```

### Verbose
The `--verbose` flag will list each node, its resources, and proposed usage.

```
$ htcb --cpu 1 --ram 7500M --jobs 1 --verbose

 Jobs ┃       Node        ┃  Slot ┃  CPUs ┃      RAM      ┃     Disk     ┃ GPUs
━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━
   24 │ cpu1.htc.test.com  │     1 │ 24/24 │ 180.0/210.0G  │ 0.0/3416.06G │ 0/0
    8 │ cpu2.htc.test.com  │     1 │  8/12 │  60.0/65.0G   │ 0.0/3416.16G │ 0/0
    8 │ cpu3.htc.test.com  │     1 │  8/12 │  60.0/65.0G   │ 0.0/3415.78G │ 0/0
    8 │ cpu4.htc.test.com  │     1 │  8/12 │  60.0/65.0G   │ 0.0/3416.2G  │ 0/0
    8 │ cpu5.htc.test.com  │     1 │  8/12 │  60.0/65.0G   │ 0.0/3414.71G │ 0/0
    8 │ cpu6.htc.test.com  │     1 │  8/12 │  60.0/65.0G   │ 0.0/3416.14G │ 0/0
    8 │ cpu7.htc.test.com  │     1 │  8/12 │  60.0/65.0G   │ 0.0/3415.3G  │ 0/0
    8 │ cpu8.htc.test.com  │     1 │  8/12 │  60.0/65.0G   │ 0.0/3413.49G │ 0/0
   64 │ cpu9.htc.test.com  │     1 │ 64/64 │ 480.0/500.0G  │ 0.0/3413.33G │ 0/0
   64 │ cpu10.htc.test.com │     1 │ 64/64 │ 480.0/500.0G  │ 0.0/3415.93G │ 0/0
   64 │ cpu11.htc.test.com │ 1..64 │   1/1 │   7.5/7.5G    │  0.0/56.19G  │ 0/0
   64 │ cpu12.htc.test.com │ 1..64 │   1/1 │   7.5/7.5G    │  0.0/56.15G  │ 0/0
    8 │ cpu13.htc.test.com │  1..4 │   2/2 │  15.0/30.0G   │ 0.0/828.74G  │ 0/0
   24 │ cpu14.htc.test.com │     1 │ 24/24 │ 180.0/210.0G  │ 0.0/3416.1G  │ 0/0
   24 │ cpu15.htc.test.com │     1 │ 24/24 │ 180.0/210.0G  │ 0.0/3416.1G  │ 0/0
   16 │ cpu16.htc.test.com │     1 │ 16/20 │ 120.0/120.0G  │ 0.0/3416.09G │ 0/0
   16 │ cpu17.htc.test.com │     1 │ 16/20 │ 120.0/120.0G  │ 0.0/3415.32G │ 0/0
   16 │ cpu18.htc.test.com │     1 │ 16/20 │ 120.0/120.0G  │ 0.0/3416.12G │ 0/0
   16 │ cpu19.htc.test.com │ 1..16 │   1/1 │   7.5/9.0G    │ 0.0/215.76G  │ 0/0
   32 │ cpu21.htc.test.com │     1 │ 32/32 │ 240.0/500.0G  │ 0.0/3504.16G │ 0/0
   32 │ cpu22.htc.test.com │     1 │ 32/32 │ 240.0/500.0G  │ 0.0/3504.21G │ 0/0
   32 │ cpu23.htc.test.com │ 1..32 │   1/1 │   7.5/15.0G   │ 0.0/110.67G  │ 0/0
   32 │ cpu24.htc.test.com │ 1..32 │   1/1 │   7.5/15.0G   │ 0.0/110.67G  │ 0/0
   28 │ cpu25.htc.test.com │     1 │ 28/28 │ 210.0/244.14G │  0.0/138.8G  │ 0/0
   20 │ gpu1.htc.test.com  │  1..2 │ 10/10 │ 75.0/180.76G  │ 0.0/1613.9G  │ 0/4
                              Prediction per node
LEGEND:
█ (<= 90%); █ (90-100%); █ (> 100%)

TOTAL MATCHES: 632

No --jobs or --time specified. No duration estimate will be given.

The above number(s) are for an idle pool.
```

### Big job with runtime projection
```
$ htcb --cpu 16 --ram 16G --disk 100G --jobs 20 --time 5h

19 jobs of this size can run on this pool.

A total of 1600 core-hour(s) will be used and 20 job(s) will complete in about 10 hour(s).

The above number(s) are for an idle pool.
```

## Limit to a maximum number of nodes

```
$ htcb --cpu 16 --ram 16G --disk 100G --maxnodes 2 --jobs 20 --time 5h

A maximum of 8 jobs of this size can run using only 2 nodes.

The following nodes are suggested:
cpu9.htc.inm7.de
cpu10.htc.inm7.de

A total of 1600 core-hour(s) will be used and 20 job(s) will complete in about 15 hour(s).

The above number(s) are for an idle pool.
```

## Limit to a maximum number of nodes (verbose)

```
$ htcb --cpu 16 --ram 16G --disk 100G --maxnodes 2 --verbose

 Jobs ┃       Node        ┃ Slot ┃  CPUs ┃     RAM     ┃      Disk      ┃ GPUs
━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━
    4 │ cpu9.htc.inm7.de  │    1 │ 64/64 │ 64.0/500.0G │ 400.0/3412.41G │ 0/0
    4 │ cpu10.htc.inm7.de │    1 │ 64/64 │ 64.0/500.0G │ 400.0/3415.17G │ 0/0
                              Prediction per node
LEGEND:
█ (<= 90%); █ (90-100%); █ (> 100%)

TOTAL MATCHES: 8

No --jobs or --time specified. No duration estimate will be given.

The above number(s) are for an idle pool.
```

## Testing
To run the tests, make sure you have the following python modules installed:

```
pip3 install pytest natsort testfixtures
```

Run the following command to execute your test:

```
python3 -m pytest -q tests/test_me.py
```
