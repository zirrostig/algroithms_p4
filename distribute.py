#/usr/bin/python
import sys


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

    #Put code here

    return assignments


def readInputFile(filename):
    with open(filename, 'r') as f:
        #Throw away first two lines since they are not needed
        f.readline()
        f.readline()

        #Next two lines contain our task processing times and machine speeds
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



