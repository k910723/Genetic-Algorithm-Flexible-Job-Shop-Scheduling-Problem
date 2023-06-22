class Activity:
    def __init__(self, job, id_activity):
        self.__job = job
        self.__id_activity = id_activity
        self.__operations_to_be_done = []
        self.__operation_done = None

    # toString method
    def __str__(self):
        stringToReturn = "Job" + str(self.id_job) + " [Activity" + str(self.__id_activity) + "]\n Operations to be done :\n"
        for operation in self.__operations_to_be_done:
            stringToReturn += str(operation) + "\n"
        stringToReturn += "Operations done :\n" + str(self.__operation_done) + "\n"
        return stringToReturn

    @property
    def shop_time(self):
        return self.operation_done.duration if self.is_done else max(self.__operations_to_be_done, key=lambda operation: operation.duration)

    @property
    def is_feasible(self):
        return self.__job.check_if_previous_activity_is_done(self.__id_activity)

    @property
    def is_pending(self):
        return len(list(filter(lambda element: element.is_pending, self.__operations_to_be_done))) > 0

    # the job id of current activity
    @property
    def id_job(self):
        return self.__job.id_job

    # the id of current activity
    @property
    def id_activity(self):
        return self.__id_activity

    # add operation to this activity
    def add_operation(self, operation):
        self.__operations_to_be_done.append(operation)

    # is operation done
    @property
    def is_done(self):
        return not (self.__operation_done is None)

    # operations to be done
    @property
    def next_operations(self):
        return self.__operations_to_be_done

    # return the shortest operations
    @property
    def shortest_operation(self):
        candidate_operation = None
        for operation in self.__operations_to_be_done:
            if candidate_operation is None or operation.duration < candidate_operation.duration:
                candidate_operation = operation
        return candidate_operation
    
    # return operations to be done
    @property
    def operations_to_be_done(self):
        return self.__operations_to_be_done
    
    # return operations done
    @property
    def operation_done(self):
        return self.__operation_done

    # force a operation to terminate
    def terminate_operation(self, operation):
        # delete from the list of operations to be done
        self.__operations_to_be_done = list(
            filter(lambda element: element.id_operation != operation.id_operation, self.__operations_to_be_done))
        # add to the list of operations done
        self.__operation_done = operation
        self.__job.activity_is_done(self)

    def get_operation(self, id_operation):
        for operation in self.__operations_to_be_done:
            if operation.id_operation == id_operation:
                return operation
                