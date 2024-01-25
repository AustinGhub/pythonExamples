#This will be ran, like an actual program with the whole "if __name__ == '__main__':"
import gameboard
import tkinter as tk
from tkinter import messagebox
import socket
import threading

class invalidNameError(Exception):
    pass
   
def serverConnect(ipAddress, ipPort, event=None):
    addressString = ipAddress.get()
    portValue = ipPort.get()

    try:
        connectionSocket.connect((addressString, portValue))

        serverData = connectionSocket.recv(1024)
        print(serverData.decode('ascii'))

        for x in clientMaster.grid_slaves():
            if str(x) == '.!button':
                x.config(state="disabled")

        statusLabel.configure(text='Connection Successful', fg='green')
        statusLabel.grid(row=2,column=1)
        #Clears the tkinter window
        #for x in clientMaster.grid_slaves():
            #   x.grid_forget()
        nameEntry()

    except Exception:
        global connectionFail
        connectionFail = True
        statusLabel.configure(text='Connection Failed, Try Again', fg='red')
        statusLabel.grid(row=2,column=1)
        userChoice = tk.messagebox.askyesno(title="Tic-Tac-Toe - Client", message = "Connection Failed, try again?")
        if not userChoice:
            clientMaster.destroy()

def nameEntry():
    nameLabel = tk.Label(clientMaster, text = "Name:").grid(row=6,column=0)
    playerName = tk.Entry(clientMaster, textvariable=nameHold).grid(row=6,column=1)
    submitButton = tk.Button(clientMaster, text="Submit", command=lambda : submitName()).grid(row=8,column=1)

def submitName(event=None):
    clientPlayerTwo.playerTwoUsername = nameHold.get()
    try:
        if clientPlayerTwo.playerTwoUsername.isalnum():
            for x in clientMaster.grid_slaves():
                if '.!button' in str(x):
                    x.config(state="disabled")
            nameValidLabel.configure(text='Waiting for Host', fg='blue')
            nameValidLabel.grid(row=7,column=1)

            connectionSocket.send(clientPlayerTwo.playerTwoUsername.encode())

            receivedData = connectionSocket.recv(1024)
            receivedData = receivedData.decode()
            if receivedData:
                print("Host's name is:", receivedData)
                clientPlayerTwo.playerOneUsername = receivedData

                #clientMaster.destroy()
                for x in clientMaster.grid_slaves():
                    x.destroy()
                
                #threading._start_new_thread(runGame, tuple(''))
                setUpGame(clientPlayerTwo.playerTwoUsername)
        else:
            raise invalidNameError
    except invalidNameError:
        nameValidLabel.configure(text='Invalid name, only use alphanumeric characters', fg='red')
        nameValidLabel.grid(row=7,column=1)

def promptUserBox():
    response = tk.messagebox.askyesno(title='Tic Tac Toe', message='Would you like to play again?')
    if response:
        endChoice('Play Again')
    else:
        endChoice('Fun Times')

def buttonClk(button):
    if button['text'] == '':
        if not clientPlayerTwo.isGameFinished('X'):
            clientPlayerTwo.playMoveOnBoard(button, labelLastPlayer)
        threading._start_new_thread(playerMoveTransmission, (button, ''))
    else:
        tk.messagebox.showerror(title="Tic Tac Toe", message="This box has already been used!")

def btnToNum(button):
    strButton = str(button)[-1:]
    if not strButton.isdigit():
        strButton = '1'
    return strButton

def playerMoveTransmission(button, trash):
    buttonNumber = btnToNum(button)
    playerMoveSend = buttonNumber
    try:
        connectionSocket.send(playerMoveSend.encode())
        #Will reset the board if the user decides to
        if clientPlayerTwo.isGameFinished('X'):
            promptUserBox()
    except Exception:
        connectionLost()
    if clientPlayerTwo.isBoardFull():
        promptUserBox()
    receiveData()

def receiveData():
    """ Works well, but has issue with transmitting
    while True:
        playerMove = (connectionSocket.recv(1024)).decode()
        print("P1:", playerMove)
        if playerMove != None: break
    """
    while True:
        try:
            buttonIndex = (connectionSocket.recv(1024)).decode()
            for (index,row) in enumerate(clientPlayerTwo.buttonDataTable):
                for (subindex,element) in enumerate(row):
                    stripped = btnToNum(element)
                    if not stripped.isdigit():
                        stripped = '1'
                    if buttonIndex == stripped:
                        storedButton = clientPlayerTwo.buttonDataTable[index][subindex]
            clientPlayerTwo.playMoveOnBoard(storedButton, labelLastPlayer)
            if str(storedButton) != '':
                if clientPlayerTwo.isGameFinished('O'):
                    promptUserBox()
                break
        except Exception:
            connectionLost()

def connectionLost():
    userChoice = tk.messagebox.showinfo(title="Tic-Tac-Toe - Host", message = "Connection Lost")
    if userChoice:
        clientMaster.destroy()

    #while True:
    #    playerMove = connectionSocket.recv(1024)
    #    playerMove = playerMove.decode()
    #    if playerMove == None: break
    #    print('P1:', playerMove)
    #serverSocket.close()

    #if contToRun:
    #        playerMove = 'Me : '
    #        connectionSocket.send(playerMove.encode())
    #        playerMove = connectionSocket.recv(1024)
    #        playerMove = playerMove.decode()
    #        print('P1:', playerMove)

def endChoice(message):
    #print('Resetting Game . . ')
    connectionSocket.send(message.encode())
    clientPlayerTwo.resetGameBoard()
    if message == 'Play Again':
        for x in clientMaster.winfo_children():
            x.destroy()
        setUpGame(clientPlayerTwo.playerTwoUsername)
    else:
        for x in clientMaster.winfo_children():
            x.destroy()
        statsPage()

def statsPage():
    statData = clientPlayerTwo.computeStats()

    clientMaster.title("{user}'s Statistics".format(user=clientPlayerTwo.playerTwoUsername))
    clientMaster.geometry('280x200')
    header = tk.Label(clientMaster, text="Player Statistics", font="Futura, 12", bg='grey', fg='white').grid(row=1,column=2)

    hostNameLabel = tk.Label(clientMaster, text="Player 1's Name", bg='grey', fg='white').grid(row=2,column=1)
    hostNameText = tk.Label(clientMaster, text=statData[0], bg='grey', fg='white').grid(row=2,column=3)

    clientNameLabel = tk.Label(clientMaster, text="Player 2's Name", bg='grey', fg='white').grid(row=3,column=1)
    clientNameText = tk.Label(clientMaster, text=statData[1], bg='grey', fg='white').grid(row=3,column=3)

    lastUserLabel = tk.Label(clientMaster, text="Last Move User", bg='grey', fg='white').grid(row=4,column=1)
    lastUserText = tk.Label(clientMaster, text=statData[2], bg='grey', fg='white').grid(row=4,column=3)

    numGamesLabel = tk.Label(clientMaster, text="Games Played", bg='grey', fg='white').grid(row=5,column=1)
    numGamesText = tk.Label(clientMaster, text=statData[3], bg='grey', fg='white').grid(row=5,column=3)

    numWinsLabel = tk.Label(clientMaster, text="Wins", bg='grey', fg='white').grid(row=6,column=1)
    numGamesText = tk.Label(clientMaster, text=statData[4], bg='grey', fg='white').grid(row=6,column=3)

    numTiesLabel = tk.Label(clientMaster, text="Ties", bg='grey', fg='white').grid(row=7,column=1)
    numGamesText = tk.Label(clientMaster, text=statData[5], bg='grey', fg='white').grid(row=7,column=3)

    numLostLabel = tk.Label(clientMaster, text="Losses", bg='grey', fg='white').grid(row=8,column=1)
    numGamesText = tk.Label(clientMaster, text=statData[6], bg='grey', fg='white').grid(row=8,column=3)

    exitButton = tk.Button(clientMaster, text="Quit", command=lambda: clientMaster.destroy()).grid(row=9, column=2)

    clientMaster.grid_rowconfigure((0, 10), weight=1)
    clientMaster.grid_columnconfigure((0, 4), weight=1)


def setUpGame(titleName):
    clientMaster.geometry('280x332')
    clientMaster.title("Tic Tac Toe - {name}".format(name=titleName))
    clientMaster.configure(background='grey')

    clientPlayerTwo.lastPlayerName = clientPlayerTwo.playerTwoUsername
    clientPlayerTwo.clientName = clientPlayerTwo.playerTwoUsername

    #Formats and creates the new tkinter parent, from which the the window can be used in two halves
    mainFrame = tk.Frame(clientMaster)
    mainFrame.pack(fill='both', expand=True)

    #Top half, contains "Current Player" and the player's name
    topHalfFrame = tk.Frame(clientMaster)
    topicLabel = tk.Label(topHalfFrame, text="Player Status:", font="Futura, 12", bg='grey').pack(fill='x')
    playerNameLabel = tk.Label(topHalfFrame, textvariable=labelLastPlayer, font="Futura, 11", bg='grey')
    topHalfFrame.pack(fill='x')

    #Bottom half, contains the actual Tic Tac Toe game grid
    #1st Row
    bottomHalfFrame = tk.Frame(clientMaster, bg='grey')
    buttonOne = tk.Button(bottomHalfFrame, text='', font="Futura", height=3, width=6, command=lambda: buttonClk(buttonOne))
    buttonOne.grid(row=1, column=1)
    buttonTwo = tk.Button(bottomHalfFrame, text='', font="Futura", height=3, width=6, command=lambda: buttonClk(buttonTwo))
    buttonTwo.grid(row=1, column=2)
    buttonThree = tk.Button(bottomHalfFrame, text='', font="Futura", height=3, width=6, command=lambda: buttonClk(buttonThree))
    buttonThree.grid(row=1, column=3)
        
    #2nd Row
    buttonFour = tk.Button(bottomHalfFrame, text='', font="Futura", height=3, width=6, command=lambda: buttonClk(buttonFour))
    buttonFour.grid(row=2, column=1)
    buttonFive = tk.Button(bottomHalfFrame, text='', font="Futura", height=3, width=6, command=lambda: buttonClk(buttonFive))
    buttonFive.grid(row=2, column=2)
    buttonSix = tk.Button(bottomHalfFrame, text='', font="Futura", height=3, width=6, command=lambda: buttonClk(buttonSix))
    buttonSix.grid(row=2, column=3)
        
    #3rd Row
    buttonSeven = tk.Button(bottomHalfFrame, text='', font="Futura", height=3, width=6, command=lambda: buttonClk(buttonSeven))
    buttonSeven.grid(row=3, column=1)
    buttonEight = tk.Button(bottomHalfFrame, text='', font="Futura", height=3, width=6, command=lambda: buttonClk(buttonEight))
    buttonEight.grid(row=3, column=2)
    buttonNine = tk.Button(bottomHalfFrame, text='', font="Futura", height=3, width=6, command=lambda: buttonClk(buttonNine))
    buttonNine.grid(row=3, column=3)

    quitButton = tk.Button(bottomHalfFrame, text="Quit", command=lambda: clientMaster.destroy()).grid(row=9, column=2)
        
    clientPlayerTwo.buttonDataTable[0][0] = buttonOne
    clientPlayerTwo.buttonDataTable[0][1] = buttonTwo
    clientPlayerTwo.buttonDataTable[0][2] = buttonThree
    clientPlayerTwo.buttonDataTable[1][0] = buttonFour
    clientPlayerTwo.buttonDataTable[1][1] = buttonFive
    clientPlayerTwo.buttonDataTable[1][2] = buttonSix
    clientPlayerTwo.buttonDataTable[2][0] = buttonSeven
    clientPlayerTwo.buttonDataTable[2][1] = buttonEight
    clientPlayerTwo.buttonDataTable[2][2] = buttonNine

    #Centre aligns the Tic Tac Toe Grid
    bottomHalfFrame.grid_rowconfigure((0, 4), weight=1)
    bottomHalfFrame.grid_columnconfigure((0, 4), weight=1)
    bottomHalfFrame.pack(fill='x')
    
    if titleName == clientPlayerTwo.lastPlayerName:
        labelLastPlayer.set("Your turn")
        #setButtonStatus('normal')
    else:
        labelLastPlayer.set(clientPlayerTwo.playerOneUsername + "'s turn")
        #setButtonStatus('disabled')
    playerNameLabel.pack(fill='x')
    #threading._start_new_thread(receiveData, tuple(''))


if __name__ == '__main__':
    clientPlayerTwo = gameboard.BoardClass()
    clientMaster = tk.Tk()
    clientMaster.geometry('350x190')
    clientMaster.title("Tic-Tac-Toe - Client")
    clientMaster.resizable(0,0)
    labelLastPlayer = tk.StringVar()
    nameHold = tk.StringVar()
    ipAddress = tk.StringVar()
    ipPort = tk.IntVar()
    connectionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connectionFail = False


    nameValidLabel = tk.Label(clientMaster, text='', font='Futura, 8', fg='red')
    statusLabel = tk.Label(clientMaster, text='', font='Futura, 8')
    addressLabel = tk.Label(clientMaster, text = "Enter IP Address:").grid(row=0,column=0)
    addressEntry = tk.Entry(clientMaster, textvariable=ipAddress).grid(row=0,column=1)

    #Gets the Port Value
    portLabel = tk.Label(clientMaster, text = "Enter Port Value:").grid(row=1,column=0)
    portEntry = tk.Entry(clientMaster, textvariable=ipPort).grid(row=1,column=1)

    #Submit IP Address and Port Value
    connectButton = tk.Button(clientMaster, text="Connect", command=lambda : serverConnect(ipAddress, ipPort)).grid(row=4,column=1)


    clientMaster.mainloop()

