import requests
import datetime as date
from datetime import datetime
import tkinter as tk

econExclude = ["Extraction", "Refinery"]
typeExclude = ["Fleet Carrier", "Planetary Outpost", "Planetary Port", "Outpost"]
MFinclude = ["Pilots' Federation Local Branch", 'EG Union', 'Wolf 406 Transport & Co', 'East India Company', 'EDA Kunti League', 'Iota Hydri Empire Pact', 'Independent Deciat Green Party', 'Nationals of HIP 6108', 'HIP 11241 Patrons of Law', 'Ngalinn Jet Natural Incorporated', 'Aitvas Corp.', 'Mainani Empire Party', 'Imperial Wargrannys', 'Brothers of Mainani', 'Hajo General Solutions', 'Sirius Corporation', 'Canonn', 'Eurybia Blue Mafia', 'Federation Unite!', 'RSR', 'Exphiay for Equality', 'White Star Surveillance Division', 'Exphiay Blue Transport Corp', 'Exphiay Crimson Hand Gang', 'Gallant Investment Brokers', 'The Bliss Consortium', 'Duduseklis Empire League', 'Fionn Liberals', 'Alliance Democratic Network', 'Party of Yoru', 'HIP 14211 Blue Posse', 'Dominion of LHS 54', 'Sirius Atmospherics']
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
            if sysInfo["factionState"] in stateExclude:
                continue
        except KeyError:
            continue

        try:
            econ = sysInfo["economy"]
            try:
                econ2 = sysInfo["secondEconomy"]
            except KeyError:
                econ2 = None
        except KeyError:
            continue

        if econ in econExclude and (econ2 in econExclude or not econ2):
            continue

        # print("{} ({}): {}".format(i, k, econ) + ("/{}".format(econ2) if econ2 else ""))

        factions = requests.get("https://www.edsm.net/api-system-v1/factions", params={"systemName": i}).json()
        print(factions)
        # if not len(factions):
            # continue
        MFacs = [i["name"] for i in factions["factions"]]
        if not len([i for i in MFacs if i in MFinclude]):
            continue

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
        if not lite:
            t.insert("end", "None Found")
        else:
            print("None Found")

    num = sum([len(tracking[i]) for i in tracking])
    print("Found {} Stations to Visit :)".format(num))


if not lite:
    b = tk.Button(master=back, text="Refresh", width=25, height=1, command=update).place(x=0, y=0)
    tk.mainloop()

update()
