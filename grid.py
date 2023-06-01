import cv2, math, random, numpy as np


class grid():
    def __init__(self, shape, tileSize, start, goalPosition=None):
        self.shape = shape
        self.start = start
        width, height = self.shape
        self.tileSize = tileSize
        self.walls = []
        self.baseIm = None
        if goalPosition==None:
            self.gp = (random.randint(0,width), random.randint(0,height))
        else: self.gp = goalPosition

    def getWeight(self, pos):
        #assert type(pos)==tuple, "wtf???"
        if self.inBounds(pos) and pos not in self.walls:
            return np.linalg.norm(np.int32(pos)-np.int32(self.gp))
        else: return 1e6

    def inBounds(self, pos):
        return -1<pos[0]<self.shape[0] and -1<pos[1]<self.shape[1]

    def addWall(self, pos):
        #self.walls = np.append(self.walls, np.int32(pos), axis=0)
        self.walls.append(pos)

    def buildWall(self, p1, p2):
        p1x, p1y = p1
        p2x, p2y = p2
        steps = round(np.linalg.norm([p1x-p2x,p1y-p2y]))+2
        xs = np.linspace(p1x, p2x, num=steps)
        ys = np.linspace(p1y, p2y, num=steps)
        for i in range(steps):
            p = (round(xs[i]), round(ys[i]))
            if p not in self.walls: self.addWall(p)

    def inBounds(self, pos):
        return -1<pos[0]<self.shape[0] and -1<pos[1]<self.shape[1]

    def show(self, scale=1, start=None, lines=True, grade=False, steps=None, mark=None):
        width, height = self.shape
        ts = round(self.tileSize*scale)
        gpx, gpy = self.gp
        if type(self.baseIm) == type(None):
            im = np.ones((ts*height, ts*width, 3))*.13
            im = cv2.rectangle(im, [ts*gpx, ts*gpy], [ts*(gpx+1), ts*(gpy+1)], color=(.35,1,0), thickness=-1)
            sx, sy = self.start
            im = cv2.rectangle(im, [ts*sx, ts*sy], [ts*(sx+1), ts*(sy+1)], color=(1,.5,0), thickness=-1)
            for (wx, wy) in self.walls:
                im = cv2.rectangle(im, [ts*wx, ts*wy], [ts*(wx+1), ts*(wy+1)], color=(.15,.15,1), thickness=-1)
            if lines:
                for i in range(0, ts*width, ts):
                    im = cv2.line(im, [i, 0], [i, ts*height], color=(.5,.5,.5), thickness=1)
                for i in range(0, ts*height, ts):
                    im = cv2.line(im, [0, i], [ts*width, i], color=(.5,.5,.5), thickness=1)
            if grade:
                maxx = np.linalg.norm([self.shape])
                for x in range(0, ts*width, ts):
                    for y in range(0, ts*height, ts):
                        c = np.int32([x+ts/2, y+ts/2])
                        w = self.getWeight((x/ts, y/ts))
                        im = cv2.circle(im, c, ts//10, color=(0, 1-w/maxx, w/maxx), thickness=-1)
            if grade:
                maxx = np.linalg.norm([self.shape])
                for x in range(0, ts*width, ts):
                    for y in range(0, ts*height, ts):
                        c = np.int32([x+ts/2, y+ts/2])
                        w = self.getWeight((x/ts, y/ts))
                        im = cv2.circle(im, c, ts//10, color=(0, 1-w/maxx, w/maxx), thickness=-1)
            self.baseIm = im
        im = np.array(self.baseIm, copy=True)
        if mark != None: 
            for i in range(len(mark[0])):
                mx, my = mark[1][i], mark[0][i]
                im = cv2.circle(im, [ts*mx+ts//2, ts*my+ts//2], ts//2, color=(.6, .6, .6), thickness=1)
        if steps != None:
            for i, (stepx, stepy) in enumerate(steps):
                #im = cv2.circle(im, [stepsx, stepsy], round(ts/2), color=(1,1,1), thickness=2)
                if i != 0: im = cv2.line(im, [ts*stepx+ts//2, ts*stepy+ts//2], [ts*steps[i-1][0]+ts//2, ts*steps[i-1][1]+ts//2], color=(1,1,1), thickness=ts//2)
                else: im = cv2.circle(im, [ts*stepx+ts//2, ts*stepy+ts//2], ts//2, color=(1, 1, 1), thickness=-1)
        return im

def constructPath(n, start):
    step = n
    path = []
    while step.pos != start:
        path.append(step.pos)
        step = step.cameFrom
    path.append(step.pos)
    return path

dirs = [(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1)]
class node():
    def __init__(self, g, pos, cost, cameFrom, dScale=1, hScale=1):
        self.pos = pos
        self.cost = cost
        self.heuristic = g.getWeight(pos)*hScale
        self.cameFrom = cameFrom
        self.dScale = dScale
        self.hScale = hScale
        self.nbrs = None
        self.g = g

    def neighbors(self, others=None):
        if self.nbrs == None:
            self.nbrs = []
            for dir in dirs:
                dx, dy = dir
                x, y = self.pos
                if self.g.inBounds((x+dx, y+dy)):
                    if others[y+dy][x+dx] == 0:
                        if dx*dy==0: dist = 1 
                        else: dist= 1.414
                        self.nbrs.append(node(self.g, (x+dx,y+dy), self.cost+dist*self.dScale, self, dScale=self.dScale, hScale=self.hScale))
                    else:
                        self.nbrs.append(others[y+dy][x+dx])
        return self.nbrs
    
    def __lt__(self, other: object) -> bool:
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)
    #def __eq__(self, other: object) -> bool:
    #    return (self.cost + self.heuristic) == (other.cost + other.heuristic)