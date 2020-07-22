# HTCrystalBall

[![Build Status](https://travis-ci.org/psyinfra/HTCrystalBall.svg?branch=master)](https://travis-ci.org/psyinfra/HTCrystalBall)

A crystal ball, that lets you peer into the future.

## INPUT

This tool provides a quick and easy way for you to preview how well your requested jobs might be using our HTcondor slots.
Therefore you can provide multiple parameters:

*  CPU: the number of CPU cores for your job
*  RAM: the amount of RAM your job needs
*  DISK: the amount of disk space your job needs
*  GPU: the number of GPU units your job should use
*  JOBS: the number of similar jobs you want to execute
*  TIME: the estimated time for each job to run
*  MAXNODES: the maximum number of nodes that a job can run on e.g. due to licensing limitations


> NOTE: As HTCondor uses base-2 storage units instead of base 10, DISK and RAM are treated as base-2
>and expect at least a letter that describes the unit like K, M, G or T.

## OUTPUT
### Basic Output
HTCrystalBall will give you a brief summary of the executed slot checking for your jobs like this:

|Slot Type|Job fits|Amount of similar jobs|Wall Time on Idle|
|---|---|---|---|
|gpu|...|...|0 min|
|static|...|...|0 min|
|dynamic|...|...|0 min|

*  Job fits: If one job fits into a slot it will be highlighted in green color, if not in red.
*  Amount of similar jobs: number of jobs similar to the one defined, that fit into a slot the same time.
*  Wall time on Idle: Theoretical execution time for all similar jobs to be executed on a slot.

### Advanced Output
When using VERBOSE HTCrystalBall will print out your given Input...

|Parameter|Input Value|
|---|---|
|CPUS|...|
|RAM|...|
|STORAGE|...|
|GPUS|...|
|JOBS|...|
|JOB DURATION|...|
|MAXIMUM NODES|...|

...the current slot configuration of Juseless...

|Node|Slot Type|Total slots|Cores|GPUs|RAM|DISK|
|---|---|---|---|---|---|---|
|Name|gpu|...|...|...|...|...|
|Name|static|...|...|...|...|...|
|Name|dynamic|...|...|...|...|...|

...and a more detailed summary of the slot checking:

|Node|Slot Type|Job fits|Slot usage|RAM usage|GPU usage|Amount of similar jobs|Wall Time on Idle|
|---|---|---|---|---|---|---|---|
|Name|gpu|YES|... (x %)|... (x %)|... (x %)|...|... min|
|Name|static|NO|... (x %)|... (x %)|... (x %)|...|... min|
|Name|dynamic|NO|... (x %)|... (x %)|... (x %)|...|... min|

### Examples:
./htcrystalball.py -c 2 -r 10G -g 2

    ---------------------- PREVIEW ----------------------
    ┏━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
    ┃ Slot Type ┃ Job fits ┃ Amount of similar jobs ┃ Wall Time on IDLE ┃
    ┡━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
    │ gpu       │      YES │                      4 │             0 min │
    └───────────┴──────────┴────────────────────────┴───────────────────┘

./htcrystalball.py -c 2 -r 10G -g 2 -v

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
    ┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
    ┃ Node         ┃ Slot Type ┃ Total Slots ┃ Cores ┃ GPUs ┃        RAM ┃        DISK ┃
    ┡━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
    │ gpu1         │ gpu       │          17 │    10 │    4 │ 165.99 GiB │ 1617.34 GiB │
    └──────────────┴───────────┴─────────────┴───────┴──────┴────────────┴─────────────┘
    ---------------------- PREVIEW ----------------------
    ┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
    ┃ Node         ┃ Slot Type ┃ Job fits ┃       Slot usage ┃       RAM usage       ┃ GPU usage ┃ Amount of similar jobs ┃ Wall Time on IDLE ┃
    ┡━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
    │ gpu1         │ gpu       │      YES │ 2/10 (20%) Cores │ 10.00/165.99 GiB (6%) │ 2/4 (50%) │                      2 │             0 min │
    └──────────────┴───────────┴──────────┴──────────────────┴───────────────────────┴───────────┴────────────────────────┴───────────────────┘

./htcrystalball.py -c 5 -r 10G

    ---------------------- PREVIEW ----------------------
    ┏━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
    ┃ Slot Type ┃ Job fits ┃ Amount of similar jobs ┃ Wall Time on IDLE ┃
    ┡━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
    │ dynamic   │      YES │                     12 │             0 min │
    │ dynamic   │      YES │                     12 │             0 min │
    │ dynamic   │      YES │                      6 │             0 min │
    │ dynamic   │      YES │                      6 │             0 min │
    │ dynamic   │      YES │                      4 │             0 min │
    │ dynamic   │      YES │                      4 │             0 min │
    │ dynamic   │      YES │                      4 │             0 min │
    │ dynamic   │      YES │                      4 │             0 min │
    │ dynamic   │      YES │                      4 │             0 min │
    │ dynamic   │      YES │                      2 │             0 min │
    │ dynamic   │      YES │                      2 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ dynamic   │       NO │                      0 │             0 min │
    │ static    │       NO │                      0 │             0 min │
    │ static    │       NO │                      0 │             0 min │
    │ static    │       NO │                      0 │             0 min │
    │ static    │       NO │                      0 │             0 min │
    │ static    │       NO │                      0 │             0 min │
    │ static    │       NO │                      0 │             0 min │
    │ static    │       NO │                      0 │             0 min │
    │ static    │       NO │                      0 │             0 min │
    │ static    │       NO │                      0 │             0 min │
    │ static    │       NO │                      0 │             0 min │
    └───────────┴──────────┴────────────────────────┴───────────────────┘

./htcrystalball.py -c 5 -r 10G  -v

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
    ┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ Node         ┃ Slot Type ┃ Total Slots ┃ Cores ┃   GPUs ┃       RAM ┃                   DISK ┃
    ┡━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
    │ cpu7         │ dynamic   │           7 │    12 │ ------ │  65.0 GiB │            3416.16 GiB │
    │ cpu7         │ dynamic   │           7 │     1 │ ------ │  20.0 GiB │             212.16 GiB │
    │ cpu7         │ dynamic   │           7 │     4 │ ------ │   4.0 GiB │                3.6 GiB │
    │ cpu7         │ dynamic   │           7 │     1 │ ------ │  5.88 GiB │                3.6 GiB │
    │ cpu8         │ dynamic   │           7 │    12 │ ------ │  65.0 GiB │            3416.17 GiB │
    │ cpu8         │ dynamic   │           7 │     1 │ ------ │  20.0 GiB │             212.16 GiB │
    │ cpu8         │ dynamic   │           7 │     1 │ ------ │  5.88 GiB │                3.6 GiB │
    │ cpu9         │ dynamic   │          52 │    64 │ ------ │ 500.0 GiB │             3416.2 GiB │
    │ cpu9         │ dynamic   │          52 │     1 │ ------ │   5.0 GiB │                3.6 GiB │
    │ cpu9         │ dynamic   │          52 │     1 │ ------ │  20.0 GiB │             212.16 GiB │
    │ cpu9         │ dynamic   │          52 │     1 │ ------ │  5.88 GiB │                3.6 GiB │
    │ cpu10        │ dynamic   │          61 │    64 │ ------ │ 500.0 GiB │             3416.2 GiB │
    │ cpu10        │ dynamic   │          61 │     1 │ ------ │   5.0 GiB │                3.6 GiB │
    │ cpu10        │ dynamic   │          61 │     1 │ ------ │  20.0 GiB │             212.16 GiB │
    │ cpu10        │ dynamic   │          61 │     1 │ ------ │  5.88 GiB │                3.6 GiB │
    │ cpu13        │ dynamic   │          11 │     2 │ ------ │  30.0 GiB │              51.53 GiB │
    │ cpu13        │ dynamic   │          11 │     1 │ ------ │  5.88 GiB │               3.46 GiB │
    │ cpu14        │ dynamic   │          11 │    24 │ ------ │ 210.0 GiB │            3414.33 GiB │
    │ cpu14        │ dynamic   │          11 │     1 │ ------ │  20.0 GiB │             212.05 GiB │
    │ cpu15        │ dynamic   │          11 │    24 │ ------ │ 210.0 GiB │            3414.52 GiB │
    │ cpu15        │ dynamic   │          11 │     1 │ ------ │  20.0 GiB │             212.06 GiB │
    │ cpu16        │ dynamic   │           7 │    20 │ ------ │ 120.0 GiB │            3413.92 GiB │
    │ cpu16        │ dynamic   │           7 │     1 │ ------ │  20.0 GiB │             212.02 GiB │
    │ cpu17        │ dynamic   │           7 │    20 │ ------ │ 120.0 GiB │            3413.83 GiB │
    │ cpu17        │ dynamic   │           7 │     1 │ ------ │  20.0 GiB │             212.02 GiB │
    │ cpu17        │ dynamic   │           7 │     2 │ ------ │  12.0 GiB │               3.59 GiB │
    │ cpu18        │ dynamic   │           7 │    20 │ ------ │ 120.0 GiB │            3413.84 GiB │
    │ cpu18        │ dynamic   │           7 │     1 │ ------ │  20.0 GiB │             212.02 GiB │
    │ cpu21        │ dynamic   │          25 │    32 │ ------ │ 500.0 GiB │            3504.55 GiB │
    │ cpu21        │ dynamic   │          25 │     1 │ ------ │  20.0 GiB │             213.96 GiB │
    │ cpu21        │ dynamic   │          25 │     1 │ ------ │  5.88 GiB │               3.69 GiB │
    │ cpu22        │ dynamic   │          23 │    32 │ ------ │ 500.0 GiB │            3504.55 GiB │
    │ cpu22        │ dynamic   │          23 │     1 │ ------ │  20.0 GiB │             213.96 GiB │
    │ cpu22        │ dynamic   │          23 │     1 │ ------ │  5.88 GiB │               3.69 GiB │
    │ gpu1         │ dynamic   │          17 │     1 │ ------ │  20.0 GiB │             212.05 GiB │
    │ gpu1         │ dynamic   │          17 │     2 │ ------ │  12.0 GiB │               3.59 GiB │
    │ cpu2         │ static    │          12 │     1 │ ------ │   5.0 GiB │ 287.53 GiB[/dark_blue] │
    │ cpu3         │ static    │          12 │     1 │ ------ │   5.0 GiB │ 287.68 GiB[/dark_blue] │
    │ cpu4         │ static    │          12 │     1 │ ------ │   5.0 GiB │ 287.68 GiB[/dark_blue] │
    │ cpu5         │ static    │          12 │     1 │ ------ │   5.0 GiB │ 287.68 GiB[/dark_blue] │
    │ cpu6         │ static    │          12 │     1 │ ------ │   5.0 GiB │ 287.68 GiB[/dark_blue] │
    │ cpu11        │ static    │          64 │     1 │ ------ │   7.5 GiB │  56.16 GiB[/dark_blue] │
    │ cpu12        │ static    │          64 │     1 │ ------ │   7.5 GiB │  56.19 GiB[/dark_blue] │
    │ cpu19        │ static    │          16 │     1 │ ------ │   9.0 GiB │ 215.64 GiB[/dark_blue] │
    │ cpu23        │ static    │          32 │     1 │ ------ │  15.0 GiB │ 110.67 GiB[/dark_blue] │
    │ cpu24        │ static    │          32 │     1 │ ------ │  15.0 GiB │ 110.67 GiB[/dark_blue] │
    └──────────────┴───────────┴─────────────┴───────┴────────┴───────────┴────────────────────────┘
    ---------------------- PREVIEW ----------------------
    ┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
    ┃ Node         ┃ Slot Type ┃ Job fits ┃       Slot usage ┃       RAM usage       ┃ GPU usage ┃ Amount of similar jobs ┃ Wall Time on IDLE ┃
    ┡━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
    │ cpu9         │ dynamic   │      YES │  5/64 (8%) Cores │ 10.00/500.0 GiB (2%)  │  ------   │                     12 │             0 min │
    │ cpu10        │ dynamic   │      YES │  5/64 (8%) Cores │ 10.00/500.0 GiB (2%)  │  ------   │                     12 │             0 min │
    │ cpu21        │ dynamic   │      YES │ 5/32 (16%) Cores │ 10.00/500.0 GiB (2%)  │  ------   │                      6 │             0 min │
    │ cpu22        │ dynamic   │      YES │ 5/32 (16%) Cores │ 10.00/500.0 GiB (2%)  │  ------   │                      6 │             0 min │
    │ cpu14        │ dynamic   │      YES │ 5/24 (21%) Cores │ 10.00/210.0 GiB (5%)  │  ------   │                      4 │             0 min │
    │ cpu15        │ dynamic   │      YES │ 5/24 (21%) Cores │ 10.00/210.0 GiB (5%)  │  ------   │                      4 │             0 min │
    │ cpu16        │ dynamic   │      YES │ 5/20 (25%) Cores │ 10.00/120.0 GiB (8%)  │  ------   │                      4 │             0 min │
    │ cpu17        │ dynamic   │      YES │ 5/20 (25%) Cores │ 10.00/120.0 GiB (8%)  │  ------   │                      4 │             0 min │
    │ cpu18        │ dynamic   │      YES │ 5/20 (25%) Cores │ 10.00/120.0 GiB (8%)  │  ------   │                      4 │             0 min │
    │ cpu7         │ dynamic   │      YES │ 5/12 (42%) Cores │ 10.00/65.0 GiB (15%)  │  ------   │                      2 │             0 min │
    │ cpu8         │ dynamic   │      YES │ 5/12 (42%) Cores │ 10.00/65.0 GiB (15%)  │  ------   │                      2 │             0 min │
    │ cpu7         │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/20.0 GiB (50%)  │  ------   │                      0 │             0 min │
    │ cpu7         │ dynamic   │       NO │ 5/4 (125%) Cores │ 10.00/4.0 GiB (250%)  │  ------   │                      0 │             0 min │
    │ cpu7         │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/5.88 GiB (170%) │  ------   │                      0 │             0 min │
    │ cpu8         │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/20.0 GiB (50%)  │  ------   │                      0 │             0 min │
    │ cpu8         │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/5.88 GiB (170%) │  ------   │                      0 │             0 min │
    │ cpu9         │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/5.0 GiB (200%)  │  ------   │                      0 │             0 min │
    │ cpu9         │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/20.0 GiB (50%)  │  ------   │                      0 │             0 min │
    │ cpu9         │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/5.88 GiB (170%) │  ------   │                      0 │             0 min │
    │ cpu10        │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/5.0 GiB (200%)  │  ------   │                      0 │             0 min │
    │ cpu10        │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/20.0 GiB (50%)  │  ------   │                      0 │             0 min │
    │ cpu10        │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/5.88 GiB (170%) │  ------   │                      0 │             0 min │
    │ cpu13        │ dynamic   │       NO │ 5/2 (250%) Cores │ 10.00/30.0 GiB (33%)  │  ------   │                      0 │             0 min │
    │ cpu13        │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/5.88 GiB (170%) │  ------   │                      0 │             0 min │
    │ cpu14        │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/20.0 GiB (50%)  │  ------   │                      0 │             0 min │
    │ cpu15        │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/20.0 GiB (50%)  │  ------   │                      0 │             0 min │
    │ cpu16        │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/20.0 GiB (50%)  │  ------   │                      0 │             0 min │
    │ cpu17        │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/20.0 GiB (50%)  │  ------   │                      0 │             0 min │
    │ cpu17        │ dynamic   │       NO │ 5/2 (250%) Cores │ 10.00/12.0 GiB (83%)  │  ------   │                      0 │             0 min │
    │ cpu18        │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/20.0 GiB (50%)  │  ------   │                      0 │             0 min │
    │ cpu21        │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/20.0 GiB (50%)  │  ------   │                      0 │             0 min │
    │ cpu21        │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/5.88 GiB (170%) │  ------   │                      0 │             0 min │
    │ cpu22        │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/20.0 GiB (50%)  │  ------   │                      0 │             0 min │
    │ cpu22        │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/5.88 GiB (170%) │  ------   │                      0 │             0 min │
    │ gpu1         │ dynamic   │       NO │ 5/1 (500%) Cores │ 10.00/20.0 GiB (50%)  │  ------   │                      0 │             0 min │
    │ gpu1         │ dynamic   │       NO │ 5/2 (250%) Cores │ 10.00/12.0 GiB (83%)  │  ------   │                      0 │             0 min │
    │ cpu2         │ static    │       NO │ 5/1 (500%) Cores │ 10.00/5.0 GiB (200%)  │  ------   │                      0 │             0 min │
    │ cpu3         │ static    │       NO │ 5/1 (500%) Cores │ 10.00/5.0 GiB (200%)  │  ------   │                      0 │             0 min │
    │ cpu4         │ static    │       NO │ 5/1 (500%) Cores │ 10.00/5.0 GiB (200%)  │  ------   │                      0 │             0 min │
    │ cpu5         │ static    │       NO │ 5/1 (500%) Cores │ 10.00/5.0 GiB (200%)  │  ------   │                      0 │             0 min │
    │ cpu6         │ static    │       NO │ 5/1 (500%) Cores │ 10.00/5.0 GiB (200%)  │  ------   │                      0 │             0 min │
    │ cpu11        │ static    │       NO │ 5/1 (500%) Cores │ 10.00/7.5 GiB (133%)  │  ------   │                      0 │             0 min │
    │ cpu12        │ static    │       NO │ 5/1 (500%) Cores │ 10.00/7.5 GiB (133%)  │  ------   │                      0 │             0 min │
    │ cpu19        │ static    │       NO │ 5/1 (500%) Cores │ 10.00/9.0 GiB (111%)  │  ------   │                      0 │             0 min │
    │ cpu23        │ static    │       NO │ 5/1 (500%) Cores │ 10.00/15.0 GiB (67%)  │  ------   │                      0 │             0 min │
    │ cpu24        │ static    │       NO │ 5/1 (500%) Cores │ 10.00/15.0 GiB (67%)  │  ------   │                      0 │             0 min │
    └──────────────┴───────────┴──────────┴──────────────────┴───────────────────────┴───────────┴────────────────────────┴───────────────────┘
