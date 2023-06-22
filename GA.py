import copy
import random
import sys

from colorama import init
from deap import base, creator
from termcolor import colored

from Heuristics import Heuristics
from Scheduler import Scheduler

# the location of machine
CNC_LOCATION_COLOMN = [0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 4]

class GAScheduler:
    def __init__(self, machines, jobs, RGV_config):
        init()  # init colorama
        self.__original_stdout = sys.stdout
        self.__toolbox = base.Toolbox()
        self.__machines = machines
        self.__jobs = jobs
        self.__rgv_config = RGV_config

    @staticmethod
    def constraint_order_respected(individual):
        list = [(activity.id_job, activity.id_activity)
                for (activity, _) in individual]
        for key, (id_job, id_activity) in enumerate(list):
            if id_activity == 1:
                continue
            elif not list.index((id_job, id_activity - 1)) < key:
                return False
        return True

    # initialize individual
    def init_individual(self, ind_class, size):
        temp_jobs_list = copy.deepcopy(self.__jobs)
        temp_machines_list = copy.deepcopy(self.__machines)

        s = Scheduler(temp_machines_list, 1, temp_jobs_list, self.__rgv_config)
        s.run(Heuristics.random_operation_choice, verbose=True)

        # find all jobs and finished activities
        list_activities = []
        for temp_job in temp_jobs_list:
            for temp_activity in temp_job.activities_done:
                activity = self.__jobs[temp_activity.id_job - 1].get_activity(temp_activity.id_activity)
                operation = activity.get_operation(temp_activity.operation_done.id_operation)
                list_activities.append(
                    (temp_activity.operation_done.time, activity, operation))
        # print(str(list_activities))
        # sort by time
        list_activities = sorted(list_activities, key=lambda x: x[0])
        individual = [(activity, operation)
                      for (_, activity, operation) in list_activities]
        del temp_jobs_list, temp_machines_list
        return ind_class(individual)

    # initialize population
    def init_population(self, total_population):
        return [self.__toolbox.individual() for _ in range(total_population)]

    # calculate movement time cost
    def calculate_RGV_movement_time_cost(self, from_CNC_id, to_CNC_id, verbose=False):
        col_from = CNC_LOCATION_COLOMN[from_CNC_id]
        col_to = CNC_LOCATION_COLOMN[to_CNC_id]
        diff = abs(col_to-col_from)
        if diff == 0:
            return 0
        elif diff == 1:
            return self.__rgv_config.RGV_movement_1_time
        elif diff == 2:
            return self.__rgv_config.RGV_movement_2_time
        elif diff == 3:
            return self.__rgv_config.RGV_movement_3_time

    # calculate the makespan of an individual (decoder)
    def compute_time(self, individual):
        # the list of time where activity occurs
        list_time = []
        # store the schedule of each machine
        schedule = {}
        for machine in self.__machines:
            schedule.update({machine.id_machine: []})
        # store the finished operation of each job
        operations_done = {}
        for job in self.__jobs:
            operations_done.update({job.id_job: []})

        previous_machine_id = 1
        extra_time_cost = 0
        previous_event_time = 0

        for activity, operation in individual:
            # get the time when last operation was finished
            # print("operation time = ", operation.duration)
            time_last_operation, last_operation_job = operations_done.get(activity.id_job)[-1] if len(
                operations_done.get(activity.id_job)) > 0 else (0, None)
            time_last_machine, last_operation_machine = schedule.get(operation.id_machine)[-1] if len(
                schedule.get(operation.id_machine)) > 0 else (0, None)
            
            # claculate extra time cost including cleanup time, install and uninstall time and movement time
            extra_time_cost = self.__rgv_config.RGV_clean_time + \
                self.__machines[operation.id_machine-1].install_uninstall_time_cost + \
                self.calculate_RGV_movement_time_cost(previous_machine_id, operation.id_machine)
            
            if operation.id_operation == -1:
                # print("Break down at machine ",  operation.id_machine)
                extra_time_cost = 0
            
            previous_machine_id = operation.id_machine

            # first start
            if last_operation_machine is None and last_operation_job is None:
                time = extra_time_cost
            elif last_operation_machine is None:
                time = time_last_operation + last_operation_job.duration + extra_time_cost
            elif last_operation_job is None:
                time = time_last_machine + last_operation_machine.duration + extra_time_cost
            else:
                time = max(time_last_operation + last_operation_job.duration,
                           time_last_machine + last_operation_machine.duration) + extra_time_cost
            # check time constraint
            if time == previous_event_time:
                time = previous_event_time + extra_time_cost
            elif time > previous_event_time and (time - previous_event_time) < extra_time_cost:
                time = previous_event_time + extra_time_cost
            elif time < previous_event_time:
                for temp_time in list_time:
                    if time >= temp_time and time - temp_time < extra_time_cost:
                        time = temp_time + extra_time_cost
                        break
            
            #print("previous_event_time = ", previous_event_time)
            previous_event_time = time
            list_time.append(time)
            #print("time = ", time)
            operations_done.update({activity.id_job: operations_done.get(
                activity.id_job) + [(time, operation)]})
            schedule.update({operation.id_machine: schedule.get(
                operation.id_machine) + [(time, operation)]})
            
        # calculate makespan
        total_time = 0
        for machine in self.__machines:
            if len(schedule.get(machine.id_machine)) > 0:
                time, operation = schedule.get(machine.id_machine)[-1]
                if time + operation.duration > total_time:
                    total_time = time + operation.duration
        # print("total time", total_time)
        return total_time, list_time

    # calculate the fitness of an individual
    def evaluate_individual(self, individual):
        return self.compute_time(individual)[0],

    # mutate function
    @staticmethod
    def mutate_individual(individual):
        # all candidates activities for mutation
        candidates = list(filter(lambda element: len(element[0].next_operations) > 1, individual))
        # randomly choose one for mutation if there exists candidates
        if len(candidates) > 0:
            mutant_activity, previous_operation = candidates[random.randint(0, len(candidates) - 1)]
            id_mutant_activity = [element[0] for element in individual].index(mutant_activity)
            mutant_operation = previous_operation
            while mutant_operation.id_operation == previous_operation.id_operation:
                mutant_operation = mutant_activity.next_operations[random.randint(0, len(mutant_activity.next_operations) - 1)]
            individual[id_mutant_activity] = (mutant_activity, mutant_operation)
        # remove previous fitness since it needs to be recalculated
        del individual.fitness.values
        return individual

    # 计算边界
    @staticmethod
    def compute_bounds(permutation, considered_index):
        considered_activity, _ = permutation[considered_index]
        min_index = key = 0
        max_index = len(permutation) - 1
        while key < max_index:
            activity, _ = permutation[key]
            if activity.id_job == considered_activity.id_job:
                if min_index < key < considered_index:
                    min_index = key
                if considered_index < key < max_index:
                    max_index = key
            key += 1
        return min_index, max_index

    # permute an activity of a job with an activity of another job
    def permute_individual(self, individual):
        permutation_possible = False
        considered_index = considered_permutation_index = 0
        while not permutation_possible:
            considered_index = min_index = max_index = 0
            while max_index - min_index <= 2:
                considered_index = random.randint(0, len(individual) - 1)
                min_index, max_index = self.compute_bounds(individual, considered_index)

            considered_permutation_index = random.randint(min_index + 1, max_index - 1)
            min_index_permutation, max_index_permutation = self.compute_bounds(individual, considered_permutation_index)
            if min_index_permutation < considered_index < max_index_permutation:
                permutation_possible = considered_index != considered_permutation_index

        # permute
        individual[considered_index], individual[considered_permutation_index] = \
            individual[considered_permutation_index], individual[considered_index]
        return individual

    # move an acitivity
    def move_individual(self, individual):
        considered_index = min_index = max_index = 0
        while max_index - min_index <= 2:
            considered_index = random.randint(0, len(individual) - 1)
            min_index, max_index = self.compute_bounds(
                individual, considered_index)
        # find the index to be inserted
        new_index = random.randint(min_index + 1, max_index - 1)
        while considered_index == new_index:
            new_index = random.randint(min_index + 1, max_index - 1)
        # move
        individual.insert(new_index, individual.pop(considered_index))
        return individual

    def evolve_individual(self, individual, mutation_probability, permutation_probability, move_probability):
        future_individual = copy.deepcopy(individual)
        if random.randint(0, 100) < mutation_probability:
            future_individual = self.mutate_individual(future_individual)
        if random.randint(0, 100) < permutation_probability:
            future_individual = self.permute_individual(future_individual)
        if random.randint(0, 100) < move_probability:
            future_individual = self.move_individual(future_individual)
        return future_individual

    # selection
    @staticmethod
    def run_tournament(population, total=10):
        # total can't be bigger than current population
        assert total <= len(population)
        new_population = []
        while len(new_population) < total:
            first_individual = population[random.randint(0, len(population) - 1)]
            second_individual = population[random.randint(0, len(population) - 1)]
            if first_individual.fitness.values[0] < second_individual.fitness.values[0]:
                new_population.append(first_individual)
                population.remove(first_individual)
            else:
                new_population.append(second_individual)
                population.remove(second_individual)
        del population
        return new_population

    # run simulation
    def run_simulation(self, individual):
        total_time, list_time = self.compute_time(individual)
        previous_machine_id = 1
        result_file_content = "Job ID, machine ID, start time, end time, total time"
        for key, (individual_activity, individual_operation) in enumerate(individual):
            activity = self.__jobs[individual_activity.id_job - 1].get_activity(individual_activity.id_activity)
            operation = activity.get_operation(individual_operation.id_operation)
            operation.time = list_time[key]
            if(operation.id_operation == -1):
                print(colored("[break down]", "red"),"[time", operation.time, "seconds], machine", operation.id_machine,"# break down for ", operation.duration)
            else:
                diff = abs(CNC_LOCATION_COLOMN[operation.id_machine]-CNC_LOCATION_COLOMN[previous_machine_id])
                if diff == 0:
                    print(colored("[simulation]job", "cyan"), "job dosn't need to move")
                elif diff == 1:
                    print(colored("[simulation]job", "cyan"), "job moves from", operation.id_machine, "to",
                        previous_machine_id, ", taking", self.__rgv_config.RGV_movement_1_time, "unit time.")
                elif diff == 2:
                    print(colored("[simulation]job", "cyan"), "job moves from", operation.id_machine, "to",
                        previous_machine_id, ", taking", self.__rgv_config.RGV_movement_2_time, "unit time.")
                elif diff == 3:
                    print(colored("[simulation]job", "cyan"), "job moves from", operation.id_machine, "to",
                        previous_machine_id, ", taking", self.__rgv_config.RGV_movement_3_time, "unit time.")
                previous_machine_id = operation.id_machine
                print(colored("[simulation]operation", self.RUN_LABLE_COLOR), "[ time", operation.time, "] machine",
                    operation.id_machine, "is processing job", individual_activity.id_job)
            operation.place_of_arrival = 0
            result_file_content = result_file_content + "\n" + str(individual_activity.id_job) + ", " + str(operation.id_machine) + ", " + str(operation.time) + "," + str(operation.time + operation.duration) + ", " + str(operation.duration)
            activity.terminate_operation(operation)
        return total_time, result_file_content

    RUN_LABLE = "[scheduling]"
    RUN_LABLE_COLOR = "blue"

    # called in main to run GA
    def run_genetic(self, total_population=10, max_generation=100, verbose=False):
        assert total_population > 0, max_generation > 0

        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        # don't print if verbose is set to false
        if not verbose:
            sys.stdout = None

        self.__toolbox.register("individual", self.init_individual, creator.Individual, size=1)
        self.__toolbox.register("mutate", self.mutate_individual)
        self.__toolbox.register("permute", self.permute_individual)
        self.__toolbox.register("evaluate", self.evaluate_individual)

        print(colored(self.RUN_LABLE, self.RUN_LABLE_COLOR), "initializing population...")
        population = self.init_population(total_population)

        best = population[0]
        best.fitness.values = self.evaluate_individual(best)
        print(colored(self.RUN_LABLE, self.RUN_LABLE_COLOR), "evolves for", max_generation, "generations")

        log_file_content = "generation, mutation, best makespan"
        for current_generation in range(max_generation):
            # mutation
            mutation_probability = random.randint(50, 100)
            permutation_probability = random.randint(50, 100)
            move_probability = random.randint(50, 100)
            # evolve
            print(colored("evolving", "green"), "evolving", current_generation + 1, "generation")
            mutants = list(set([random.randint(0, total_population - 1) for _ in
                                range(random.randint(1, total_population))]))
            print(colored("mutation", "red"), "There are", len(mutants), "mutations in this generation")
            for key in mutants:
                individual = population[key]
                population.append(
                    self.evolve_individual(individual, mutation_probability, permutation_probability, move_probability))
            # calculate fitness
            fitnesses = list(map(self.evaluate_individual, population))
            for ind, fit in zip(population, fitnesses):
                ind.fitness.values = fit
                if best.fitness.values[0] > ind.fitness.values[0]:
                    print(colored("better individual", "cyan"), "better individual found, current best time is",
                          ind.fitness.values[0])
                    best = copy.deepcopy(ind)
            population = self.run_tournament(population, total=total_population)
            log_file_content = log_file_content + "\n" + str(current_generation + 1) + "," + str(len(mutants)) + "," + str(best.fitness.values[0])

        print(colored(self.RUN_LABLE, self.RUN_LABLE_COLOR), "finish evolving")
        if self.constraint_order_respected(best):
            print(colored(self.RUN_LABLE, self.RUN_LABLE_COLOR), "best time =", best.fitness.values[0])
            print(colored(self.RUN_LABLE, self.RUN_LABLE_COLOR), "simulating best strategy...")
            total_time, result_file_content = self.run_simulation(best)
            print(colored(self.RUN_LABLE, self.RUN_LABLE_COLOR), "simulation finished")
            print(colored(self.RUN_LABLE, self.RUN_LABLE_COLOR), "GA finished")
        else:
            print(colored(self.RUN_LABLE, self.RUN_LABLE_COLOR), "data does not satisfy constraint")

        # print
        if not verbose:
            sys.stdout = self.__original_stdout

        return total_time, log_file_content, result_file_content
