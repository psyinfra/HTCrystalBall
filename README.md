# HTCrystalBall

[![Build Status](https://travis-ci.org/psyinfra/HTCrystalBall.svg?branch=master)](https://travis-ci.org/psyinfra/HTCrystalBall)
[![codecov](https://codecov.io/gh/psyinfra/HTCrystalBall/branch/master/graph/badge.svg)](https://codecov.io/gh/psyinfra/HTCrystalBall)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/a3f2efd33ff14ab9af91e5a367b6d0ff)](https://www.codacy.com/gh/psyinfra/HTCrystalBall?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=psyinfra/HTCrystalBall&amp;utm_campaign=Badge_Grade)

A crystal ball, that lets you peer into the future.

`HTCrystalBall` is a tool that - based on given job parameters - analyzes an `HTCondor pool` to give a
prediction about suitable `slot` configurations, the number of simulaneous executable `jobs` as well as core-hours and wall-time it takes to complete a given number of jobs.
## Overview
If you are familiar with this README or just want to skip sections,
here is a list of hyperlinks for you to skip searching for a particular section:

*   [Requirements](#Requirements)
*   [Installation](#Installation-and-Configuration)
*   [Description](#Description)
*   [Input](#INPUT)
*   [Output](#OUTPUT)
*   [Examples](#Examples)
*   [Testing](#Testing)

## Requirements
`HTCrystalBall` uses the `rich` and `natsort` module for printing out nicely formatted and ordered tables.
The `rich` module requires Python 3.6+ to run.
For using the HTCondor API the module `htcondor` has to be installed.

To also run our tests, we require `pytest` and `pyflakes` to be installed.

## Installation and Configuration
To install and configure `HTCrystalBall` please follow these steps:

1.  clone this repo to the file system of any machine in your HTCondor cluster
    
    `git clone https://github.com/psyinfra/HTCrystalBall.git`
2.  create and open a new or existing python `virtualenv` by using the commands
    
    `python3 -m venv /path/to/virtual/environment`
    
    `source /path/to/virtual/environment/bin/activate`

2.  `cd` into the newly created directory and install python modules using the setup.py to then call the script from the `virtualenv` whenever necessary

    `cd HTCrystalBall`

    `pip3 install .`

3.  (optional) adjust the keys to be queried from the htcondor in `main.py`

    `QUERY_DATA = ["SlotType", "Machine", "TotalSlotCpus", "TotalSlotDisk", "TotalSlotMemory", "TotalSlotGPUs"]`

## Description
This project contains of five modules
*   `main.py` to define the command line parser and start manage executiing the other modules
*   `collect.py` for fetching an HTCondor slot configuration and creating a list of slots
*   `examine.py` for checking slot configurations whether they fit a given job
*   `display.py` for formatting and returning output
*   `utils.py` as a library of methods for the other modules to use

and is intended for HTCondor (server) systems, which describe resources as slots
rather than nodes.

`collect.py` uses HTCondor's `Collector().query()` method to query the defined attributes about each slot.
In our particular use-case we decided to ignore all dynamic created slots by using `constraint='SlotType != "Dynamic"'`
as those slots are created when needed and are not available to the general pool.

So if you want to adjust this script to your use-case feel free to add other keys to `QUERY_DATA` or change other
parameters of the `Collector().query()` method.

As it turns out, the resulting list of slots had more than 500 entries because every single slot (static and dynamic created ones)
would be displayed. But as we don't need every single slot of identical configuration,
we chose to filter them out to show all available slot configurations and just store a counter for each slot configuration
as the `SimSlots` property to reflect the number of slots with similar configuration.
Each configuration is assigned to a node with its full name as the key:

    {
        "cpuXX.htc.test.com": [
                {"TotalSlotCpus": 2, "TotalSlotDisk": 51.53, "TotalSlotMemory": 30.0, "TotalSlotGPUs": 0, "SlotType": "partitionable", "SimSlots": 11},
                {"TotalSlotCpus": 1, "TotalSlotDisk": 3.46, "TotalSlotMemory": 5.88, "TotalSlotGPUs": 0, "SlotType": "static", "SimSlots": 11}
            ]
    }

Here comes our `crystal ball` to play its part. The script takes a user input of requested
ressources for a single job and checks whether and how it fits into the given slots.
If the user provides a parameter for the number of `jobs` to be executed and
the execution time per job, a total `wall time` can also be calculated.

## INPUT

To use our `crystal ball` your input has to provide at least CPU and RAM requirements 
while also giving you the ability to pass values familiar parameter you already know from
writing a [condor submit](https://htcondor.readthedocs.io/en/latest/users-manual/submitting-a-job.html) file:

    htcrystalball | htcb --help
    
    usage: htcrystalball -c CPU -r RAM [-g GPU] [-d DISK] [-j JOBS] [-t TIME] [-m MAX_NODES] [-v]

    htcrystalball - A crystal ball that lets you peek into the future. To get a
    preview for any job you are trying ot execute using HTCondor, please pass at
    least the number of CPUs and the amount of RAM including units (e.g. 100MB,
    90M, 10GB, 15g) according to the usage example shown above. For JOB duration
    please use d, h, m, or s
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         Print extended log to stdout
      -c CPU, --cpu CPU     Set number of requested CPU Cores
      -g GPU, --gpu GPU     Set number of requested GPU Units
      -j JOBS, --jobs JOBS  Set number of jobs to be executed
      -t TIME, --time TIME  Set the duration for one job to be executed
      -d DISK, --disk DISK  Set amount of requested disk storage
      -r RAM, --ram RAM     Set amount of requested memory storage
      -m MAXNODES, --maxnodes MAXNODES
                            Set maximum of nodes to run jobs on
    
    PLEASE NOTE: HTCondor always uses binary storage sizes (1 GiB = 1024 MiB, 1 GB
    = 1000 MB), so inputs will automatically be treated that way.

## OUTPUT
### Basic Output
Our `crystal ball` will give you a brief peek of the result when checking your jobs when executing
the command `htcb --cpu 1 --ram 7500M --jobs 1`:

    632 jobs of this size can run on this pool.

    No --jobs or --time specified. No duration estimate will be given.

    The above number(s) are for an idle pool.

The estimated wall time can only be calculated if both the number of `jobs` and `time` per job are being provided.

### Advanced Output
When using `--verbose` HTCrystalBall will return the following output:

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

### Examples
Here are some more examples:

#### Single-core with huge RAM
htcb --cpu 1 --ram 128G --disk 1T

    17 jobs of this size can run on this pool.

    No --jobs or --time specified. No duration estimate will be given.

    The above number(s) are for an idle pool.

#### Big multi-core with medium RAM
htcb --cpu 16 --ram 16G --disk 100G --jobs 20 --time 5h

    19 jobs of this size can run on this pool.

    A total of 1600 core-hour(s) will be used and 20 job(s) will complete in about 10 hour(s).

    The above number(s) are for an idle pool.
    
#### Matlab mode
htcb --cpu 16 --ram 16G --disk 100G --maxnodes 2 --jobs 20 --time 5h

    A maximum of 8 jobs of this size can run using only 2 nodes.

    The following nodes are suggested:
    cpu9.htc.inm7.de
    cpu10.htc.inm7.de

    A total of 1600 core-hour(s) will be used and 20 job(s) will complete in about 15 hour(s).

    The above number(s) are for an idle pool.

htcb --cpu 16 --ram 16G --disk 100G --maxnodes 2 --verbose

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
    
#### GPU job
htcb --cpu 1 --gpu 1 --ram 8G --disk 64G --jobs 10 --time 2h

    8 jobs of this size can run on this pool.

    A total of 20 core-hour(s) will be used and 10 job(s) will complete in about 4 hour(s).

    The above number(s) are for an idle pool.

## Testing
Make sure you have the necessary python modules:

`pip3 install pytest natsort`

Run the following command to execute your test:

`python3 -m pytest -q tests/test_me.py`
