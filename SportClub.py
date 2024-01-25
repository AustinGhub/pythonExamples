class SportClub:
    def __init__(self):
        self.name = ""
        self.city = ""
        self.sport = ""
        self.rank = 0
        self.count = 0
    #sets stuff
    def setName(self, name):
        self.name = name

    def setCity(self, city):
        self.city = city

    def setSport(self, sport):
        self.sport = sport

    def setRank(self, rank):
        self.rank = rank
    #gets the values
    def getName(self):
        return self.name

    def getCity(self):
        return self.city

    def getSport(self):
        return self.sport

    def getRank(self):
        return self.rank

    def getCount(self):
        return self.count

    def incrementCount(self):
        self.count += 1

    def __str__(self):
        return f"Sport: {self.sport}, Name: {self.city} {self.name}, Rank: {self.rank}, Count: {self.count}"