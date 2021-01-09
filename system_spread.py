import json
import math
import MFRep
import numpy as np
import requests

stationTypeExclude = ["Outpost", "Fleet Carrier", "Planetary Port", "Planetary Outpost", "Mega ship"]


class Commodity:
    def __init__(self, id, name, average):
        self.id = id
        self.name = name
        self.avg = average


class System:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Station:
    def __init__(self, id, name, s):
        self.id = id
        self.name = name
        self.system = next(i.name for i in systems if i.id == s)


class Target:
    def __init__(self, id, direction):
        self.id = id
        self.name = next(i.name for i in commodities if i.id == id)
        self.station = None
        self.price = 1000000000 if direction else 0
        self.quantity = 0

    def updateTarget(self, s, p, q):
        try:
            self.station = next(i for i in stations if i.id == s)
        except StopIteration:
            return
        self.price = p
        self.quantity = q


commodities = set()
with open("commodities.json") as f:
    for c in json.loads(f.read()):
        commodities.add(Commodity(c["id"], c["name"], c["average_price"]))
    f.close()

print("Commodity Ingest Complete")

systems = set()
with open("systems_populated_EDDB.json") as f:
    for s in json.loads(f.read()):
        systems.add(System(s["id"], s["name"]))
    f.close()

print("System Ingest Complete")

stations = set()
with open("stationsEDDB.json") as f:
    for s in json.loads(f.read()):
        if s["type"] in stationTypeExclude:
            continue
        stations.add(Station(s["id"], s["name"], s["system_id"]))
    f.close()

print("Station Ingest Complete")

imports = {i.id: Target(i.id, 0) for i in commodities}
exports = {i.id: Target(i.id, 1) for i in commodities}

data = np.genfromtxt("listings.csv", delimiter=',', dtype=int)

count = 0
for i in range(len(data[1:, ])):
    row = data[i+1, ]
    comm = row[2]
    supply, demand = row[3], row[7]
    price = row[5] if supply else row[6] if demand else 0

    if supply and price < exports[comm].price:
        exports[comm].updateTarget(row[1], price, supply)

    if demand and price > imports[comm].price:
        imports[comm].updateTarget(row[1], price, demand)

    if count % 50000000 == 0:
        print("{}%".format(round(100 * i/len(data[1:, ]), 2)))

'''        for i in (i.station.name for i in imports.values() if i.station):
            print("import", i, end=' ')
        print()
        for i in (i.station.name for i in exports.values() if i.station):
            print("import", i, end=' ')
        print()'''

for i, j in imports.items():
    k = exports[i]
    delta = j.price - k.price
    cap = min(k.quantity, j.quantity)
    source = k.station
    dest = j.station
    if delta and cap:
        print("Trade: {} from {}/{} to {}/{} ({}Cr/ton profit)".format(j.name, source.system, source.name, dest.system, dest.name, delta))
    input()

data = None
