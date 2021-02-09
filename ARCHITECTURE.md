# Architecture

HTCrystalBall contains five modules:
* `main.py` defines the command line parser and executes the other modules
* `collect.py` fetches the HTCondor slot configuration and creates a list of slots
* `examine.py` checks whether slot configurations fit a given job
* `display.py` formats and returns output
* `utils.py` a library of methods for the other modules to use

`collect.py` uses HTCondor's `Collector().query()` method to query the defined
attributes of each slot. In our particular use-case, we decided to ignore all
dynamic slots (the ephemeral children of partitionable slots) by using
`constraint='SlotType != "Dynamic"'`.

To adjust HTCrystalBall to your site's needs, other keys can be added to
`QUERY_DATA` or the parameters to `Collector().query()` can be changed.

Pools often have a large number of identical sized slots. To reduce complexity,
slot configurations are reduced to one entry with a counter in the `SimSlots`
property to reflect the number of slots with similar configuration.

Each configuration is assigned to a node with its full name as the key:

```
    {
        "cpuXX.htc.test.com": [
                {"TotalSlotCpus": 2, "TotalSlotDisk": 51.53, "TotalSlotMemory": 30.0, "TotalSlotGPUs": 0, "SlotType": "partitionable", "SimSlots": 11},
                {"TotalSlotCpus": 1, "TotalSlotDisk": 3.46, "TotalSlotMemory": 5.88, "TotalSlotGPUs": 0, "SlotType": "static", "SimSlots": 11}
            ]
    }
```

Here comes our "crystal ball" to play its part. The script takes a user input of
requested resources for a single job and checks how (and if) it fits into the
given slots. If the user provides a parameter for the number of jobs to be
executed and the execution time per job, the core-hours and wall time will also
be calculated.
