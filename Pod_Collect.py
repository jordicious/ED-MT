import os
from pathlib import Path
import json
from time import time

pods = {
    'podcoretissue': [0, "Pod Core Tissue"],
    'poddeadtissue': [0, "Pod Dead Tissue"],
    'podmesoglea': [0, "Pod Mesoglea"],
    'podoutertissue': [0, "Pod Outer Tissue"],
    'podshelltissue': [0, "Pod Shell Tissue"],
    'podsurfacetissue': [0, "Pod Surface Tissue"],
    'podtissue': [0, "Pod Tissue"],
}

dirpath = os.path.expanduser("~") + "/Saved Games/Frontier Developments/Elite Dangerous"
paths = sorted([i for i in Path(dirpath).iterdir() if os.path.getmtime(i) > time() - 604800], key=os.path.getmtime)

for i in (i for i in paths if str(i)[-4:] == ".log"):
    with open(str(i), encoding='utf-8') as file:
        for line in file:
            try:
                entry = json.loads(line)
            except json.decoder.JSONDecodeError:
                entry = None

            if entry:
                try:
                    if entry["MarketID"] != 3704002816:
                        continue
                    if entry["event"] != 'MarketSell':
                        continue

                    try:
                        pods[entry["Type"]][0] += entry["Count"]
                    except KeyError:
                        continue

                except KeyError:
                    continue

        file.close()

for i in pods.values():
    print("{}: {}".format(i[1], i[0]))

input()