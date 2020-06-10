import argparse


def define_environment():
    parser = argparse.ArgumentParser(description="Description for my parser")
    parser.add_argument("-v", "--verbose", help="Print extended log to stdout", action='store_true')
    parser.add_argument("-c", "--cpu", help="Set number of requested CPU Cores", type=int, action='store_const')
    parser.add_argument("-g", "--gpu", help="Set number of requested GPU Units", type=int, action='store_const')
    parser.add_argument("-d", "--disk", help="Set amount of requested disk storage in GB", type=int,
                        action='store_const')
    parser.add_argument("-r", "--ram", help="Set amount of requested memory storage in GB", type=int,
                        action='store_const')

    p = parser.parse_args()
    return p


# a collection of slots will be defined as a list of dictionarys for each different slot configuration
def define_slots():
    #  define all existing static slot configurations
    static_slots = [{"node": "cpu1", "total_cores": 32, "total_ram": 500, "cores_blocked": 0, "ram_blocked": 0,
                     "single_slot": {"cpu_cores": 1, "ram_amount": 15}}]

    #  define all existing partitionable configurations
    partitionable_slots = [{"node": "cpu2", "total_cores": 32, "total_ram": 500, "cores_blocked": 0, "ram_blocked": 0}]

    return static_slots, partitionable_slots


def check_slots(static, dynamic, num_cpu, amount_ram, amount_disk=0, num_gpu=0):
    #  print out what the user gave as input
    res = "REQUESTED_CPU: " + str(num_cpu) + " Cores, REQUESTED_RAM: " + str(amount_ram) + " GB\n"
    #  Check all DYNAMIC slots
    for slot in dynamic:
        available_cores = slot["total_cores"] - slot["cores_blocked"]
        available_ram = slot["total_ram"] - slot["ram_blocked"]
        # if the job fits, calculate and return the usage
        if num_cpu <= available_cores and amount_ram <= available_ram:
            cpu_share = int(round((num_cpu/slot["total_cores"])*100))
            ram_share = int(round((amount_ram/slot["total_ram"])*100))
            #  add the interpretation to the output
            res += "The requested job might use " + str(cpu_share) + "% of the cores and " + \
                   str(ram_share) + "% of the RAM on DYNAMIC node " + slot["node"] + ".\nThis means that " + \
                   str(int(available_cores/num_cpu)-1) + " other jobs with similar requirements can run at the same time.\n"

    #  Check all STATIC slots
    for slot in static:
        available_cores = slot["total_cores"] - slot["cores_blocked"]
        available_ram = slot["total_ram"] - slot["ram_blocked"]
        # if the job fits, calculate and return the usage
        if num_cpu <= available_cores and amount_ram <= available_ram:
            #  On STATIC nodes it's like ALL or NOTHING, when there are more than one CPUs requested
            cpu_share = int(round((num_cpu/slot["total_cores"])*100)) if num_cpu == 1 else 100
            similar_jobs = int(available_cores - num_cpu) if num_cpu == 1 else 0
            ram_share = int(round((amount_ram/slot["total_ram"])*100)) if num_cpu == 1 else 100
            #  add the interpretation to the output
            res += "The requested job might use " + str(cpu_share) + "% of the cores and " + \
                   str(ram_share) + "% of the RAM on STATIC node " + slot["node"] + ".\nThis means that " + \
                   str(similar_jobs) + " other jobs with similar requirements can run at the same time.\n"
    return res


if __name__ == "__main__":
    static_slots, dynamic_slots = define_slots()
    answer = check_slots(static_slots, dynamic_slots, 2, 20)
    print("Check finished! Answer:\n" + answer)