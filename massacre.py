import json
import math
import MFRep
import numpy as np
import csv

stateExclude = ["War", "Civil War", "Bust", "Election"]
stationTypeExclude = ["Fleet Carrier", "Planetary Port", "Planetary Outpost", "MegaShip"]
allied = MFRep.getMinorFactions(90)
maxDist = 10000
facsThresh = 10

anarchies = {}
systems = set()

print("{} Allied factions found".format(len(allied)))

def dist(c1, c2):
    x = (c2[0] - c1[0])**2
    y = (c2[1] - c1[1])**2
    z = (c2[2] - c1[2])**2
    s = x + y + z
    return math.sqrt(s)


class System:
    def __init__(self, name, coords, stations, factions):
        self.name = name
        self.coords = tuple(coords[i] for i in coords)
        self.stations = stations
        self.factions = factions


class Anarchy:
    def __init__(self, name, coords, stations):
        self.name = name
        self.coords = tuple(coords[i] for i in coords)
        self.stations = stations
        self.sources = set()


def anarchyNeighbours(system: System):
    neighbours = {sys.name for sys in anarchies.values() if dist(system.coords, sys.coords) < 10}
    if len(neighbours) == 1:
        (el,) = neighbours
        return el
    else:
        return False


with open("systems.json", "r") as f:
    for sys in json.loads(f.read()):
        try:
            facs = [fac for fac in sys["factions"]]
        except KeyError:
            facs = [sys["controllingFaction"] if sys["controllingFaction"] else ()]
        if not len(facs):
            continue

        flag = False
        for i in facs:
            if not flag:
                try:
                    if i["government"] == "Anarchy":
                        anarchies[sys["name"]] = Anarchy(sys["name"], sys["coords"], len(sys["stations"]))
                        flag = True
                        continue
                except KeyError:
                    continue

        validFacs = 0
        for i in facs:
            remFac = False
            try:
                for j in i["activeStates"]:
                    if j[1] in stateExclude:
                        remFac = True
            except KeyError:
                pass
            if not remFac and i["name"] in allied:
                #print(i["name"])
                validFacs += 1

        if validFacs < 1:
            continue

        #input()

        if len(sys["stations"]):
            try:
                if len([s for s in sys["stations"] if s["distanceToArrival"] < maxDist and s["type"] not in stationTypeExclude]) > 0:
                    systems.add(System(sys["name"], sys["coords"], len(sys["stations"]), validFacs))
            except TypeError:
                continue

    print("anarchy filter complete", len(anarchies), len(systems))

    for sys in systems:
        neighbour = anarchyNeighbours(sys)
        # print(neighbour)
        if neighbour:
            anarchies[neighbour].sources.add(sys.name)
            print(anarchies[neighbour].name, anarchies[neighbour].sources)

'''
    with open("output.csv", "w") as f:
        write = csv.writer(f, delimiter=',', quotechar="|", quoting=csv.QUOTE_MINIMAL)
        for j, k in targets.items():
            write.writerow(j, *(l.name for l in k))
            
            '''
