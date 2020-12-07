import os
from pathlib import Path
import json

with open("logpath.txt", "r") as file:
    dirpath = file.read().strip("\n")
    file.close()
paths = sorted(Path(dirpath).iterdir(), key=os.path.getmtime)
for i in paths:
    if str(i)[-4:] != ".log":
        paths.remove(i)


def getMinorFactions(thresh):
    MFs = {}
    for i in paths:
        with open(str(i), "r", encoding='utf-8')as file:
            for line in file:
                try:
                    entry = json.loads(file.readline())
                except json.decoder.JSONDecodeError:
                    entry = None

                if entry:
                    if entry["event"] == 'Location':
                        try:
                            fac = entry["Factions"]
                            for faction in fac:
                                MFs[faction["Name"]] = faction["MyReputation"]

                        except KeyError:
                            fac = None
            file.close()

    for i in MFs:
        if int(MFs[i]) > 5:
            l = MFs[i]
            rep = "Allied" if l > 90 else "Friendly" if l > 35 else "Cordial"
            # print("{}: {}".format(i, rep))

    facs = set()

    for i in MFs:
        if int(MFs[i]) > thresh:
            facs.add(i)

    return(facs)


def getLastDock():
    paths.reverse()
    lastDock = None
    for i in paths:
        with open(str(i), "r", encoding='utf-8') as file:
            for line in file:
                try:
                    entry = json.loads(file.readline())
                except json.decoder.JSONDecodeError:
                    entry = None

                if entry:
                    if entry["event"] == "Docked":
                        lastDock = entry["StarSystem"]
            if lastDock:
                return lastDock


if __name__ == "__main__":
    print(getLastDock())

    facs = getMinorFactions(35)
    for i in facs:
        print(i)