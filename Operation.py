class Operation:
	def __init__(self, id_operation, id_machine, duration):
		self.__id_operation = id_operation
		self.__duration = duration
		self.__id_machine = id_machine
		self.__time = None
		self.__is_pending = False
		self.__place_of_arrival = None

	# toString
	def __str__(self):
		output = "operation" + str(self.__id_operation) + " [machine" + str(
			self.__id_machine) + "processing] takes" + str(self.__duration) + "(unit time)"
		if not (self.__time is None):
			output += ", this operation starts at" + str(self.__time)
		return output

	# the ID of operation
	@property
	def id_operation(self):
		return self.__id_operation

	# is finished
	def is_done(self, t):
		return not (self.__time is None) and self.__time + self.__duration <= t

	# is pending
	@property
	def is_pending(self):
		return self.__is_pending

	# set pending status
	@is_pending.setter
	def is_pending(self, value):
		self.__is_pending = value

	# return the machine ID that is going to process this operation
	@property
	def place_of_arrival(self):
		return self.__place_of_arrival

	# set the machine ID that is going to process this operation
	@place_of_arrival.setter
	def place_of_arrival(self, value):
		self.__place_of_arrival = value

	# corresponding machine ID
	@property
	def id_machine(self):
		return self.__id_machine

	# duration
	@property
	def duration(self):
		return self.__duration

	# start time
	@property
	def time(self):
		return self.__time

	# set start time
	@time.setter
	def time(self, value):
		if value < 0:
			raise ValueError("[error] start can't be less than 0")
		self.__time = value
