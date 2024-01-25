import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class BoardClass():
    #Defining Class Variables
    gameBoardData = [  ['', '', ''],
                       ['', '', ''],
                       ['', '', '']
                    ]

    buttonDataTable = [ ['', '', ''],
                        ['', '', ''],
                        ['', '', '']
                      ]

    playerOneUsername = ''
    playerTwoUsername = ''
    lastPlayerName = playerTwoUsername
    otherLastUser = ''
    clientName = ''
    victory = False
    victoryBtnList = []

    numOfGames = 0
    numOfWins = 0
    numOfTies = 0
    numOfLosses = 0

    #Define class variable to store tkinter object
    master = 0

    #Define Class Constructor
    def __init__(self):
        pass
        #self.createBoardCanvas('tester1')
        #self.createGameGrid()
        #self.playerNameLabel.pack(fill='x')
        #self.createQuitButton()
        #self.runUI()

    def recordGamePlayed(self):
        #Updates how many total games have been played
        self.numOfGames += 1


    def resetGameBoard(self):
        #Clear all the moves from game board
        for (rowIndex,row) in enumerate(self.gameBoardData):    
            for (subIndex,element) in enumerate(row):
                self.gameBoardData[rowIndex][subIndex] = ''
        for row in self.buttonDataTable:
            for btn in row:
                btn['text'] = ''
        self.lastPlayerName = self.playerTwoUsername
        self.victory = False
        #print('Board Reset')


    def isPlayerTurn(self):
        if self.clientName == self.lastPlayerName:
            return True
        else:
            return False


    def playMoveOnBoard(self, button, label):
        #Updates the game board with the player's move
        boardDataDict = {
                '1': 0, '2': 0, '3': 0,
                '4': 1, '5': 1, '6': 1,
                '7': 2, '8': 2, '9': 2,

                0: 0, 1: 1, 2: 2,
                3: 0, 4: 1, 5: 2,
                6: 0, 7: 1, 8: 2
            }
        stringButton = str(button)[-1:]
        if not stringButton.isdigit():
            stringButton = '1'
        buttonNumber = int(int(stringButton) - 1)
        self.otherLastUser = self.lastPlayerName
        if not self.isBoardFull():
            #self.clkStatus = not self.clkStatus
            if button['text'] == '' and self.lastPlayerName == self.playerTwoUsername:
                button['text'] = 'X'
                self.gameBoardData[boardDataDict[stringButton]][boardDataDict[buttonNumber]] = 'X'
                if not self.isGameFinished('X') and not self.isBoardFull():
                    if not self.isPlayerTurn():
                        label.set("Your turn")
                        for row in self.buttonDataTable:
                            for btn in row:
                                btn.config(state='normal')
                    else:
                        label.set(self.playerOneUsername + "'s turn")
                        for row in self.buttonDataTable:
                            for btn in row:
                                btn.config(state='disabled')
                    self.lastPlayerName = self.playerOneUsername
                    #print("Player 1's turn now")
                else:
                    self.outputGameEnd()
            elif button['text'] == '' and self.lastPlayerName == self.playerOneUsername:
                button['text'] = 'O'
                self.gameBoardData[boardDataDict[stringButton]][boardDataDict[buttonNumber]] = 'O'
                if not self.isGameFinished('O') and not self.isBoardFull():
                    if not self.isPlayerTurn():
                        label.set("Your turn")
                        for row in self.buttonDataTable:
                            for btn in row:
                                btn.config(state='normal')
                    else:
                        label.set(self.playerTwoUsername + "'s turn")
                        for row in self.buttonDataTable:
                            for btn in row:
                                btn.config(state='disabled')
                    self.lastPlayerName = self.playerTwoUsername
                    #print("Player 2's Turn Now")
                else:
                    self.outputGameEnd()


    def isBoardFull(self):
        #Checks if the board is full (I.e. no more moves to make)
        isFull = True
        for row in self.gameBoardData:
            for element in row:
                if element == '':
                    isFull = False
                    break
        return isFull


    def isGameFinished(self,player):
        self.victoryBtnList.clear()
        #Checks if the latest move resulted in a win, loss or tie
        #Updates the wins, losses and ties count if the game is over
        for (index,row) in enumerate(self.gameBoardData):
            #Checks if a player has a complete row victory condition
            if row == [player, player, player]:
                self.victoryBtnList.append(self.buttonDataTable[index][0])
                self.victoryBtnList.append(self.buttonDataTable[index][1])
                self.victoryBtnList.append(self.buttonDataTable[index][2])
                self.victory = True
                break
            #Checks if a player has a complete column victory condition
            tempCount = 0
            for colCount in range(0,3):
                if player == self.gameBoardData[colCount][index]:
                    tempCount += 1
            if tempCount == 3:
                self.victoryBtnList.append(self.buttonDataTable[0][index])
                self.victoryBtnList.append(self.buttonDataTable[1][index])
                self.victoryBtnList.append(self.buttonDataTable[2][index])
                self.victory = True
                break
            #Checks if a player has a complete diagonal victory condition
            if [player, player, player] == [self.gameBoardData[0][2], self.gameBoardData[1][1], self.gameBoardData[2][0]]:
                self.victoryBtnList.append(self.buttonDataTable[0][2])
                self.victoryBtnList.append(self.buttonDataTable[1][1])
                self.victoryBtnList.append(self.buttonDataTable[2][0])
                self.victory = True
                break
            elif [player, player, player] == [self.gameBoardData[0][0], self.gameBoardData[1][1], self.gameBoardData[2][2]]:
                self.victoryBtnList.append(self.buttonDataTable[0][0])
                self.victoryBtnList.append(self.buttonDataTable[1][1])
                self.victoryBtnList.append(self.buttonDataTable[2][2])
                self.victory = True
                break
        return self.victory

    def outputGameEnd(self):
        if self.victory or self.isBoardFull():
            if self.isBoardFull() and not self.victory:
                tk.messagebox.showinfo("Tic Tac Toe", "TIED GAME!")
                for row in self.buttonDataTable:
                        for btn in row:
                            btn.config(state='disabled')
                self.lastPlayerName = self.playerTwoUsername
                self.numOfTies += 1
                self.victory = False
                #print('Tie')
            elif self.victory:
                if self.isPlayerTurn():
                    tk.messagebox.showinfo("Tic Tac Toe", "You Win!")
                    for row in self.buttonDataTable:
                        for btn in row:
                            btn.config(state='disabled')
                    self.lastPlayerName = self.playerTwoUsername
                    self.numOfWins += 1
                    #print('Win')
                else:
                    tk.messagebox.showinfo("Tic Tac Toe", "{playerChar} Wins".format(playerChar=self.lastPlayerName))
                    for row in self.buttonDataTable:
                        for btn in row:
                            btn.config(state='disabled')
                    self.lastPlayerName = self.playerTwoUsername
                    self.victory = False
                    self.numOfLosses += 1
                    #print('Lost')

            self.recordGamePlayed()
            #self.computeStats()
            for tile in self.victoryBtnList:
                tile.config(bg='light green')
        else:
            for row in self.buttonDataTable:
                for btn in row:
                    btn.config(state='disabled')
        return self.victory      


    def computeStats(self):
        returnList = []
        #Usernames of both players
        returnList.append(self.playerOneUsername)
        returnList.append(self.playerTwoUsername)

        #The username of the last person to make a move
        returnList.append(self.otherLastUser)

        #The total number of games
        returnList.append(self.numOfGames)

        #The total number of wins
        returnList.append(self.numOfWins)
        #The total number of losses
        returnList.append(self.numOfTies)
        #The total number of ties
        returnList.append(self.numOfLosses)

        print('\n-------- Shell Display STATS --------')
        print('Player 1:', self.playerOneUsername)
        print('Player 2;', self.playerTwoUsername)
        print('Last Player to make a move:', self.otherLastUser)
        print('        #-------------------#        ')
        print('Total Number of Games Played:', self.numOfGames)
        print('Number of wins for {player}: {wins}'.format(player=self.clientName, wins=self.numOfWins))
        print('Number of Ties:', self.numOfTies)
        print('Number of losses for {player}: {losses}'.format(player=self.clientName, losses=self.numOfLosses))
        print('-------------------------------------\n')

        return returnList

    def runUI(self):
      self.master.mainloop()

