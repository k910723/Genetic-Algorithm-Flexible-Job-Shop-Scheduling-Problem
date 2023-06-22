class Heuristics:
	# select first operation when there are multiple choices
	@staticmethod
	def select_first_operation(jobs_to_be_done, max_operations, _):
		best_candidates = {}

		for job in jobs_to_be_done:
			current_activity = job.current_activity
			best_operation = current_activity.shortest_operation

			if best_candidates.get(best_operation.id_machine) is None:
				best_candidates.update({best_operation.id_machine: [(current_activity, best_operation)]})
			elif len(best_candidates.get(best_operation.id_machine)) < max_operations:
				best_candidates.get(best_operation.id_machine).append((current_activity, best_operation))
			else:
				list_operations = best_candidates.get(best_operation.id_machine)

				for key, (_, operation) in enumerate(list_operations):
					if operation.duration < best_operation.duration:
						list_operations.pop(key)
						break

				if len(list_operations) < max_operations:
					list_operations.append((current_activity, best_operation))

		return best_candidates

	# longest expected processing time first
	@staticmethod
	def longest_expected_processing_time_first(jobs_to_be_done, max_operations, current_time):
		pass

	# shortest slack time
	@staticmethod
	def shortest_slack_per_remaining_operations(jobs_to_be_done, max_operations, current_time):
		pass

	# highest critical ratio
	@staticmethod
	def highest_critical_ratios(jobs_to_be_done, max_operations, current_time):
		best_candidates = {}
		critical_ratios = {}
		assignment = {}

		for job in jobs_to_be_done:
			current_activity = job.current_activity

			# calculate the critical ratio of every operation of the activity
			for operation in current_activity.next_operations:
				critical_ratio = operation.duration / (job.total_shop_time - current_time)
				critical_ratios.update({job.id_job: (current_activity, operation, critical_ratio)})

			for id_job, current_activity, operation, critical_ratio in critical_ratios.items():
				if assignment.get(operation.id_machine) is None:
					assignment.update({operation.id_machine: (current_activity, operation, critical_ratio)})

				elif len(assignment.get(operation.id_machine)) < max_operations:
					list_operations = assignment.get(operation.id_machine)
					list_operations.append((current_activity, operation, critical_ratio))
					best_candidates.update({operation.id_machine: list_operations})

	# select a random operation
	@staticmethod
	def random_operation_choice(jobs_to_be_done, max_operations, _):
		import random
		best_candidates = {}
		dict_operations = {}

		for job in jobs_to_be_done:
			current_activity = job.current_activity
			for operation in current_activity.next_operations:
				if dict_operations.get(operation.id_machine) is None:
					dict_operations.update({operation.id_machine: [(current_activity, operation)]})
				else:
					dict_operations.get(operation.id_machine).append((current_activity, operation))

		for machine, list_operations in dict_operations.items():
			best_candidates.update({machine: list(
				set([list_operations[random.randint(0, len(list_operations) - 1)] for _ in range(max_operations)]))})

		return best_candidates

	## todo
	@staticmethod
	def initialisation_list(jobs_to_be_done):
		machine_assignment = []
		operation_sequence = []
		for job in jobs_to_be_done:
			for activity in job.activities_to_be_done:
				operation_sequence.append(job.id_job)
				machine_assignment.append(activity.next_operations[0].id_machine)
		print("machine selected :")
		for machine in machine_assignment:
			print(str(machine))
		print("operations :")
		for operation in operation_sequence:
			print(operation)
