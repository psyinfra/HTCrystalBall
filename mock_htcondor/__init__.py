"""

Module to mock htcondor.Collector().query() for tests.
This also allows tests ti run properly on systems where
A) no htcondor module is available such as Macs and
B) no htcondor pool is available.
"""


class Collector:
    """
    Class to mock htcondor.Collector(), therefore named also Collector
    """

    def __init__(self):
        """

        Initialize the collector with a default list of slot configurations
        that mock the output of htcondor.Collector().query()
        """
        self.query_output = [
            {
                "Machine": "cpu2",
                "TotalSlotCpus": "1",
                "TotalSlotDisk": "287530000",
                "TotalSlotMemory": "500000",
                "SlotType": "Static",
            },
            {
                "Machine": "cpu3",
                "TotalSlotCpus": "1",
                "TotalSlotDisk": "287680000",
                "TotalSlotMemory": "500000",
                "SlotType": "Partitionable",
            },
            {
                "Machine": "gpu1",
                "TotalSlotCpus": "1",
                "TotalSlotGPUs": "4",
                "TotalSlotDisk": "287680000",
                "TotalSlotMemory": "500000",
                "SlotType": "Partitionable",
            }]

    def query(self):
        """
        Function to return the mocked Collector.query result of
        htcondor which is a list of slot dictionaries.
        Returns:

        """
        return self.query_output
