# Darw a Gantt chart
import os
import random

class GraphDrawer:
	@staticmethod
	def draw_schedule(number_machines, max_operations, jobs, filename=None):
		import matplotlib.pyplot as plt
		import matplotlib.patches as patches
		#plt.rcParams['font.sans-serif'] = ['Microsoft YaHei ']
		plt.rcParams['axes.unicode_minus'] = False # solving the problem of symbol '-' being the save button
		operation_vertical_space = 1
		operation_vertical_height = 2
		# dictionary with machine ID as key
		operations_done = {}
		for job in jobs:
			for activity in job.activities_done:
				# add all operations
				operation = activity.operation_done
				if operations_done.get(operation.id_machine) is None:
					list_operations = []
				else:
					list_operations = operations_done.get(operation.id_machine)

				# add a record with its job ID and activity ID
				list_operations.append((job.id_job, activity.id_activity, operation))
				# update dictionary
				operations_done.update({operation.id_machine: list_operations})

		# generate different color
		colors = ['#%06X' % random.randint(0, 256 ** 3 - 1) for _ in range(len(jobs))]
		# draw
		plt.clf()
		plot = plt.subplot()
		for id_machine, list_operations in operations_done.items():
			for id_job, id_activity, operation in list_operations:
				# X - time，Y - machine
				x, y = operation.time, 1 + id_machine * max_operations * (
						operation_vertical_space + operation_vertical_height) + operation.place_of_arrival * (
							   operation_vertical_space + operation_vertical_height)
				# draw according to operation time
				if operation.id_operation == -1: # black block if machine breaks down
					plot.add_patch(
					patches.Rectangle(
						(x, y-1),
						operation.duration,
						operation_vertical_height+2,
						facecolor='#000000'
						)
					)
				else:
					plot.add_patch(
						patches.Rectangle(
							(x, y),
							operation.duration,
							operation_vertical_height,
							facecolor=colors[id_job - 1]
						)
					)

		# adjust Y height
		plt.yticks([1 + (i + 1) * max_operations * (operation_vertical_space + operation_vertical_height) + (
				max_operations * (operation_vertical_height + operation_vertical_space) - operation_vertical_space) / 2 for i in
					range(number_machines)], ["CNC" + str(i + 1) + "#" for i in range(number_machines)])

		plot.autoscale()

		# draw according to job ID
		handles = []
		handles.append(patches.Patch(color="#000000", label='Failure'))
		for id_job, color in enumerate(colors):
			handles.append(patches.Patch(color=color, label='Item' + str(id_job + 1)))
		plt.legend(handles=handles)

		print("image opened in window, close to continue")

		# show the chart
		plt.show()
		if not (filename is None):
			plt.savefig(os.path.join("output", filename), bbox_inches='tight')
			print("image saved")
