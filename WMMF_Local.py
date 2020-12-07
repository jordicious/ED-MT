import json
import math
import MFRep
import numpy as np
import csv
'''from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt'''

stationTypeExclude = ["Outpost", "Fleet Carrier", "Planetary Port", "Planetary Outpost"]
econExclude = ["Extraction", "Refinery"]
stateExclude = ["War", "Civil War", "Pirate Attack", "Bust", "Election"]
MFacs = MFRep.getMinorFactions(35)
originSys = MFRep.getLastDock()[0]
radius = float(input("Radius >"))
maxDist = 10000


class System:
    def __init__(self, name, coords, stations, factions):
        self.name = name
        self.coords = tuple(coords[i] for i in coords)
        self.distOrig = 0
        self.stations = None
        self.factions = None
        self.stations = {s["name"]: (s["economy"], s["secondEconomy"]) for s in stations if s["type"] not in stationTypeExclude and float(s["distanceToArrival"]) < maxDist and "Missions" in s["otherServices"] and not (s["economy"] in econExclude or s["secondEconomy"] in econExclude)}
        if not len(self.stations):
            self.stations = set()
        self.factions = {fac["name"] for fac in factions if fac["name"] in MFacs and fac["state"] not in stateExclude}
        if not len(self.factions):
            self.factions = set()

    def radius(self, d):
        self.distOrig = d
        return self


def delta(c1, c2):
    return round(math.sqrt((c2[0]-c1[0])**2 + (c2[1]-c1[1])**2 + (c2[2]-c1[2])**2), 2)


def getTargets():
    with open("systems.json", "r") as f:
        systems = set()
        for sys in json.loads(f.read()):
            try:
                facs = [fac for fac in sys["factions"]]
            except KeyError:
                facs = [sys["controllingFaction"] if sys["controllingFaction"] else ()]

            system = System(sys["name"], sys["coords"], sys["stations"], facs)

            if system.name == originSys:
                originCoords = system.coords

            if not system.stations or not system.factions:
                continue

            systems.add(system)

        for sys in systems:
            sys.distOrig = delta(originCoords, sys.coords)
        systems = sorted([s for s in systems if s.distOrig < radius], key=lambda i: i.distOrig)
        f.close()

    if not len(systems):
        print("None Found")
        return None

    for system in systems:
        print("{} ({}ly)".format(system.name, system.distOrig))
        for i in system.stations:
            print("    {} ({}/{})".format(i, system.stations[i][0], system.stations[i][1]))

    targets = 0
    for system in systems:
        targets += len(system.stations)

    print(targets)
    return systems


systems = getTargets()

xs, ys, zs = [sys.coords[0] for sys in systems], [sys.coords[1] for sys in systems], [-sys.coords[2] for sys in systems]
stations = [len(sys.stations) for sys in systems]
factions = [len(sys.factions) for sys in systems]
names = [sys.name for sys in systems]

data = np.transpose(np.vstack((names, xs, ys, zs, stations, factions)))

with open('MWWF.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for row in data:
        writer.writerow(row)
    f.close()


'''fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.autoscale(enable=False)
ax.set_xlim(-300, 300)
ax.set_ylim(-300, 300)
ax.set_zbound(-300, 300)

ax.scatter(xs, ys, zs, s=stations, c=factions, alpha=0.9)
plt.show()
'''

while True:
    input(">")
    dock = MFRep.getLastDock()
    try:
        sys = next(sys for sys in systems if sys.name == dock[0])
    except StopIteration:
        print("You aren't at a listed system")
        continue
    facs = list(sys.factions)

    for i in range(len(facs)):
        print("({}) {}".format(i, facs[i]))
    faction = int(input("Which Faction >"))

    with open("WMMs Log.txt", "a") as f:
        f.writelines("{}/{}/{}\n".format(sys.name, dock[1], facs[faction]))
    f.close()
