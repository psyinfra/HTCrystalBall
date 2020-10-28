# HTCrystalBall

[![Build Status](https://travis-ci.org/psyinfra/HTCrystalBall.svg?branch=master)](https://travis-ci.org/psyinfra/HTCrystalBall)
[![codecov](https://codecov.io/gh/psyinfra/HTCrystalBall/branch/master/graph/badge.svg)](https://codecov.io/gh/psyinfra/HTCrystalBall)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/a3f2efd33ff14ab9af91e5a367b6d0ff)](https://www.codacy.com/gh/psyinfra/HTCrystalBall?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=psyinfra/HTCrystalBall&amp;utm_campaign=Badge_Grade)

A crystal ball, that lets you peer into the future.

## Overview
First, if you are familiar with this README or just want to skip sections, 
here is a list of hyperlinks for you to skip searching for a particular section:

*   [Description](#Description)
*   [Requirements](#Requirements)
*   [Installation](#Installation-and-Configuration)
*   [Input](#INPUT)
*   [Output](#OUTPUT)
*   [Examples](#Examples)
*   [Testing](#Testing)

## Description
This project contains of two main parts
*   fetching an HTCondor slot configuration to create a list of slots

*   looking for suiting slots in the given configuration to execute user-defined
jobs a.k.a. the `crystal ball`

and is intended for HTCondor (server) systems which describe resources as slots
rather than nodes. 

Fetching the slots uses the `condor_status` command to get necessary
information about the various slots. In our particular use-case we went for the `-long` 
option that gives us way too much information but at least all the information we need. 
As each line of the command output follows the pattern `key = value` we chose to parse
it that way and only store the key-value pairs for

*   UtsnameNodename
*   TotalSlots
*   Name
*   TotalSlotCpus
*   TotalSlotDisk
*   TotalSlotMemory
*   TotalSlotGPUs
*   SlotType

So if you want to adjust this script to your use-case feel free to add other keys.

As it turns out, the resulting list of slots had more than 500 entries because every single slot (static and dynamic created ones)
would be displayed. But as we don't need every single slot of identical configuration, 
we chose to filter them out to show all available slot configurations and just keep the
`TotalSlots` property to reflect that there are multiple slots of the same configuration.
To also account for the relation to a `node`, we chose to go with a node object in JSON that 
has various `slot` sizes as children objects. Here you can see an example for a `node` object in JSON:
    
    {
        "node": "cpuXX", 
        "slot_size": [
            {"cores": 2, "disk": 51.53, "ram": 30.0, "type": "partitionable", "total_slots": 11},
            {"cores": 1, "disk": 3.46, "ram": 5.88, "type": "static", "total_slots": 11}
        ]
    }

Here comes our `crystal ball` to play its part. The script takes a user input of requested 
ressources for a single job and checks whether and how it fits into the given slots. 
If the user provides a parameter for the number of similar `jobs` to be executed and 
the execution time per job, a total `wall time` can also be calculated per `slot`.

## Requirements
`HTCrystalBall` uses the `rich` module for printing out nicely formatted tables. 
The module requires Python 3.6+ to run.
For using the HTCondor API the module `htcondor` has to be installed.

To also run our tests, we require `pytest` to be installed.

## Installation and Configuration
To install and configure `HTCrystalBall` please follow these steps:

1.  clone this repo to the file system of any machine in your HTCondor cluster
    
    `git clone https://github.com/psyinfra/HTCrystalBall.git`

2.  `cd` into the newly created directory and install python modules using the setup.py

    `cd HTCrystalBall`

    `pip3 install .`

3.  adjust the keys to be fetched from the command in `collect.py`

    `if key in ("SlotType", "UtsnameNodename", "Name", "TotalSlotCpus", "TotalSlotDisk", "TotalSlotMemory", "TotalSlots", "TotalSlotGPUs"):`

## INPUT

To use our `crystal ball` your input has to provide at least CPU and RAM requirements 
while also giving you the ability to pass values familiar parameter you already know from
writing a [condor submit](https://htcondor.readthedocs.io/en/latest/users-manual/submitting-a-job.html) file:

    htcrystalball | htcb -h
    
    usage: htcrystalball | htcb -c CPU -r RAM [-g GPU] [-d DISK] [-j JOBS] [-d DURATION] [-v]

    To get a preview for any job you are trying to execute using HTCondor, please
    pass at least the number of CPUs and the amount of RAM (including units eg.
    100MB, 90M, 10GB, 15G) to this script according to the usage example shown
    above. For JOB Duration please use d, h, m or s
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         Print extended log to stdout
      -c CPU, --cpu CPU     Set number of requested CPU Cores
      -g GPU, --gpu GPU     Set number of requested GPU Units
      -j JOBS, --jobs JOBS  Set number of jobs to be executed
      -t TIME, --time TIME  Set the duration for one job to be executed
      -d DISK, --disk DISK  Set amount of requested disk storage
      -r RAM, --ram RAM     Set amount of requested memory storage
      -m MAXNODES, --maxnodes  Set maximum of nodes to run jobs on
    
    PLEASE NOTE: HTCondor always uses binary storage sizes, so inputs will
    automatically be treated that way.

## OUTPUT
### Basic Output
Our `crystal ball` will give you a brief summary of the executed slot checking for your jobs like this:

|   Slot Type   | Job fits | Amount of similar jobs | Wall Time on Idle |
| ------------- | -------- | ---------------------- | ----------------- |
|      gpu      |   ....   |          ....          |       0 min       |
|    static     |   ....   |          ....          |       0 min       |
| partitionable |   ....   |          ....          |       0 min       |

*   Job fits: If one job fits into a slot it will be highlighted in green color, if not in red.
*   Amount of similar jobs: number of jobs similar to the one defined, that fit into a slot the same time.
*   Wall time on Idle: Theoretical execution time for all similar jobs to be executed on a slot.

### Advanced Output
When using VERBOSE HTCrystalBall will print out your given Input...

|   Parameter   | Input Value |
| ------------- |  ---------  |
|     CPUS      |     ...     |
|      RAM      |     ...     |
|    STORAGE    |     ...     |
|     GPUS      |     ...     |
|     JOBS      |     ...     |
| JOB DURATION  |     ...     |
| MAXIMUM NODES |     ...     |

...the current slot configuration of the cluster...

| Node |   Slot Type   | Total slots | Cores | GPUs | RAM | DISK |
| ---- | ------------- | ----------- | ----- | ---- | --- | ---- |
| Name |      gpu      |     ...     |  ...  | ...  | ... | ...  |
| Name |     static    |     ...     |  ...  | ...  | ... | ...  |
| Name | partitionable |     ...     |  ...  | ...  | ... | ...  |

...and a more detailed summary of the slot checking:

| Node |   Slot Type   | Job fits | Slot usage | RAM usage | GPU usage | Amount of similar jobs | Wall Time on Idle |
| ---- | ------------- | -------- | ---------- | --------- | --------- | ---------------------- | ----------------- |
| Name |      gpu      |   YES    | ... (x %)  | ... (x %) | ... (x %) |           ...          |      ... min      |
| Name |     static    |    NO    | ... (x %)  | ... (x %) | ... (x %) |           ...          |      ... min      |
| Name | partitionable |    NO    | ... (x %)  | ... (x %) | ... (x %) |           ...          |      ... min      |

### Examples
htcb peek -c 2 -r 10G -g 2

    ---------------------- PREVIEW ----------------------
    ┏━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
    ┃ Slot Type ┃ Job fits ┃ Amount of similar jobs ┃ Wall Time on IDLE ┃
    ┡━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
    │ gpu       │      YES │                      2 │             0 min │
    └───────────┴──────────┴────────────────────────┴───────────────────┘

htcb peek -c 2 -r 10G -g 2 -v

    ---------------------- INPUT ----------------------
    ┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
    ┃ Parameter     ┃ Input Value ┃
    ┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
    │ CPUS          │           2 │
    │ RAM           │   10.00 GiB │
    │ STORAGE       │    0.00 GiB │
    │ GPUS          │           2 │
    │ JOBS          │           1 │
    │ JOB DURATION  │    0.00 min │
    │ MAXIMUM NODES │           0 │
    └───────────────┴─────────────┘
    ---------------------- NODES ----------------------
    ┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
    ┃ Node         ┃ Slot Type ┃ Total Slots ┃ Cores ┃ GPUs ┃        RAM ┃       DISK ┃
    ┡━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
    │ gpu1         │ gpu       │          22 │    10 │    4 │ 180.76 GiB │ 1618.1 GiB │
    └──────────────┴───────────┴─────────────┴───────┴──────┴────────────┴────────────┘
    ---------------------- PREVIEW ----------------------
    ┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
    ┃ Node         ┃ Slot Type ┃ Job fits ┃       Slot usage ┃       RAM usage       ┃ GPU usage ┃ Amount of similar jobs ┃ Wall Time on IDLE ┃
    ┡━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
    │ gpu1         │ gpu       │      YES │ 2/10 (20%) Cores │ 10.00/180.76 GiB (6%) │ 2/4 (50)% │                      2 │             0 min │
    └──────────────┴───────────┴──────────┴──────────────────┴───────────────────────┴───────────┴────────────────────────┴───────────────────┘

htcb peek -c 5 -r 10G

    ---------------------- PREVIEW ----------------------
    ┏━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
    ┃ Slot Type     ┃ Job fits ┃ Amount of similar jobs ┃ Wall Time on IDLE ┃
    ┡━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
    │ partitionable │      YES │                     12 │             0 min │
    │ partitionable │      YES │                     12 │             0 min │
    │ partitionable │      YES │                      6 │             0 min │
    │ partitionable │      YES │                      6 │             0 min │
    │ partitionable │      YES │                      4 │             0 min │
    │ partitionable │      YES │                      4 │             0 min │
    │ partitionable │      YES │                      4 │             0 min │
    │ partitionable │      YES │                      4 │             0 min │
    │ partitionable │      YES │                      4 │             0 min │
    │ partitionable │      YES │                      4 │             0 min │
    │ partitionable │      YES │                      2 │             0 min │
    │ partitionable │      YES │                      2 │             0 min │
    │ partitionable │      YES │                      2 │             0 min │
    │ partitionable │      YES │                      2 │             0 min │
    │ partitionable │      YES │                      2 │             0 min │
    │ partitionable │      YES │                      2 │             0 min │
    │ partitionable │      YES │                      2 │             0 min │
    │ partitionable │       NO │                      0 │             0 min │
    │ static        │       NO │                      0 │             0 min │
    │ static        │       NO │                      0 │             0 min │
    │ static        │       NO │                      0 │             0 min │
    │ static        │       NO │                      0 │             0 min │
    │ static        │       NO │                      0 │             0 min │
    └───────────────┴──────────┴────────────────────────┴───────────────────┘
    
htcb peek -c 5 -r 10G  -v

    ---------------------- INPUT ----------------------
    ┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
    ┃ Parameter     ┃ Input Value ┃
    ┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
    │ CPUS          │           5 │
    │ RAM           │   10.00 GiB │
    │ STORAGE       │    0.00 GiB │
    │ GPUS          │           0 │
    │ JOBS          │           1 │
    │ JOB DURATION  │    0.00 min │
    │ MAXIMUM NODES │           0 │
    └───────────────┴─────────────┘
    ---------------------- NODES ----------------------
    ┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┓
    ┃ Node         ┃ Slot Type     ┃ Total Slots ┃ Cores ┃   GPUs ┃       RAM ┃        DISK ┃
    ┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━┩
    │ cpu22        │ partitionable │          33 │    32 │ ------ │ 500.0 GiB │ 3504.21 GiB │
    │ cpu14        │ partitionable │          25 │    24 │ ------ │ 210.0 GiB │ 3414.28 GiB │
    │ cpu1         │ partitionable │          25 │    24 │ ------ │ 210.0 GiB │ 3414.49 GiB │
    │ cpu15        │ partitionable │          25 │    24 │ ------ │ 210.0 GiB │ 3414.23 GiB │
    │ cpu2         │ partitionable │          13 │    12 │ ------ │  65.0 GiB │ 3416.16 GiB │
    │ cpu13        │ partitionable │          12 │     2 │ ------ │  30.0 GiB │  829.54 GiB │
    │ cpu16        │ partitionable │          16 │    20 │ ------ │ 120.0 GiB │ 3416.09 GiB │
    │ cpu3         │ partitionable │          13 │    12 │ ------ │  65.0 GiB │ 3415.78 GiB │
    │ cpu17        │ partitionable │          16 │    20 │ ------ │ 120.0 GiB │ 3416.06 GiB │
    │ cpu4         │ partitionable │          13 │    12 │ ------ │  65.0 GiB │  3416.2 GiB │
    │ cpu5         │ partitionable │          13 │    12 │ ------ │  65.0 GiB │ 3414.52 GiB │
    │ cpu18        │ partitionable │          16 │    20 │ ------ │ 120.0 GiB │ 3416.12 GiB │
    │ cpu6         │ partitionable │          13 │    12 │ ------ │  65.0 GiB │ 3416.14 GiB │
    │ cpu7         │ partitionable │          13 │    12 │ ------ │  65.0 GiB │ 3416.14 GiB │
    │ cpu8         │ partitionable │          13 │    12 │ ------ │  65.0 GiB │ 3416.14 GiB │
    │ cpu9         │ partitionable │          65 │    64 │ ------ │ 500.0 GiB │ 3414.53 GiB │
    │ cpu10        │ partitionable │          65 │    64 │ ------ │ 500.0 GiB │ 3416.04 GiB │
    │ cpu21        │ partitionable │          33 │    32 │ ------ │ 500.0 GiB │ 3500.75 GiB │
    │ cpu23        │ static        │          32 │     1 │ ------ │  15.0 GiB │  110.56 GiB │
    │ cpu11        │ static        │          64 │     1 │ ------ │   7.5 GiB │   56.15 GiB │
    │ cpu24        │ static        │          32 │     1 │ ------ │  15.0 GiB │  110.56 GiB │
    │ cpu12        │ static        │          64 │     1 │ ------ │   7.5 GiB │   56.19 GiB │
    │ cpu19        │ static        │          16 │     1 │ ------ │   9.0 GiB │  215.76 GiB │
    └──────────────┴───────────────┴─────────────┴───────┴────────┴───────────┴─────────────┘
    ---------------------- PREVIEW ----------------------
    ┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
    ┃ Node         ┃ Slot Type     ┃ Job fits ┃       Slot usage ┃      RAM usage       ┃ GPU usage ┃ Amount of similar jobs ┃ Wall Time on IDLE ┃
    ┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
    │ cpu9         │ partitionable │      YES │  5/64 (8%) Cores │ 10.00/500.0 GiB (2%) │  ------   │                     12 │             0 min │
    │ cpu10        │ partitionable │      YES │  5/64 (8%) Cores │ 10.00/500.0 GiB (2%) │  ------   │                     12 │             0 min │
    │ cpu22        │ partitionable │      YES │ 5/32 (16%) Cores │ 10.00/500.0 GiB (2%) │  ------   │                      6 │             0 min │
    │ cpu21        │ partitionable │      YES │ 5/32 (16%) Cores │ 10.00/500.0 GiB (2%) │  ------   │                      6 │             0 min │
    │ cpu14        │ partitionable │      YES │ 5/24 (21%) Cores │ 10.00/210.0 GiB (5%) │  ------   │                      4 │             0 min │
    │ cpu1         │ partitionable │      YES │ 5/24 (21%) Cores │ 10.00/210.0 GiB (5%) │  ------   │                      4 │             0 min │
    │ cpu15        │ partitionable │      YES │ 5/24 (21%) Cores │ 10.00/210.0 GiB (5%) │  ------   │                      4 │             0 min │
    │ cpu16        │ partitionable │      YES │ 5/20 (25%) Cores │ 10.00/120.0 GiB (8%) │  ------   │                      4 │             0 min │
    │ cpu17        │ partitionable │      YES │ 5/20 (25%) Cores │ 10.00/120.0 GiB (8%) │  ------   │                      4 │             0 min │
    │ cpu18        │ partitionable │      YES │ 5/20 (25%) Cores │ 10.00/120.0 GiB (8%) │  ------   │                      4 │             0 min │
    │ cpu2         │ partitionable │      YES │ 5/12 (42%) Cores │ 10.00/65.0 GiB (15%) │  ------   │                      2 │             0 min │
    │ cpu3         │ partitionable │      YES │ 5/12 (42%) Cores │ 10.00/65.0 GiB (15%) │  ------   │                      2 │             0 min │
    │ cpu4         │ partitionable │      YES │ 5/12 (42%) Cores │ 10.00/65.0 GiB (15%) │  ------   │                      2 │             0 min │
    │ cpu5         │ partitionable │      YES │ 5/12 (42%) Cores │ 10.00/65.0 GiB (15%) │  ------   │                      2 │             0 min │
    │ cpu6         │ partitionable │      YES │ 5/12 (42%) Cores │ 10.00/65.0 GiB (15%) │  ------   │                      2 │             0 min │
    │ cpu7         │ partitionable │      YES │ 5/12 (42%) Cores │ 10.00/65.0 GiB (15%) │  ------   │                      2 │             0 min │
    │ cpu8         │ partitionable │      YES │ 5/12 (42%) Cores │ 10.00/65.0 GiB (15%) │  ------   │                      2 │             0 min │
    │ cpu13        │ partitionable │       NO │ 5/2 (250%) Cores │ 10.00/30.0 GiB (33%) │  ------   │                      0 │             0 min │
    │ cpu23        │ static        │       NO │ 5/1 (500%) Cores │ 10.00/15.0 GiB (67%) │  ------   │                      0 │             0 min │
    │ cpu11        │ static        │       NO │ 5/1 (500%) Cores │ 10.00/7.5 GiB (133%) │  ------   │                      0 │             0 min │
    │ cpu24        │ static        │       NO │ 5/1 (500%) Cores │ 10.00/15.0 GiB (67%) │  ------   │                      0 │             0 min │
    │ cpu12        │ static        │       NO │ 5/1 (500%) Cores │ 10.00/7.5 GiB (133%) │  ------   │                      0 │             0 min │
    │ cpu19        │ static        │       NO │ 5/1 (500%) Cores │ 10.00/9.0 GiB (111%) │  ------   │                      0 │             0 min │
    └──────────────┴───────────────┴──────────┴──────────────────┴──────────────────────┴───────────┴────────────────────────┴───────────────────┘

## Testing
Make sure you have the necessary python modules:

`pip3 install pytest`

Run the following command to execute your test:

`python3 -m pytest -q tests/test_me.py`
