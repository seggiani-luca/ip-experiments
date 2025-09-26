import subprocess
import sys
import requests
import folium


# queries ip-api for ip location
def getLocation(ip):
    r = requests.get(f"http://ip-api.com/json/{ip}"
                     f"?fields=status,country,regionName,city,org,lat,lon")
    data = r.json()
    if data.get("status") != "success":
        return None
    else:
        return {
            "country": data.get("country"),
            "regionName": data.get("regionName"),
            "city": data.get("city"),
            "org": data.get("org"),
            "lat": data.get("lat"),
            "lon": data.get("lon")
        }


# prints node array
def printNodes(nodes):
    for node in nodes:
        if node["location"]:
            print(f"{node["idx"]}\t{node["ip"]}\t{node["country"]} "
                  f"{node["regionName"]} {node["city"]} {node["org"]}")
        else:
            if node["ip"] != "*":
                print(f"{node["idx"]}\t{node["ip"]}\tNo API response")
            else:
                print(f"{node["idx"]}\t{node["ip"]}\t\tNo traceroute response")


# draw node map
def showMap(nodes):
    m = folium.Map()

    poly_coords = []

    for node in nodes:
        if node["location"]:
            lat = node["lat"]
            lon = node["lon"]

            poly_coords.append((lat, lon))

            folium.Marker(
                location=[lat, lon],
                popup=f"{node["idx"]}\t{node["ip"]}\t{node["country"]} "
                      f"{node["regionName"]} {node["city"]} {node["org"]}"
            ).add_to(m)

    folium.PolyLine(poly_coords).add_to(m)
    m.fit_bounds(poly_coords)

    m.save("map.html")
    print("\nGenerated interactive map at map.html")


# get domain name as first argument
domain = sys.argv[1]

# traceroute to domain
troute = subprocess.Popen(
    ["traceroute", "-n", "-q 1", "-w 3", domain],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# init node array
nodes = []

# step through traceroute and query location
with troute.stdout:
    tokens1 = next(troute.stdout).strip().split()

    # last ip is given first, store it
    ip1 = tokens1[3][1:-2]

    for line in troute.stdout:
        tokens = line.strip().split()

        idx = tokens[0]
        ip = tokens[1]

        node = {
            "idx": idx,
            "ip": ip
        }

        if ip != "*":
            location = getLocation(ip)
            if location:
                node = node | location
                node["location"] = True
            else:
                node["location"] = False
        else:
            node["location"] = False

        nodes.append(node)

    node = {
        "idx": int(idx) + 1,
        "ip": ip1
    }

    # now get last ip
    location = getLocation(ip1)
    if location:
        node = node | location
        node["location"] = True
    else:
        node["location"] = False

    nodes.append(node)

# view data
printNodes(nodes)
showMap(nodes)
