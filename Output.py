import csv
import SportClub


#make outfile as: #outfile = open(out.txt, "w")
#writing to outfile: outfile.write("string or somethign in here")

# Function to sort a list of SportClub objects by sport. Returns 4 different lists each represents a sport (NFL, NBA, MLB, NHL)
# Takes a list of SportClub objects as an argument.
def sortBySport(sportlist):
    #arguemnt is noDupes list
    NFL = []
    NHL = []
    NBA = []
    MLB = []
    for elements in sportlist:
        if elements.getSport() == "NFL":
            NFL.append(elements)
        if elements.getSport() == "NHL":
            NHL.append(elements)
        if elements.getSport() == "NBA":
            NBA.append(elements)
        if elements.getSport() == "MLB":
            MLB.append(elements)

   
    return NFL, NHL, NBA, MLB

    

# Function to sort a list of SportClub objects by rank. Returns a list represents the sorted SportClub objects.
# Takes a list of SportClub objects of the same sport as an argument.
def sortByRank(sport):

    sport.sort(key=lambda x: (-x.count, x.city))
    sport.sort(key=lambda x: (-x.count, x.city))
    for x in range(len(sport)):
        sport[x].setRank(x+1)
        print(sport[x])
    print()
    return sport


# Function to format the output file and output the first 3 ranked teams from each sport to a .csv file named Survey Database.csv
# in the current working directory.
# Takes 4 lists of sorted SportClub objects of the same sport as an argument.
def outputSports(NFL, NBA, MLB, NHL):
    fields = ["City", "Team Name", "Sport", "Number of Times Picked"]
    with open("Survey Database.csv", "w", newline= "") as finalSports:
        sporty = csv.writer(finalSports) 
        sporty.writerow(fields)

        for stuff in NFL:
            if stuff.getRank() <= 3:
                sporty.writerow([stuff.getCity(), stuff.getName(), stuff.getSport(), stuff.getRank(), stuff.getCount()])
        for baskets in NBA:
            if baskets.getRank() <= 3:
                sporty.writerow([baskets.getCity(), baskets.getName(), baskets.getSport(), baskets.getRank(), baskets.getCount()])
        for baseball in MLB: 
            if baseball.getRank() <= 3:
                sporty.writerow([baseball.getCity(), baseball.getName(), baseball.getSport(), baseball.getRank(), baseball.getCount()])
        for hockey in NHL:
            if hockey.getRank() <= 3:
                sporty.writerow([hockey.getCity(), hockey.getName(), hockey.getSport(), hockey.getRank(), hockey.getCount()])
        
    



