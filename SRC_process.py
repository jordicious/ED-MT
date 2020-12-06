from tkinter import Tk
from tkinter.filedialog import askopenfilename
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.transforms as mtransforms
import numpy as np
from math import sqrt, sin, cos, tan, asin, acos, atan, degrees, radians
import random
import test
from PIL import Image


def rotate(vector, axis, theta):
    if axis == 'z':
        rotationMatrix = np.reshape([
            cos(theta), -sin(theta), 0,
            sin(theta), cos(theta), 0,
            0, 0, 1
        ], (3, 3))

    elif axis == 'y':
        rotationMatrix = np.reshape([
            cos(theta), 0, sin(theta),
            0, 1, 0,
            -sin(theta), 0, cos(theta)
        ], (3, 3))

    return np.sum(np.multiply(rotationMatrix, vector), 1)


def rand():
    r = random.randint(0, 100)
    return remap(r, 0, 100, -1, 1)


def remap(value, low1, high1, low2, high2):
    return low2 + (value - low1) * (high2 - low2) / (high1 - low1)


class Rock:
    def __init__(self, uid, x, y, z, value):
        self.uid = uid
        self.x = x
        self.y = y
        self.z = z
        self.value = value

    def coords(self):
        return self.x, self.y, self.z


class Vector:
    def __init__(self, x1, x2, y1, y2, z1, z2):
        self.x = x2 - x1
        self.y = y2 - y1
        self.z = z2 - z1
        self.mag = sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
        if self.x == 0:
            self.theta = 90 * np.sign(self.y)
        else:
            self.theta = degrees(atan(self.y / self.x))
            if self.x < 0:
                self.theta += 180 * np.sign(self.y)
        self.phi = degrees(asin(self.z/self.mag))

    def normalize(self):
        return Vector(0, (self.x / self.mag), 0, (self.y / self.mag), 0, (self.z / self.mag))

    def Angle(self, initVec):
        v1, v2 = initVec.normalize(), self.normalize()
        return degrees(acos((v1.x * v2.x) + (v1.y * v2.y) + (v1.z * v2.z)))


def navball(target: Vector, originRaw: Vector):
    target, origin = target.normalize(), originRaw.normalize()
    # print(origin.theta - target.theta)

    coords = ([origin.x, origin.y, origin.z])
    # print(coords)
    rZCoords = rotate(coords, 'z', radians(-target.theta))
    newCoords = rotate(rZCoords, 'y', radians(target.phi))

    # print(newCoords)

    newOrigin = Vector(0, newCoords[0], 0, newCoords[1], 0, newCoords[2])
    return newOrigin


'''target = Vector(0, 1, 0, 1, 0, 1.4142)
origin = Vector(0, 0, 0, -2, 0, 0)

print(navball(target, origin))

input()'''
rocks = {}

Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
data = np.genfromtxt(filename, delimiter=',')
data[1, 2] = -20

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.autoscale(enable=False)
ax.set_xlim(-25, 25)
ax.set_ylim(-25, 25)
ax.set_zbound(-25, 25)

xs, ys, zs = data[1:, 1], data[1:, 2], data[1:, 3]
col = data[1:, 4]
size = data[1:, 5]**2*100
ax.scatter(xs, ys, zs, s=size, c=col, alpha=1)

ax.set_xlabel('X (km)')
ax.set_ylabel('Y (km)')
ax.set_zlabel('Z (km)')

for i in range(len(data[1:, ])):
    rocks[i] = Rock(i, data[i + 1, 1], data[i + 1, 2], data[i + 1, 3], data[i + 1, 4])


def drawPath(pathList: list, delay):
    curr = rocks[0].coords()
    pathDraw = []
    for i in pathList[1:]:
        target = rocks[i].coords()
        pathDraw.append(plt.plot((curr[0], target[0]), (curr[1], target[1]), (curr[2], target[2]), c=(1, 0, 0), alpha=0.4))
        plt.draw()
        if delay:
            plt.pause(delay)
        curr = target
    return pathDraw


def genNav(pathList: list):
    curr = rocks[0].coords()

    for i in pathList[1:]:
        index = pathList.index(i)
        target = rocks[i].coords()

        nextDir = Vector(curr[0], target[0], curr[1], target[1], curr[2], target[2])
        origin = Vector(curr[0], 0, curr[1], 0, curr[2], 0)
        navDir = navball(nextDir, origin)
        # print(-navDir.y, navDir.z)

        # input()

        yaw, pitch = navDir.theta, navDir.phi

        print(index, "Yaw {} degrees / Pitch {} degrees".format(yaw, pitch))

        x = int(remap(-navDir.y, -1, 1, 10, 340))
        y = int(remap(-navDir.z, -1, 1, 10, 340))
        side = np.sign(navDir.x)

        # print(x,y, side)

        sphere = Image.open("sphere.png").resize((500, 500), Image.ANTIALIAS)
        reticle = Image.open("reticle_f.png" if side > 0 else "reticle.png").resize((150, 150), Image.ANTIALIAS)
        # axes range from 10 to 340
        sphere.paste(reticle, (x, y), reticle)
        sphere.save("navballs/" + str(index) + ".png")

        curr = target


def selectNext(curr, rocksRem, prevVec, c1, c2, c3, first):
    metricHigh = 0
    minVal = 35
    maxVal = max(data[1:, 4])
    maxRange = 7
    maxAngle = 90
    timeout = 0
    # print("next")
    while metricHigh == 0:
        for i in rocksRem:
            if rocks[i].value < minVal:
                continue
            v = Vector(curr.x, rocks[i].x, curr.y, rocks[i].y, curr.z, rocks[i].z)
            if v.mag > maxRange or Vector(0, rocks[i].x, 0, rocks[i].y, 0, rocks[i].z).mag > 20:
                continue
            angle = abs(prevVec.theta - v.theta)
            angle -= 180 if angle > 180 else 0

            # print(angle, v.theta, prevVec.theta)
            if first:
                metric = remap(v.mag, 0, maxRange, c2, 0) + remap(rocks[i].value, minVal, maxVal, 0, c3)
            elif angle > maxAngle:
                continue
            metric = remap(angle, 0, maxAngle, c1, 0) + remap(v.mag, 0, maxRange, c2, 0) + remap(rocks[i].value, minVal, maxVal, 0, c3)

            # line = plt.plot((curr.x, rocks[i].x), (curr.y, rocks[i].y), (curr.z, rocks[i].z), c=(0,0,0))
            # plt.pause(0.05)
            # line.pop(0).remove()

            # print(metric)

            if metric > metricHigh:
                next = i
                metricHigh = metric

        if metricHigh > 0:
            # print("    Selected UID {} with fit {}".format(next, metricHigh))
            return next, angle, v.mag, rocks[i].value

        maxAngle += 5 if maxAngle < 175 else 0
        maxRange += 0.2 if maxRange < 9 else 0
        # minVal -= 2 if minVal > 0 else 0
        timeout += 1
        if timeout > 25:
            return 0, 0, 0, 0
        # print(maxAngle, minVal, maxRange)


def genPath(c1, c2, c3, col):
    length = 0
    value = 0
    turn = 0
    path = [0]
    lines = []

    rocksRem = [i for i in range(len(rocks))]
    rocksRem.remove(0)
    first = 1

    current = rocks[0]
    prevVec = Vector(0, 0, 0, 1, 0, 0)

    while True:
        next, angle, mag, val = selectNext(current, rocksRem, prevVec, c1, c2, c3, first)
        first = 0
        if next:
            turn += angle
            length += mag
            value += val

            path.append(next)
            rocksRem.remove(next)
            # lines.append(plt.plot((current.x, rocks[next].x), (current.y, rocks[next].y), (current.z, rocks[next].z), c=((1-col), 0, col)))
            # plt.pause(0.01)
            prevVec = Vector(current.x, rocks[next].x, current.y, rocks[next].y, current.z, rocks[next].z)
            current = rocks[next]
        else:
            break

    # plt.pause(0.01)
    # lines = [j.pop(0).remove() for j in lines]
    if value*0.5 < 750:
        return 0, 0, 0, 0
    return path, length, turn, value


def genetic(genCap, timer):
    plt.draw()
    plt.pause(.5)
    gen = 1000
    count = 0
    highscore = 0
    goodPath = []
    prevIter = []
    dupecount = 0
    timeout = timer
    genpaths = []

    c1, c2, c3 = gen, gen, gen

    while gen > 1:
        c1_ = (gen) * rand() + c1
        c2_ = (gen) * rand() + c2
        c3_ = (gen) * rand() + c3

        path, length, turn, value = genPath(c1_, c2_, c3_, 0.5)
        if path:
            score = 100000/turn
            print(score)
            genpaths.append((path, score, (c1_, c2_, c3_), (length, turn, value)))
            # print("    Qty", len(path), "score", score)
        else:
            timeout -= 1
            # print("Timeout: ", timeout)

        if len(genpaths) > genCap or timeout == 0:
            for i in range(len(genpaths)):
                if genpaths[i][1] > highscore:
                    goodPath = genpaths[i][0]
                    (c1, c2, c3) = genpaths[i][2]
                    (bLen, bTurn, bVal) = genpaths[i][3]
            gen *= 0.9
            genpaths = []
            count += 1
            timeout = timer/count
            print("Generation {} complete, new base coefficients: {} {} {}".format(count, c1, c2, c3))
            print("    Timeout set to", timeout)

            if goodPath == prevIter:
                dupecount += 1
                print("    Dupes:", dupecount)
            else:
                dupecount = 0
            if dupecount >= 3:
                break
            prevIter = goodPath

    return goodPath, bLen, bTurn, bVal


# path, length, turn, value = genetic(50, 1000)
# print("\nFINAL: Path generated: dist {}km, turn {} degrees, yield {}t".format(length, turn, value*0.5), "\n    ", path) if path else ("Failed to generate path")


cmd = 'go'
line = []
prev = 0
plt.draw()
tonnage = 0
path = [0, 10, 3, 1, 4, 60, 59, 58, 57, 56, 55, 54, 53, 48, 50, 45, 38, 39, 44, 42, 35, 34, 32, 26, 28, 25, 23, 22, 21, 20, 17, 13, 12, 7, 61, 8, 6, 5]

if len(path) <= 1:
    while cmd:
        cmd = input("Estimated Tonnage: " + str(tonnage) + ">>")
        if cmd:
            path.append(int(cmd))
            curr = rocks[prev]
            target = rocks[int(cmd)]
            line.append(plt.plot((curr.x, target.x), (curr.y, target.y), (curr.z, target.z), c=(1, 0, 0)))
            tonnage += target.value * 0.5

            plt.draw()
            plt.pause(0.01)
            prev = int(cmd)


line = [i.pop(0).remove() for i in line]
lines = drawPath(path, 0.05)
print(path)

if input() == 'generate':
    genNav(path)

plt.show()
