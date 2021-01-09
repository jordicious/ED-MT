from tkinter import Tk
from tkinter.filedialog import askopenfilename
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.transforms as mtransforms
import numpy as np
from math import *
import random
from PIL import Image


def removeD(d, key):
    dic = dict(d)
    del dic[key]
    return dic


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
    else:
        return None

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


class Path:
    def __init__(self, path: list):
        self.path = path
        self.length = 0
        for i in range(len(path)):
            if not i:
                continue
            p = rocks[path[i-1]]
            c = rocks[path[i]]
            self.length += Vector(p.x, c.x, p.y, c.y, p.z, c.z).mag


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

plt.draw()
plt.pause(1)

for i in range(len(data[1:, ])):
    rocks[i] = Rock(i, data[i + 1, 1], data[i + 1, 2], data[i + 1, 3], data[i + 1, 4])


def drawPath(pathList: list, delay):
    curr = rocks[0].coords()
    pathDraw = []
    c = ((rand()+1)/2, (rand()+1)/2, (rand()+1)/2)
    for i in pathList[1:]:
        target = rocks[i].coords()
        pathDraw.append(plt.plot((curr[0], target[0]), (curr[1], target[1]), (curr[2], target[2]), c=c, alpha=0.4))
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


def genPaths(n):
    random.seed = random.randint(1, 999999999)
    rocksRem = [i for i in range(len(rocks))]
    rocksRem.remove(0)
    max = int(floor(len(rocksRem)/n))
    lengths = [max]*n
    lengths[-1] += len(rocksRem) % max
    maps = set()

    for i in lengths:
        path = [0]
        for j in range(i):
            sel = random.choice(rocksRem)
            path.append(sel)
            rocksRem.remove(sel)

        maps.add(Path(path))
    return maps


record = (999999, None)

for i in range(100000000):
    paths = genPaths(3)
    lenTotal = sum(i.length for i in paths)
    if lenTotal < record[0]:
        record = (lenTotal, paths)
    print(lenTotal, record[0])


for i in record[1]:
    drawPath(i.path, 0.05)
plt.show()


# print("\nFINAL: Path generated: dist {}km, turn {} degrees, yield {}t".format(length, turn, value*0.5), "\n    ", path) if path else ("Failed to generate path")

