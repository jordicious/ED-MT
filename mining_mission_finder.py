import requests
import datetime as date
from datetime import datetime
import tkinter as tk

econExclude = ["Extraction", "Refinery"]
typeExclude = ["Fleet Carrier", "Planetary Outpost", "Planetary Port", "Outpost"]
stateExclude = []

with open("config.txt", "r") as Keys:
    cmdr, api, lite = (i.strip("\n") for i in Keys.readlines())
    lite = int(lite)
    Keys.close()
radius = input("Radius >")

if radius == "OVERRIDE":
    sysOverride = input("Override System >")
    radius = input("Radius >")
else:
    sysOverride = None


def timeSinceRefresh():
    time = datetime.utcnow().replace(microsecond=0)
    delta = date.timedelta(minutes=(time.minute - 1) % 10, seconds=time.second)
    return time, delta, time-delta


if not lite:
    master = tk.Tk()
    master.geometry("250x500")
    master.resizable(0, 1)
    master.title("Mining Missions")
    back = tk.Frame(master, bg='black')
    back.propagate(0)
    back.pack(fill=tk.BOTH, expand=1)
    t = tk.Text(master=back, height=100, width=500, back="black", fg='white')
    t.configure(font=("Arial", 12, "bold"))
    t.place(x=0, y=25)


def update():
    if not lite:
        t.delete("1.0", "end")

    lastRefresh = timeSinceRefresh()
    print("Last Refresh: {} ({} ago)".format(lastRefresh[2], lastRefresh[1]))

    tracking = {}

    if sysOverride:
        lastSys = sysOverride
    else:
        lastSys = requests.get("https://www.edsm.net/api-logs-v1/get-position", params={"commanderName": cmdr, "apiKey": api}).json()["system"]

    print("Last System is: {}".format(lastSys))

    request = {i["name"]: i for i in requests.get("https://www.edsm.net/api-v1/sphere-systems", params={"systemName": lastSys, "radius": radius, "showInformation": 1}).json()}
    systems = {i: request[i]["distance"] for i in request}
    systems = {u: v for u, v in sorted(systems.items(), key=lambda item: item[1])}

    print("{} Systems in Range".format(len(systems)))
    for i in systems:
        k = systems[i]

        sysInfo = request[i]["information"]

        try:
            econ = sysInfo["economy"]
        except KeyError:
            continue

        try:
            econ2 = sysInfo["secondEconomy"]
        except KeyError:
            econ2 = None

        if not len(sysInfo):
            continue
        if econ in econExclude and (econ2 in econExclude or not econ2):
            continue
        if sysInfo["factionState"] in stateExclude:
            continue

        # print("{} ({}): {}".format(i, k, econ) + ("/{}".format(econ2) if econ2 else ""))

        stations = requests.get("https://www.edsm.net/api-system-v1/stations", params={"systemName": i}).json()["stations"]

        for j in stations:
            if j["economy"] in econExclude or j["secondEconomy"] in econExclude:
                continue
            if j["type"] in typeExclude:
                continue
            if "Missions" not in j["otherServices"]:
                continue
            if int(j["distanceToArrival"]) > 10000:
                continue

            # print("    {} ({}".format(j["name"], j["economy"]) + (", {})".format(j["secondEconomy"]) if j["secondEconomy"] else ")"))

            if not lite:
                try:
                    tracking[i].append(j["name"])
                    t.insert("end", "    {}\n".format(j["name"]))
                    print("    {}".format(j["name"]))
                except KeyError:
                    tracking[i] = [j["name"]]
                    t.insert("end", "{} ({}ly)\n".format(i, k))
                    t.insert("end", "    {}\n".format(j["name"]))
                    print("{} ({}ly)\n    {}".format(i, k, j["name"]))
                master.update()

            else:
                try:
                    tracking[i].append(j["name"])
                    print("    {}".format(j["name"]))
                except KeyError:
                    tracking[i] = [j["name"]]
                    print("{} ({}ly)\n    {}".format(i, k, j["name"]))

    if not len(tracking):
        t.insert("end", "None Found")


if not lite:
    b = tk.Button(master=back, text="Refresh", width=25, height=1, command=update).place(x=0, y=0)
    tk.mainloop()

update()
