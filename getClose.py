#!/usr/bin/python

def bestGrouping(xs, target, path):
    routes = []
    for i, x in enumerate(xs):
        newTarget = target - x
        path.append(x)
        if not xs[1:] or newTarget <= 0:
            routes.append((newTarget, path[:]))
            path.pop()
            continue
        bestGrouping(xs[1:], newTarget, path)
        routes.append((newTarget, path[:]))
        path.pop()
    print("%-20s %-20s" % (xs[1:], min(routes)))
    return min(routes)
