#!/usr/bin/python
import sys
import math
import random

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

    print(multiplier)
    #Int so that our "Perfect" value can actually be matched to a task
    best_dist = {m : int(multiplier * s) for m, s in machines.items()}

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


def distribute_with_annealing(tasks, machines, temp=None):
    workload = sum(tasks.values())
    power = sum(machines.values())
    multiplier = workload / power
    best_dist = {m : int(multiplier * s) for m, s in machines.items()}
    print(multiplier, file=sys.stderr)

    def shuf_assign(runs):
        best_run = None
        i = 0
        while not (i > runs and best_run is not None):
            i += 1
            #Shuffle everything up
            tsks = list(tasks.items())
            machs = list(machines.items())
            random.shuffle(tsks)
            random.shuffle(machs)

            assignments = {}
            for m, s in machs:
                run_time = 0
                work = 0
                ts = []
                while tsks and abs(best_dist[m] - work) > abs(best_dist[m] - work - tsks[0][1]):
                    work += tsks[0][1]
                    ts.append(tsks.pop(0)[0])
                assignments[m] = ts
                #Get a runtime for this machine
                run_time = max(run_time, work/machines[m])

            #Check for full assignment
            full_assignment = True
            used_tasks = [t for tvs in assignments.values() for t in tvs]
            for tk in tasks.keys():
                if tk not in used_tasks:
                    full_assignment = False
                    break

            if full_assignment and (best_run is None or run_time < best_run):
                best_run = run_time
                best_assign = assignments.copy()

        return best_assign

    def anneal(dist, temp):
        machine_count = len(dist)
        orig_temp = temp
        while temp > 0:
            #Pick two machines
            m1 = random.randint(0, machine_count - 1)
            m2 = random.randint(0, machine_count - 1)
            if m1 == m2:
                #Try again if they match
                continue


            #Reducing number of lookups
            m1s = dist[m1]
            m2s = dist[m2]

            #Check if both machines are empty
            if (not m1s) and (not m2s):
                continue

            m1_speed = machines[m1]
            m2_speed = machines[m2]
            m1t = map(tasks.get, m1s)
            m2t = map(tasks.get, m2s)
            m1ts = sum(m1t)
            m2ts = sum(m2t)

            #Pick a task from each machine
            #Check if empty
            if m1s:
                t1 = m1s[random.randint(0, len(m1s) - 1)]
                t1_time = tasks[t1]
            else:
                t1_time = 0

            if m2s:
                t2 = m2s[random.randint(0, len(m2s) - 1)]
                t2_time = tasks[t2]
            else:
                t2_time = 0


            #Determine if the machines should swap tasks, steal, or do nothing
            #Purely task sums for the 'new' assignments
            m1_run_steal = m1ts + t2_time
            m1_run_give = m1ts - t1_time
            m1_run_swap = m1ts - t1_time + t2_time
            m2_run_steal = m2ts + t1_time
            m2_run_give = m2ts - t2_time
            m2_run_swap = m2ts - t2_time + t1_time

            #Gains/Losses for each machine
            m1_steal_delta = (m1_run_steal -  m1ts) / m1_speed
            m1_give_delta = (m1_run_give  -  m1ts) / m1_speed
            m1_swap_delta = (m1_run_swap  -  m1ts) / m1_speed
            m2_steal_delta = (m2_run_steal -  m2ts) / m2_speed
            m2_give_delta = (m2_run_give  -  m2ts) / m2_speed
            m2_swap_delta = (m2_run_swap  -  m2ts) / m2_speed

            #Our gains (or losses) from each operation
            steal1 = m1_steal_delta + m2_give_delta
            steal2 = m1_give_delta + m2_steal_delta
            swap = m1_swap_delta + m2_swap_delta

            # print(m1s)
            # print(t1, t1_time)
            # print(m1_steal_delta, m1_give_delta, m1_swap_delta)
            # print(m2s)
            # print(t2, t2_time)
            # print(m2_steal_delta, m2_give_delta, m2_swap_delta)

            #Choose the best
            if m1s and m2s:
                best = max((swap, 0), (steal1, 1), (steal2, 2))
            elif m1s:
                best = (steal1, 1)
            elif m2s:
                best = (steal2, 2)

            #execute the best if it helps us
            # print(best)
            # print()
            if best[0] < 0:
                if best[1] == 0:
                    #Swap
                    dist[m1].remove(t1)
                    dist[m2].append(t1)
                    dist[m2].remove(t2)
                    dist[m1].append(t2)
                elif best[1] == 1:
                    #m1 Steals from m2
                    dist[m1].append(t2)
                    dist[m2].remove(t2)
                elif best[1] == 2:
                    #m2 Steals from m1
                    dist[m2].append(t1)
                    dist[m1].remove(t1)

            #Drop temp
            temp -= 1
        return dist

    #Assign a temperature if none was given
    if temp is None:
        temp = int(100000000 / len(tasks))
        print(temp, file=sys.stderr)

    #Get a random distribution to start with
    assignments = shuf_assign(100)
    optimized_dist = anneal(assignments, temp)

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
    # result = distributeWorkload(tasks, machines)
    result = distribute_with_annealing(tasks, machines)

    #Output our results
    printResults(result, tasks, machines)


if __name__ == '__main__':
    main()



