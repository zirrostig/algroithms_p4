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

    # print(multiplier)
    #Int so that our "Perfect" value can actually be matched to a task
    best_dist = {m : int(multiplier * s) for m, s in machines.items()}

    #Assign "Perfect" values
    # for t in tasks:
    #     if tasks[t] in best_dist.values():
    #         for m, i in best_dist.items():
    #             if i == tasks[t] and m not in assignments:
    #                 assignments[m] = [t]
    #                 tasks.pop(t)
    #                 machines.pop(m)

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
    best_dist = {m : multiplier * s for m, s in machines.items()}
    print(multiplier, file=sys.stderr)

    def shuf_assign(min_runs, max_runs):
        best_run = None
        i = 0
        while (i < max_runs) and (not (i > min_runs and best_run is not None)):
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

            if i == max_runs - 1:
                for tk in tsks:
                    m = random.randint(0, len(machines) - 1)
                    if m in assignments:
                        assignments[m].append(tk[0])
                    else:
                        assignments[m] = [tk[0]]
                best_assign = assignments

        return best_assign

    def sort_assign():
        assignments = distributeWorkload(tasks, machines)

        #Check for full assignment
        used_tasks = [t for tvs in assignments.values() for t in tvs]
        not_used = []
        for tk in tasks.keys():
            if tk not in used_tasks:
                not_used.append(tk)

        if not_used:
            for tk in not_used:
                m = random.randint(0, len(machines) - 1)
                if m in assignments:
                    assignments[m].append(tk)
                else:
                    assignments[m] = [tk]

        return assignments


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

            max_run_time = max(m1ts / m1_speed, m2ts / m2_speed)

            m1off = m1ts - best_dist[m1]
            m2off = m2ts - best_dist[m2]

            #Swap
            m1off_swap = t2_time - t1_time
            m2off_swap = t1_time - t2_time

            #Try swaping first
            if m1s and m2s and \
               ((m1off + m1off_swap < 0) or (abs(m1off + m1off_swap) < abs(m1off))) and \
               ((m2off + m2off_swap < 0) or (abs(m2off + m2off_swap) < abs(m2off))):
                #Swap
                # print("<=>", file=sys.stderr)
                dist[m1].remove(t1)
                dist[m2].append(t1)
                dist[m2].remove(t2)
                dist[m1].append(t2)
            elif m2s and max((m1ts + t2_time) / m1_speed, (m2ts - t2_time) / m2_speed) < max_run_time:
                #m1 Steals from m2
                # print("<-", file=sys.stderr)
                dist[m1].append(t2)
                dist[m2].remove(t2)
            elif m1s and max((m2ts + t1_time) / m2_speed, (m1ts - t1_time) / m1_speed) < max_run_time:
                #m2 Steals from m1
                # print("->", file=sys.stderr)
                dist[m2].append(t1)
                dist[m1].remove(t1)
            elif m1s and m2s and \
                 math.exp(-(max(m1off + m1off_swap, m2off + m2off_swap))/(temp/(0.01*orig_temp))) > random.random():
                 # (abs(m1off + m1off_swap) < 0.1 * best_dist[m1]) and \
                 # (abs(m2off + m2off_swap) < 0.1 * best_dist[m2]) and \
                #Swap anyways
                # print("<<->>", temp, file=sys.stderr)
                dist[m1].remove(t1)
                dist[m2].append(t1)
                dist[m2].remove(t2)
                dist[m1].append(t2)

            #Drop temp
            temp -= 1
        return dist

    #Assign a temperature if none was given
    if temp is None:
        temp = (len(tasks)**3)
        temp = min(temp, 1000000)
        # temp = 1000000

    #Get a random distribution to start with
    assignmentshuf = shuf_assign(100, 10000)
    # assignmentsort = sort_assign()
    assignmentshuf = anneal(assignmentshuf, temp)
    # assignmentsort = anneal(assignmentsort, temp)

    return assignmentshuf

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


def calc_run_time(res, tasks, machines):
    max_time = 0
    for m in res:
        #Calculate runtime
        total_time = 0
        for t in res[m]:
            total_time += tasks[t]

        total_time /= machines[m]
        max_time = max(total_time, max_time)

    return max_time

def printResults(res, tasks, machines):
    #First of all sort our result
    res_keys = sorted(res.keys())

    max_time = 0
    #Print task ids for each machine
    #Additionally calculate runtime for each machine and keep the longest
    for m in res_keys:
        print(" ".join(map(str, res[m])))

    print("%0.4f" % calc_run_time(res, tasks, machines))

def main():
    #Get file from args
    inputFile = sys.argv[1]

    #Parse the input file
    tasks, machines = readInputFile(inputFile)

    #Distribute tasks to machines
    # result = distributeWorkload(tasks, machines)
    # result1 = distributeWorkload(tasks, machines)
    result2 = distribute_with_annealing(tasks, machines)

    #Output our results
    # printResults(result1, tasks, machines)
    # print()
    printResults(result2, tasks, machines)


if __name__ == '__main__':
    main()



