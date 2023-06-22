import copy
import os
import sys
import timeit
import warnings

from DataReader import read
from GA import GAScheduler
from GraphDrawer import GraphDrawer
from Heuristics import Heuristics
from Scheduler import Scheduler

print("=== Flexible Job Shop Problem - Genetic Algorithm ===")
# input path
if len(sys.argv) == 1:
	path = input("Please enter the relative path of the input file : ")
# read from command
else:
	path = sys.argv[1]

warnings.simplefilter('ignore', RuntimeWarning)
# read input file
jobs_list, machines_list, number_max_operations, RGV_config = read(path)
number_total_machines = len(machines_list)
number_total_jobs = len(jobs_list)

# every iteration is a simulation for specified parameters
while True:
	temp_jobs_list = copy.deepcopy(jobs_list)
	temp_machines_list = copy.deepcopy(machines_list)
	# current data
	print("Data :")
	print('\tthe number of jobs : ', number_total_jobs)
	print('\tthe number of machines :', number_total_machines)
	print("\tthe number of maximum concurrent operations on a machine : ", str(number_max_operations))
	print("\tmachine break down rate : ", temp_machines_list[0].CNC_break_down_rate)
	print("\tmachine break down recovery time : ", temp_machines_list[0].CNC_recovery_time_cost)
	print("\n")
	choice = input("Continue with the data above? [y/n]: ")
	if choice == "y":
		string = input("population : ")
		total_population = int(string)
		string = input("generation(the number of iteration) : ")
		max_generation = int(string)
		start = timeit.default_timer() # timer
		# GA
		s = GAScheduler(temp_machines_list, temp_jobs_list, RGV_config)
		total_time, log_file_content, result_file_content = s.run_genetic(total_population=total_population, max_generation=max_generation, verbose=True)
		stop = timeit.default_timer()
		print("The calculation takes " + str(stop - start) + " seconds")
		# save log and result file
		print("saving log file...")
		file = open(path + ".log.csv", "w+", encoding='UTF-8')
		file.write(str(log_file_content))
		print("Log file has been saved to ", path, ".log.csv")

		print("saving result file...")
		file = open((path + ".result.csv"), "w+", encoding='UTF-8')
		file.write(str(result_file_content))
		print("Result file has been saved to ", path, ".result.csv")
		# draw Gantt chart
		draw = input("draw the Gantt chart of the best strategy ? [y/n] ")
		if draw == "n" or draw == "N":
			continue
		else:
			print("drawing...")
			GraphDrawer.draw_schedule(number_total_machines, 1, temp_jobs_list, filename=(path + ".result.png"))
		del s
	elif choice == "n":
		break
	else:
		print("Please enter again.")
	del temp_jobs_list, temp_machines_list
