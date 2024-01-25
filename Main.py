import Input
import Output
import SportClub


def main():
    #Input.readOneFile("file1.csv")
    Input.readAllFiles()
    NFL, NBA, MLB, NHL = Output.sortBySport(Input.readAllFiles())
    sortedNFL = Output.sortByRank(NFL)
    sortedNBA = Output.sortByRank(NBA)
    sortedMLB = Output.sortByRank(MLB)
    sortedNHL = Output.sortByRank(NHL)
    Output.outputSports(sortedNFL, sortedNBA, sortedMLB, sortedNHL)


if __name__ == "__main__":
    main()
