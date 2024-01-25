from pathlib import Path
import csv
import SportClub


# Function to read one .csv file in the current working directory. Returns a list of tuples of three fields (City, Name and Sport).
# Takes file name as an argument (with .csv). For example, name could be test.csv
def readOneFile(name):
  current_directory = Path(".").glob("*.csv")
  fields = []

  for files in current_directory:
    if name == files.name:
      with open(name, "r", newline = "") as csvFile:
        csv_data = csv.reader(csvFile)
        for line in csv_data:
          if line != ["City", "Team Name", "Sport"]:
            fields.append(tuple(line))

  return fields
        

# Function to read all .csv files in the current working directory. Returns a list of SportClub objects.
# This function should create a SportClub object if the tuples fields are new or just increment if an object already made.
# This function will produce a file called Report.txt which has information about the files you read.
# This function will produce a file called Error log.txt which has information about the error files you read.
def readAllFiles():
  csv_only = Path(".").glob("*.csv")

  fileCount = 0
  numberLines = 0
  corrupted_files = []
  sportsDict = dict()
  #reads all csv files and adds to text file
  for files in csv_only:
    corrupt = False
    sportGuys = readOneFile(str(files))
    for lines in sportGuys:
      numberLines += 1 
      for elements in lines:
        if elements == "":
          corrupt = True  
    if corrupt == True:
      corrupted_files.append(files)
    else: 
      fileCount += 1 
      with open('Report.txt', 'w', newline='') as poo:
        poo.write('Number of files read: %d\n' %(fileCount))
        poo.write('Number of items read: %d' %(numberLines))
      for city, name, sport in sportGuys: 
        if (city, name, sport) in sportsDict:
          sportsDict[city, name, sport].incrementCount()
        else:
          manager = SportClub.SportClub()
          manager.setName(name)
          manager.setCity(city)
          manager.setSport(sport)
          manager.setRank(0)
          manager.incrementCount()
          sportsDict[city, name, sport] = manager

  
    with open("Error log.txt", "w", newline = '') as errors:
      if len(corrupted_files) > 0:
        errors.write(",".join(str(i) for i in corrupted_files))
      else:
        errors.write("None")

  return list(sportsDict.values())

      

  