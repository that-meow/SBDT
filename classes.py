class Cargo:

    def __init__(self):
        self.commodityObjects = []
        self.commodityNames = []

    def updateCargo(self, cargo, system, station): # general update, works with current and past inventory
        # cargo is a dict with multiple entries, name: count
        unsentDeliveries = []
        checkNames = self.commodityNames.copy() # copies names to check against later
        for x in cargo: # x is the name of a commodity
            if x in self.commodityNames:  # checks if the name is already saved
                for y in range(len(self.commodityNames)):  # finds the entry with the given name
                    if x == self.commodityNames[y]:
                        print(x, cargo[x], "aaaa")
                        unsentDeliveries.extend(self.commodityObjects[y].updateCommodity(cargo[x], system, station))
                        checkNames.remove(x)
                        # updates the object with new cargo
            else: # if the name isn't saved:
                # creates new object and appends the name to commodityNames
                print(x, cargo[x], "bbbb")
                self.commodityObjects.append(Commodity(x, cargo[x], system, station))
                self.commodityNames.append(x)
        for z in checkNames:
            # these entries only appear in old cargo, meaning they're gone now, so we'll make a delivery
            toPop = 0
            for y in range(len(self.commodityNames)):
                if z == self.commodityNames[y]:
                    unsentDeliveries.extend(self.commodityObjects[y].sellAll(system, station))
                    toPop = y
                    break
            self.commodityNames.pop(toPop)
            self.commodityObjects.pop(toPop)
            # and we'll also clean them up
        return unsentDeliveries


    def buyCargo(self, cargo, system, station): # MarketBuy update, works with amount bought and past inventory
        # cargo is a dict of one, but just to be sure:
        for x in cargo: # x is the name of a commodity
            if x in self.commodityNames: # checks if the name is already saved
                for y in range(len(self.commodityNames)): # finds the entry with the given name
                    if x == self.commodityNames[y]:
                        self.commodityObjects[y].buyCommodity(cargo[x], system, station)
                        # updates the object with new cargo
            else: # if the name isn't saved:
                # creates new object and appends the name to commodityNames
                self.commodityObjects.append(Commodity(x, cargo[x], system, station))
                self.commodityNames.append(x)


class Commodity:
    def __init__(self, name, count, system, station):
        self.name = name
        self.count = 0
        self.origins = []
        self.buyCommodity(count, system, station)

    def updateCommodity(self, count, system, station): # general update, works with current and past inventory
        unsentDeliveries = []
        print(count, self.count)
        if count == self.count:
            return []
        elif count > self.count:
            self.buyCommodity(count - self.count, system, station)
        else:
            unsentDeliveries.extend(self.sellCommodity(self.count - count, system, station))
        return unsentDeliveries

    def buyCommodity(self, count, system, station): # buy update, works with amount bought and past inventory
        self.count += count
        stationFound = False
        for x in self.origins:
            if x["OriginSystem"] == system and x["OriginStation"] == station:
                stationFound = True
                x["Count"] += count
                break
        if not stationFound:
            self.origins.append({"OriginSystem":system, "OriginStation":station, "Count":count})

    def sellCommodity(self, count, system, station): # sell update, works with amount sold and past inventory
        self.count -= count
        unsentDeliveries = []
        lastOriginToRemove = -1
        for x in range(len(self.origins)):
            if count >= self.origins[x]["Count"]:
                lastOriginToRemove = x  # keeps the index of the last origin entry to remove, keep x+1
                count -= self.origins[x]["Count"]
                self.origins[x]["DestinationSystem"] = system
                self.origins[x]["DestinationStation"] = station
                self.origins[x]["Name"] = self.name
                unsentDeliveries.append(self.origins[x])
            else:
                self.origins[x]["Count"] -= count
                unsentDeliveries.append({"OriginSystem": self.origins[x]["OriginSystem"],
                                         "OriginStation": self.origins[x]["OriginStation"],
                                         "Name": self.name, "Count": count,
                                         "DestinationSystem": system,
                                         "DestinationStation": station})
                break
        self.origins = self.origins[lastOriginToRemove+1:]
        return unsentDeliveries

    def sellAll(self, system, station):
        return self.sellCommodity(self.count, system, station)