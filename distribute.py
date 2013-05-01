#!/usr/bin/python
import sys
import math

def distributeWorkload(tasks, machines):
    """Given a list of tasks and machines to assign them to, distributes the
    tasks across the machines minimizing maximum runtime.

    Expected Return:
        A dictionary of machine ids => list of tasks

    Expected Arguments:
        tasks:
            Is a dictionary of task ids => task run times

        machines:
            Is a dictionary of machine ids => machine speeds
    """
    assignments = {}

    workload = sum(tasks.values())
    power = sum(machines.values())
    multiplier = workload / power
    best_dist = {m : (multiplier * s) for m, s in machines.items()}

    #Assign "Perfect" values
    for t in tasks:
        if tasks[t] in best_dist.values():
            for m, i in best_dist.items():
                if i == tasks[t] and m not in assignments:
                    assignments[m] = [t]
                    tasks.pop(t)
                    machines.pop(m)

    sorted_tasks = sorted(tasks.items(), key=lambda x: x[1], reverse=True)
    sorted_machines = sorted(machines.items(), key=lambda x: x[1], reverse=True)

    for m, s in sorted_machines:
        workassigned = 0
        ts = []
        while sorted_tasks and abs(best_dist[m] - workassigned) > abs (best_dist[m] - workassigned - sorted_tasks[0][1]):
            workassigned += sorted_tasks[0][1]
            ts.append(sorted_tasks.pop(0)[0])
        assignments[m] = ts


    return assignments


def readInputFile(filename):
    with open(filename, 'r') as f:
        #Throw away first two lines since they are not needed
        f.readline()
        f.readline()

        #Next two lines contain our task processing times and machine speeds
        #Note: tasks are 1 indexed
        tasks = {i : int(t) for i, t in enumerate(f.readline().split())}
        #Make sure to put machine number with its speed
        machines = {i : int(s) for i, s in enumerate(f.readline().split())}

    return tasks, machines


def printResults(res, tasks, machines):
    #First of all sort our result
    res_keys = sorted(res.keys())

    max_time = 0
    #Print task ids for each machine
    #Additionally calculate runtime for each machine and keep the longest
    for m in res_keys:
        print(" ".join(map(str, res[m])))

        #Calculate runtime
        total_time = 0
        for t in res[m]:
            total_time += tasks[t]

        total_time /= machines[m]
        max_time = max(total_time, max_time)

    print("%0.4f" % max_time)


def main():
    #Get file from args
    inputFile = sys.argv[1]

    #Parse the input file
    tasks, machines = readInputFile(inputFile)

    #Distribute tasks to machines
    result = distributeWorkload(tasks, machines)

    #Output our results
    printResults(result, tasks, machines)


if __name__ == '__main__':
    main()



