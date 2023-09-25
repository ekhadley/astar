from grid import *
import heapq
import time

gsize = (90, 90)
gp = (random.randint(0, gsize[0]-1), random.randint(0, gsize[1]-1))
start = (random.randint(0, gsize[0]-1), random.randint(0, gsize[1]-1))


def aStar1(g, start, dScale=1, heuristicScale=1, show=True):
    startNode = node(g, start, 0, None, dScale=dScale, hScale=heuristicScale)
    nodes = [startNode]
    checked = [[0 for x in range(g.shape[0])] for y in range(g.shape[1])]
    checked[start[1]][start[0]] = startNode
    best = startNode
    while best.pos != g.gp:
        best = None
        for n in nodes:
            for e in n.neighbors(checked):
                x, y = e.pos
                if checked[y][x]==0 and (best==None or e.cost+e.heuristic < best.cost+best.heuristic):
                    best = e
        
        nodes.append(best)
        x, y = best.pos
        checked[y][x] = best
        if show:
            bpath = constructPath(best, start)
            cv2.imshow("g", g.show(steps=bpath, mark=np.nonzero(checked)))
            cv2.waitKey(1)
    if show: return bpath, checked
    return constructPath(best, start), checked

def aStar2(g, start, dScale=1, heuristicScale=1, show=True):
    nodes = []
    startNode = node(g, start, 0, None, dScale=dScale, hScale=heuristicScale)
    heapq.heappush(nodes, (0, startNode))
    
    checked = [[0 for x in range(g.shape[0])] for y in range(g.shape[1])]
    checked[start[1]][start[0]] = startNode
    
    best = startNode
    while best == None or best.pos != g.gp:
        fScore, best = heapq.heappop(nodes)
        for nbr in best.neighbors(checked):
            x, y = nbr.pos
            if (best.pos[0]-x)*(best.pos[1]-y)==0: d = 1 
            else: d = 1.414
            d *= dScale
            if best.cost+d <= nbr.cost:
                nbr.cameFrom = best
                nbr.cost = best.cost+d
                if checked[y][x] == 0:
                    heapq.heappush(nodes, (nbr.cost+nbr.heuristic, nbr))
                    checked[y][x] = nbr
        
        if show:
            bpath = constructPath(best, start)
            cv2.imshow("g", g.show(steps=bpath, mark=np.nonzero(checked)))
            cv2.waitKey(1)
    if show: return bpath, checked
    return constructPath(best, start), checked

while 1:
    gp = (random.randint(0, gsize[0]-1), random.randint(0, gsize[1]-1))
    g = grid(gsize, 13, start, goalPosition=gp)
    for i in range(6):
        o = [1, 0] if random.uniform(0,1) > .5 else [0, 1]
        wp1 = np.int32([random.randint(1, gsize[0]-1), random.randint(1, gsize[1]-1)])
        wp2 = np.int32([random.randint(1, gsize[0]-1), random.randint(1, gsize[1]-1)])
        wp1o = wp1 + np.int32(o)
        wp2o = wp2 + np.int32(o)
        g.buildWall(tuple(wp1), tuple(wp2))
        g.buildWall(tuple(wp1o), tuple(wp2o))

    while gp in g.walls:
        gp = (random.randint(0, gsize[0]-1), random.randint(0, gsize[1]-1))
    while start in g.walls:
        start = (random.randint(0, gsize[0]-1), random.randint(0, gsize[1]-1))

    t = time.time()
    bp2, ch2 = aStar2(g, start, dScale=.5)
    print(f"aStar2 found: {bp2} in {time.time()-t:.5f}")
    cv2.imshow("g", g.show(steps=bp2, mark=np.nonzero(ch2)))
    cv2.waitKey(0)