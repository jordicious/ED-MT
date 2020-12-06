import os
from pathlib import Path
import json

with open("logpath.txt", "r") as file:
    dirpath = file.read().strip("\n")
    file.close()

paths = sorted(Path(dirpath).iterdir(), key=os.path.getmtime)
MFs = {}

for i in paths:
    if str(i)[-4:] != ".log":
        continue

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
    if int(MFs[i]) > 10:
        l = MFs[i]
        rep = "Allied" if l > 90 else "Friendly" if l > 30 else "Cordial"
        print("{}: {}".format(i, rep))
