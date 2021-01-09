import os
from pathlib import Path
import json

dirpath = os.path.expanduser("~") + "/Saved Games/Frontier Developments/Elite Dangerous"




def getMinorFactions(thresh):
    paths = sorted(Path(dirpath).iterdir(), key=os.path.getmtime)
    MFs = {}
    for i in (i for i in paths if str(i)[-4:] == ".log"):
        with open(str(i), "r", encoding='utf-8')as file:
            for line in file:
                try:
                    entry = json.loads(line)
                except json.decoder.JSONDecodeError:
                    entry = None

                if entry:
                    try:
                        if entry["event"] == 'Location':
                            try:
                                fac = entry["Factions"]
                                for faction in fac:
                                    MFs[faction["Name"]] = faction["MyReputation"]

                            except KeyError:
                                fac = None
                    except KeyError:
                        continue
            file.close()

    facs = set()

    for i in MFs:
        if int(MFs[i]) >= thresh:
            facs.add(i)

    return(facs)


def getLastDock():
    paths = sorted(Path(dirpath).iterdir(), key=os.path.getmtime)
    paths.reverse()
    lastDock = [None, None, None]
    for i in paths:
        with open(str(i), "r", encoding='utf-8') as file:
            for line in file:
                try:
                    entry = json.loads(line)
                except json.decoder.JSONDecodeError:
                    entry = None

                if entry:
                    if entry["event"] == "Docked":
                        lastDock[0], lastDock[1] = entry["StarSystem"], entry["StationName"]
                        lastDock[2] = lastDock[0]

                    try:
                        lastDock[2] = entry["StarSystem"]
                    except KeyError:
                        pass
            if lastDock[0]:
                return lastDock

            file.close()


if __name__ == "__main__":
    print(getLastDock())
    facs = getMinorFactions(90)

    for i in facs:
        print(i)

input()