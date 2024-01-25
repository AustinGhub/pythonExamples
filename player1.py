#This will be ran, like an actual program with the whole "if __name__ == '__main__':"
#This will be the "server host", from which player2.py will connect and interat with
import gameboard
import socket
import tkinter as tk
import threading

class invalidNameError(Exception):
    pass


def serverCreate(event=None):
    for x in clientMaster.grid_slaves():
            if str(x) == '.!button':
                x.config(state="disabled")
    statusLabel.configure(text='Waiting for other player to connect', fg='blue')
    statusLabel.grid(row=2,column=1)
    clientData = ''
    #Sets up and creates server
    print(socket.gethostname() + "'s Server is Now Active")
    serverAddress = str(ipAddress.get())
    port = int(ipPort.get())
        
    serverSocket.bind((serverAddress, port))

    #Checks for and waits for the appropriate number of players to connect
    serverSocket.listen(1)
    threading._start_new_thread(serverManage, tuple(''))


def serverManage():
    connectionCounter = 0
    
    #Establishes connnection with other player and stores any sent data from the other player
    global clientSocket
    clientSocket,clientAddress = serverSocket.accept()
    print("Client connected from:", clientAddress)
    connectionCounter += 1
        
    #Clears the tkinter window
        #for x in clientMaster.grid_slaves():
            #   x.grid_forget()
        
    statusLabel.configure(text='Other Player Connected', fg='green')
    statusLabel.grid(row=2,column=1)
    #Sends data from server to the connected user
    clientSocket.send(b'Can now interact with Host/Player 1')

    #Begin interating with connected user?
    clientData = clientSocket.recv(1024).decode('ascii')
    if clientData != '':
        print("Connect Player's name:", clientData)
        clientPlayerOne.playerTwoUsername = clientData
        nameEntry(clientSocket)           


def nameEntry(clientConnection):
    nameLabel = tk.Label(clientMaster, text = "Name:").grid(row=6,column=0)
    playerName = tk.Entry(clientMaster, textvariable=nameHold).grid(row=6,column=1)
    submitButton = tk.Button(clientMaster, text="Submit", command=lambda : submitName(clientConnection)).grid(row=8,column=1)


def submitName(sendClient, event=None):
    clientPlayerOne.playerOneUsername = nameHold.get()
    try:
        if clientPlayerOne.playerOneUsername.isalnum():
            sendClient.send(clientPlayerOne.playerOneUsername.encode())

            #clientMaster.destroy()
            for x in clientMaster.grid_slaves():
                    x.destroy()

            setUpGame(clientPlayerOne.playerOneUsername)
        else:
            raise invalidNameError
    except invalidNameError:
        nameValidLabel.configure(text='Invalid name, only use alphanumeric characters', fg='red')
        nameValidLabel.grid(row=7,column=1)

def buttonClk(button):
    if button['text'] == '':
        if not clientPlayerOne.isGameFinished('O'):
            clientPlayerOne.playMoveOnBoard(button, labelLastPlayer)
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
        clientSocket.send(playerMoveSend.encode())
    except Exception:
        connectionLost()
    receiveData()

def receiveData():
    """ Previous code, worked well for receiving and printing, but not for transmitting
    print('Waiting')
    while True:
        playerMove = (clientSocket.recv(1024)).decode()
        print("P2:", playerMove)
        if playerMove != None: break
        """
    while True:
        storedButton = ''
        try:
            buttonIndex = (clientSocket.recv(1024)).decode()
            if buttonIndex == '':
                buttonIndex = 'Empty Thing'
            #print('Received', buttonIndex)
            if buttonIndex == 'Play Again' and (clientPlayerOne.isGameFinished('O') or clientPlayerOne.isBoardFull()):
                #print('Game Over')
                endChoice('Play Again')
                break
            elif buttonIndex == 'Fun Times':
                endChoice('Fun Times')
                break
            #This code only runs when it receives data from player2
            elif buttonIndex != '':
                for (index,row) in enumerate(clientPlayerOne.buttonDataTable):
                    for (subindex,element) in enumerate(row):
                        stripped = btnToNum(element)
                        if not stripped.isdigit():
                            stripped = '1'
                        if buttonIndex == stripped:
                            storedButton = clientPlayerOne.buttonDataTable[index][subindex]
                clientPlayerOne.playMoveOnBoard(storedButton, labelLastPlayer)
                if str(storedButton) != '': 
                    #Handles situation when player 2 says to replay
                    if clientPlayerOne.isGameFinished('X'):
                        message = (clientSocket.recv(1024)).decode()
                        endChoice(message)
                    if clientPlayerOne.isBoardFull():
                        message = (clientSocket.recv(1024)).decode()
                        endChoice(message)
                    break
            else:
                break
        except Exception:
            connectionLost()

def connectionLost():
    userChoice = tk.messagebox.showinfo(title="Tic-Tac-Toe - Host", message = "Connection Lost")
    if userChoice:
        clientMaster.destroy()
    
    #serverSocket.close()

    #if contToRun:
    #    playerMove = (client.recv(1024)).decode()
    #    print("P2:", playerMove)
    #    playerMove = "Me : "
    #    client.send(playerMove.encode())

    #Limits the number of connections to 1, and ceases anyone else from connecting
    #connectionCounter += 1
    #if connectionCounter == 1:
        #contToRun = False
        #serverSocket.close()

def endChoice(message):
    #print('Resetting Game . . ')
    if message == 'Play Again':
        clientPlayerOne.resetGameBoard()
        for x in clientMaster.winfo_children():
            x.destroy()
        setUpGame(clientPlayerOne.playerOneUsername)
    else:
        for x in clientMaster.winfo_children():
            x.destroy()
        statsPage()

def statsPage():
    statData = clientPlayerOne.computeStats()

    clientMaster.title("{chegg}'s Statistics".format(chegg=clientPlayerOne.playerOneUsername))
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

    clientPlayerOne.lastPlayerName = clientPlayerOne.playerTwoUsername
    clientPlayerOne.clientName = clientPlayerOne.playerOneUsername

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
    buttonOne.config(state='disabled')
    buttonOne.grid(row=1, column=1)
    buttonTwo = tk.Button(bottomHalfFrame, text='', font="Futura", height=3, width=6, command=lambda: buttonClk(buttonTwo))
    buttonTwo.config(state='disabled')
    buttonTwo.grid(row=1, column=2)
    buttonThree = tk.Button(bottomHalfFrame, text='', font="Futura", height=3, width=6, command=lambda: buttonClk(buttonThree))
    buttonThree.config(state='disabled')
    buttonThree.grid(row=1, column=3)
        
    #2nd Row
    buttonFour = tk.Button(bottomHalfFrame, text='', font="Futura", height=3, width=6, command=lambda: buttonClk(buttonFour))
    buttonFour.config(state='disabled')
    buttonFour.grid(row=2, column=1)
    buttonFive = tk.Button(bottomHalfFrame, text='', font="Futura", height=3, width=6, command=lambda: buttonClk(buttonFive))
    buttonFive.config(state='disabled')
    buttonFive.grid(row=2, column=2)
    buttonSix = tk.Button(bottomHalfFrame, text='', font="Futura", height=3, width=6, command=lambda: buttonClk(buttonSix))
    buttonSix.config(state='disabled')
    buttonSix.grid(row=2, column=3)
        
    #3rd Row
    buttonSeven = tk.Button(bottomHalfFrame, text='', font="Futura", height=3, width=6, command=lambda: buttonClk(buttonSeven))
    buttonSeven.config(state='disabled')
    buttonSeven.grid(row=3, column=1)
    buttonEight = tk.Button(bottomHalfFrame, text='', font="Futura", height=3, width=6, command=lambda: buttonClk(buttonEight))
    buttonEight.config(state='disabled')
    buttonEight.grid(row=3, column=2)
    buttonNine = tk.Button(bottomHalfFrame, text='', font="Futura", height=3, width=6, command=lambda: buttonClk(buttonNine))
    buttonNine.config(state='disabled')
    buttonNine.grid(row=3, column=3)

    quitButton = tk.Button(bottomHalfFrame, text="Quit", command=lambda: clientMaster.destroy()).grid(row=9, column=2)
        
    clientPlayerOne.buttonDataTable[0][0] = buttonOne
    clientPlayerOne.buttonDataTable[0][1] = buttonTwo
    clientPlayerOne.buttonDataTable[0][2] = buttonThree
    clientPlayerOne.buttonDataTable[1][0] = buttonFour
    clientPlayerOne.buttonDataTable[1][1] = buttonFive
    clientPlayerOne.buttonDataTable[1][2] = buttonSix
    clientPlayerOne.buttonDataTable[2][0] = buttonSeven
    clientPlayerOne.buttonDataTable[2][1] = buttonEight
    clientPlayerOne.buttonDataTable[2][2] = buttonNine

    #Centre aligns the Tic Tac Toe Grid
    bottomHalfFrame.grid_rowconfigure((0, 4), weight=1)
    bottomHalfFrame.grid_columnconfigure((0, 4), weight=1)
    bottomHalfFrame.pack(fill='x')
    
    if titleName == clientPlayerOne.lastPlayerName:
        labelLastPlayer.set("Your turn")
    else:
        labelLastPlayer.set(clientPlayerOne.playerTwoUsername + "'s turn")
    playerNameLabel.pack(fill='x')
    threading._start_new_thread(receiveData, tuple(''))


if __name__ == '__main__':
    clientPlayerOne = gameboard.BoardClass()
    clientMaster = tk.Tk()
    clientMaster.title("Tic-Tac-Toe - Server Host")
    clientMaster.geometry('350x190')
    clientMaster.resizable(0,0)
    labelLastPlayer = tk.StringVar()
    nameHold = tk.StringVar()
    ipAddress = tk.StringVar()
    ipPort = tk.IntVar()
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connectionFail = False
    clientSocket = ''


    nameValidLabel = tk.Label(clientMaster, text='', font='Futura, 8', fg='red')
    statusLabel = tk.Label(clientMaster, text='', font='Futura, 8')
    nameValidLabel = tk.Label(clientMaster, text='', font='Futura, 8', fg='red')

    addressLabel = tk.Label(clientMaster, text = "Create IP Address:").grid(row=0,column=0)
    addressEntry = tk.Entry(clientMaster, textvariable=ipAddress).grid(row=0,column=1)
    portLabel = tk.Label(clientMaster, text = "Create Port Value:").grid(row=1,column=0)
    portEntry = tk.Entry(clientMaster, textvariable=ipPort).grid(row=1,column=1)

    connectButton = tk.Button(clientMaster, text="Establish", command=lambda : serverCreate()).grid(row=4,column=1)

    clientMaster.mainloop()
    