#!/usr/bin/python
import sys

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

def parseResults(f):
    lines = f.read().splitlines()
    reported_runtime = float(lines.pop(-1))
    results = {m: [int(t) for t in ts.split()] for m, ts in enumerate(lines)}

    return results, reported_runtime

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: ./testResult.py inputFile <resultsFile|STDIN>", file=sys.stderr)
    elif len(sys.argv) < 3:
        f = sys.stdin
    else:
        f = open(sys.argv[2], 'r')

    #Read given input
    tasks, machines = readInputFile(sys.argv[1])

    #Read in given results
    results, reported_time = parseResults(f)
    if f is not sys.stdin:
        f.close()

    #Check results
    failed = False

    #Check machine count
    if len(results) > len(machines):
        print('Results is using too many machines')
        failed = True

    #Check task usage
    usedTasks = [t for ts in results.values() for t in ts]

    #Make sure a task is not assigned twice
    if len(set(usedTasks)) != len(usedTasks):
        used = usedTasks[:]
        #Get duplicate tasks
        for i in set(used):
            used.remove(i)

        print("Tasks %s used more than once" % list(set(used)))
        failed = True

    #Make sure all tasks are used
    for t in tasks.keys():
        if t not in usedTasks:
            print("Task %d not used in result" % t)
            failed = True


    #Calculate runtime
    actual_time = 0
    for m in results:
        #Quick check handling case when too many machines where given
        if m in machines:
            total_time = 0
            for t in results[m]:
                total_time += tasks[t]
            total_time /= machines[m]
            actual_time = max(total_time, actual_time)

    if actual_time != reported_time:
        print("Reported time of %0.4f does not match actual time of %0.4f" % (reported_time, actual_time))
        failed = True

    if failed:
        print("Result input failed")
    else:
        print("Result input accepted")
