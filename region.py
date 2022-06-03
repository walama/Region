import pandas as pd
from geopy import distance
import yaml
import os

def main():
    newCities = []
    global cities
    cities = []
    df = pd.read_excel(r'citydata.xlsx')
    data = df.to_dict()
    for i in data['city'].keys():
        name = data['city'][i]
        population = data['population'][i]
        longitude = data['lng'][i]
        lattitude = data['lat'][i]
        city = {'id': i, 'name': name, 'population': population, 'boss': None, 'distance': 500, 'longitude': longitude, 'lattitude': lattitude}
        newCities.append(city)
    
    # a hub is a city of significant size and isolation that the reisdents would be unlikely to travel elsewhere for significant services
    hubs = []
    for raw in newCities:
        city = findBoss(raw)
        if city['boss'] == None:
            hubs.append(city['id'])
        cities.append(city)
    for hub in hubs:
        tree = getTree(hub)
        fileName = "regions/" + cities[hub]['name'] + ".yaml"
        writeFile(fileName, tree)
    
def findIndex(name):
    for city in cities:
        if city['name'] == name:
            return city['id']
    return(-1)

# find the city one step up the ladder
def findBoss(city):
    for big in cities:
        # the coefficient here is relatively arbitrary but the idea is that the city should have to be signifficantly bigger enough to provide services that would motivate one to travel
        if big['population'] > (city['population'] * 1.25):
            between = findDistance(big, city)
            if between < city['distance']:
                city['distance'] = between
                city['boss'] = big['id']
        else:
            return city
    return city

def findDistance(a, b):
    aPosition = (a['lattitude'], a['longitude'])
    bPosition = (b['lattitude'], b['longitude'])
    between = distance.distance(aPosition, bPosition).miles
    return between


def getTree(base):
    tree = {}
    name = cities[base]['name']
    children = getChildren(base)
    if len(children) == 0:
        tree = "leaf"
    else:
        for child in children:
            subTree = getTree(child)
            childName = cities[child]['name']
            tree[childName] = subTree
    return tree
        

def getChildren(base):
    i = base
    children = []
    while i < len(cities):
        if cities[i]['boss'] == base:
            children.append(cities[i]['id'])
        i = i+1
    return children

def getLineage(i, lineage):
    if cities[i]['boss'] != None:
        lineage.append(cities[i]['boss'])
        return getLineage(cities[i]['boss'], lineage)
    else:
     return lineage

def writeFile(fileName, tree):
    if not os.path.exists("regions"):
        os.makedirs("regions")
    f = open(fileName, "a")
    f.write(yaml.dump(tree))
    f.close()

if __name__ == "__main__":
    main()