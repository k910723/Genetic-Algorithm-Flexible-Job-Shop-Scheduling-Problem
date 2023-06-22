# Data format :
# First line : 3 integers
# [the number of jobs (a), the number of machines (b), capacity for simultaneous operations on each machine]
#
# Second line : b integers
# [the unit time to install and uninstall for each machinme]
#
# Third line : 4 integers
# [time for cleaning up a machine, time to move between 1, 2 and 3 units of machine distance]
#
# Fourth line : 2 parameters
# [failure rate (decimal), time for machine recovery (integer, in unit time)]
# If the failure rate is non-zero, the machine will randomly fail with the given probability before starting 
# and will remain idle until recovery time is over.
#
# The Following a lines :
# [number of operations for the job (m),
# (the number of machine available for a operation (n), (the index of the machine, its processing time for the operation) * n) *m
# ]

import os
import re
import random

from Activity import Activity
from Machine import Machine
from Job import Job
from Operation import Operation
from RGVSystemConfig import RGVSystemConfig

def read(path):
    with open(os.path.join(os.getcwd(), path), "r") as data:
        # read first line
        total_jobs, total_machines, max_operations = re.findall('\S+', data.readline()) # find all non-empty symbol with at least length 1
        # to number
        number_total_jobs, number_total_machines, number_max_operations = int(total_jobs), int(total_machines), int(float(max_operations))

        machines_list = []
        machines_install_uninstall_time_cost_list = []
        # read second line
        machines_install_uninstall_time_cost_list = re.findall('\S+', data.readline())
        # read third line
        RGV_clean_time, RGV_movement_1_time, RGV_movement_2_time, RGV_movement_3_time = re.findall('\S+', data.readline())
        # read fourth line
        machine_break_down_rate, machine_recovery_time_cost = re.findall('\S+', data.readline())

        # to number
        RGV_clean_time = int(RGV_clean_time)
        RGV_movement_1_time = int(RGV_movement_1_time)
        RGV_movement_2_time = int(RGV_movement_2_time)
        RGV_movement_3_time = int(RGV_movement_3_time)
        machine_break_down_rate = float(machine_break_down_rate)
        machine_recovery_time_cost = int(machine_recovery_time_cost)

        # RGV system configuration
        RGV_config = RGVSystemConfig(RGV_movement_1_time, RGV_movement_2_time, RGV_movement_3_time, RGV_clean_time)

        for id_machine in range(1, number_total_machines + 1):
            machines_list.append(
                Machine(
                    id_machine,
                    number_max_operations,
                    int(machines_install_uninstall_time_cost_list[id_machine-1]),
                    machine_break_down_rate,
                    machine_recovery_time_cost
                )
            )

        id_job = 1
        jobs_list = []
        for key, line in enumerate(data):
            if key >= number_total_jobs:
                break
            # find all non-empty symbol with at least length 1
            parsed_line = re.findall('\S+', line)
            # new job
            job = Job(id_job)
            # current activity
            id_activity = 1
            # current input in this line
            cur_input = 1
            # activity : (the number of machine available for a operation (n), operation * n)
            # operation : (the index of the machine, its processing time for the operation)
            while cur_input < len(parsed_line):
                number_of_available_machines = int(parsed_line[cur_input])
                # new acitivity
                activity = Activity(job, id_activity)
                for id_operation in range(1, number_of_available_machines + 1):
                    # add operation to activity
                    machine_id_for_current_operation = int(parsed_line[cur_input + 2 * id_operation - 1])
                    activity.add_operation(
                        Operation(
                            id_operation,
                            machine_id_for_current_operation,
                            int(parsed_line[cur_input + 2 * id_operation])
                        )
                    )

                # randomly add a 
                if random.random() < machine_break_down_rate:
                    # select a machine to break down
                    activity.add_operation(
                        Operation(
                            -1, 
                            random.randint(1, number_total_machines), 
                            random.randint(10*60, 20*60) # random recovery time
                        )
                    )

                job.add_activity(activity)
                cur_input += 1 + 2 * number_of_available_machines
                id_activity += 1
            jobs_list.append(job)
            id_job += 1

    return jobs_list, machines_list, number_max_operations, RGV_config
