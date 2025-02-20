class Machine:
	def __init__(self, id_machine, max_operations, install_uninstall_time_cost,CNC_break_down_rate,CNC_recovery_time_cost):
		self.__id_machine = id_machine
		self.__is_working = False
		self.__operations_done = []
		self.__processed_operations = []
		self.__max_operations = max_operations
		self.__install_uninstall_time_cost = install_uninstall_time_cost
		self.__current_time = 0
		self.__available_places = [i for i in range(max_operations)]
		self.__CNC_break_down_rate = CNC_break_down_rate
		self.__CNC_recovery_time_cost = CNC_recovery_time_cost

	# machine ID
	@property
	def id_machine(self):
		return self.__id_machine

	# finished operations
	@property
	def operations_done(self):
		return self.__operations_done

	# machine breakdown rate
	@property
	def CNC_break_down_rate(self):
		return self.__CNC_break_down_rate

	# machine recovery time
	@property
	def CNC_recovery_time_cost(self):
		return self.__CNC_recovery_time_cost

	# time to install and uninstall on this machine
	@property
	def install_uninstall_time_cost(self):
		return self.__install_uninstall_time_cost

	# is working at maximum capacity
	def is_working_at_max_capacity(self):
		return len(self.__processed_operations) == self.__max_operations

	# add a operation to this machine
	def add_operation(self, activity, operation):
		if self.is_working_at_max_capacity():
			raise EnvironmentError("machine at maximum capacity")
		if operation.id_machine != self.__id_machine:
			raise EnvironmentError("machine ID incorrect")

		operation.time = self.__current_time
		operation.is_pending = True
		operation.place_of_arrival = self.__available_places.pop(0)

		self.__processed_operations.append((activity, operation))

	# simulate work in a unit time
	def work(self):
		self.__current_time += 1
		for activity, operation in self.__processed_operations:
			if operation.time + operation.duration <= self.__current_time:
				self.__processed_operations = list(filter(lambda element: not (
						element[0].id_job == activity.id_job and element[0].id_activity == activity.id_activity and
						element[1].id_operation == operation.id_operation), self.__processed_operations))
				self.__available_places.append(operation.place_of_arrival)
				activity.terminate_operation(operation)
				self.__operations_done.append(operation)
