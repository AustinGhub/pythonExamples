from collections import deque
import os

class Processes: #ready and blocked state or running
    def __init__(self,state ,priority,id):
        self.state = state
        self.parent = None
        self.children = deque()
        self.resources = [] #r resrouce and k num units of i held
        self.kunits = 0 #number of units i is holding 
        self.id = id #name of process id
        self.priority = priority
        #self.status = status

    def setParent(self, parent):
        self.parent = parent

    def resourceRelease(self, id, units):
        for resourcelist in self.resources:
            if resourcelist[0] == id and (units-resourcelist[1] >=0):
                units -= resourcelist[1]
                self.resources.remove(resourcelist)

class Resources: #free and allocated state
    def __init__(self,id,resourceUnits,state):
        self.state = state
        self.maxResource = resourceUnits
        self.waitlist = deque() #i is waiting process and k for number of requested units
        self.units =  resourceUnits#counter keep track of units of resoures
        self.id = id #name of resource id
        self.stateCount = 7

    def addtoWaitlist(self, index, units):
        self.waitlist.append(tuple((index,units)))

#{"state": ready, "waitlist": []}

class Manager:
    def __init__(self):
        self.pcbList = [] #holds process class objects
        self.rcbList = []
        self.rl0= deque()
        self.rl1 = deque()
        self.rl2 = deque()
        self.currprocess = None
        makeoutput = open("output.txt", "w")

        self.writefile = open("output.txt", "r+")
        self.newLine = False

    def putinFile(self, char):
        if char == "start" and self.newLine:
            self.writefile.write("\n0 ")
        elif char == "start":
            self.writefile.write("0 ")
            self.newLine = True
        else:
            self.writefile.write(str(char)+" ")
    #creates a new process
    def create(self, priorityNum): #parentpcb is the list and priority is the input
        #priorityNum = int(priorityNum)
        if(priorityNum == 0):
            self.putinFile(-1)
        for i in range(len(self.pcbList)): #find lowest index to put the pcb into
            if self.pcbList[i] == None:
                #process(stae, priority, id)
                newProcess = Processes("ready", priorityNum,i) #allocate new pcb j 
                self.pcbList[i] = newProcess 
                newProcess.id = i
                self.currprocess.children.append(newProcess) #insert process j into children of i parent
                newProcess.parent = self.currprocess #make the parent of new process i ccc
                # if int(priorityNum)>int(self.currprocess.priority):
                #     self.currprocess = newProcess

                #insert j into readylist
                if priorityNum == 0:
                    self.rl0.append(newProcess)
                    #print("add 0")
                elif priorityNum == 1:
                    self.rl1.append(newProcess)
                    #print("add 1")
                elif priorityNum == 2:
                    self.rl2.append(newProcess)

                self.scheduler()
                self.putinFile(self.currprocess.id)
                print(self.currprocess.id)
                return
            elif i == 15:
                self.putinFile(-1)
    # def sortRL(self):
    #     self.rl = sorted(self.rl, key=lambda x: x.priority)

    def checkKid(self, index):
        if self.pcbList[index] == None:
            return False
        parentProcess = self.pcbList[index].parent
        if (index == 0 or parentProcess.id == 0):
            return False

        if(self.currprocess.id == index) or (self.currprocess.id == 0):
            return True

        if(parentProcess.id == self.currprocess.id):
            return True
        else:
            return self.checkKid(parentProcess.id)
  
    def destroy(self,indexDestroy):
        if self.checkKid(indexDestroy) == False:
            print("-1")
            self.putinFile(-1)
            return

        if self.pcbList[indexDestroy] == None:
            print("-1")
            #print("DOES NOT EXIST")
            self.putinFile(-1)
            return

        for k in self.pcbList[indexDestroy].children.copy(): #going through list of children = [process1,process2]
            self.destroy(k.id)

        #releaes resource
        for resourcebro in self.pcbList[indexDestroy].resources:
            for rsource in self.pcbList[indexDestroy].resources:
                if (rsource[0] == resourcebro[0]) and (resourcebro[1]-rsource[1] >=0):
                    resourcebro[1] -= rsource[1]
                    self.pcbList[indexDestroy].resources.remove(rsource)
            self.rcbList[indexDestroy].units += resourcebro[1]
            self.rcbList[indexDestroy].state = "free"

            while(len(self.rcbList[indexDestroy].waitlist)>0 and self.rcbList[indexDestroy].units > 0):
                getNext = self.rcbList[indexDestroy].waitlist[0]
                if(self.rcbList[indexDestroy].units >= getNext[1]):
                    self.rcbList[indexDestroy].units -= getNext[1]
                    if(self.rcbList[indexDestroy].units ==0):
                        self.rcbList[indexDestroy].state = "allocated"

                    self.pcbList[getNext[0]].resources.append([indexDestroy, getNext[1]])
                    self.pcbList[getNext[0]].state = "ready"
                    self.rcbList[indexDestroy].waitlist.popleft()
                    
                    if self.pcbList[getNext[0]].priority == 0:
                        self.rl0.append(self.pcbList[getNext[0]])
                    if self.pcbList[getNext[0]].priority == 1:
                        self.rl1.append(self.pcbList[getNext[0]])
                    if self.pcbList[getNext[0]].priority == 2:
                        self.rl2.append(self.pcbList[getNext[0]])
                else:
                    break
        self.pcbList[indexDestroy].resources.clear()

        #remove from rl
        if self.pcbList[indexDestroy].state == "ready":
            if self.pcbList[indexDestroy].priority == 0:
                self.rl0.remove(self.pcbList[indexDestroy])
            if self.pcbList[indexDestroy].priority == 1:
                self.rl1.remove(self.pcbList[indexDestroy])
            if self.pcbList[indexDestroy].priority == 2:
                self.rl2.remove(self.pcbList[indexDestroy])

        
        #still need waitlist
    
        for rsource in self.rcbList:
            if rsource.waitlist:
                for pairs in rsource.waitlist.copy():
                    if pairs[0] == self.pcbList[indexDestroy].id:
                        rsource.waitlist.remove([pairs[0],pairs[1]])


        #remove from parent's list of children
        parentProcess = self.pcbList[self.pcbList[indexDestroy].parent.id] #gets the index of parent
        parentProcess.children.remove(self.pcbList[indexDestroy])
        self.pcbList[indexDestroy] = None
        #self.putinFile(self.currprocess.id)
        self.scheduler()
        return

    def request(self,resourceIndex,kUnitsReq):
        #if(resourceIndex == 0)
        if ((resourceIndex > 3) or (resourceIndex < 0)):

            print("-1")
            self.putinFile(-1)
            return
        
        if((kUnitsReq == 0) or (self.currprocess.id == 0)):
            print("-1")
            self.putinFile(-1)
            return
        
        if self.rcbList[resourceIndex].maxResource >= kUnitsReq:
            print("bro this is max resrouce:" ,self.rcbList[resourceIndex].maxResource)
            unitsAvailable = self.rcbList[resourceIndex].units
            if kUnitsReq <= unitsAvailable:
                self.rcbList[resourceIndex].units -= kUnitsReq
                if self.rcbList[resourceIndex].units == 0:
                    self.rcbList[resourceIndex].state = "allocated"
                self.currprocess.resources.append([resourceIndex, kUnitsReq])
            else:
                self.rcbList[resourceIndex].waitlist.append([self.currprocess.id, kUnitsReq])
                self.currprocess.state = "blocked"
                self.scheduler()
            self.putinFile(self.currprocess.id)
        else:
            self.putinFile("-1") 



    def release(self, resourceIndex,kunits):
        #print("MUCHELSLLSSL")
        if(resourceIndex > 3 or resourceIndex < 0):
            print("-1")
            self.putinFile(-1)
            print("bruh1")
            return
        
        if(kunits == 0 or kunits>3 or self.currprocess.id == 0):
            print("-1")
            self.putinFile(-1)
            print("Bruh2")
            return
        temp = False

        for rsource in self.currprocess.resources:
            if rsource[0] == resourceIndex:
                temp = True
                break

        if temp == False:
            self.putinFile(-1)
            print("-1")
            print("Bruh3")

            return
        
        availableUnits = 0
        for rsource in self.currprocess.resources:
            if rsource[0] == resourceIndex:
                availableUnits += rsource[1]
        if availableUnits != kunits:
            self.putinFile(-1)
            print("-1")
            print("Bruh4")
            return
        

        for i in self.currprocess.resources:
            if(i[0] == resourceIndex) and (kunits - i[1] >= 0):
                kunits -= i[1]
                self.currprocess.resources.remove(i)
        self.rcbList[resourceIndex].units += kunits
        self.rcbList[resourceIndex].state = "free"

        while(len(self.rcbList[resourceIndex].waitlist)>0 and self.rcbList[resourceIndex].units > 0):
            getNext = self.rcbList[resourceIndex].waitlist[0]
            if(self.rcbList[resourceIndex].units >= getNext[1]):
                self.rcbList[resourceIndex].units -= getNext[1]
                if(self.rcbList[resourceIndex].units ==0):
                    self.rcbList[resourceIndex].state = "allocated"

                self.pcbList[getNext[0]].resources.append([resourceIndex, getNext[1]])
                self.pcbList[getNext[0]].state = "ready"
                self.rcbList[resourceIndex].waitlist.popleft()
                
                if self.pcbList[getNext[0]].priority == 0:
                    self.rl0.append(self.pcbList[getNext[0]])
                if self.pcbList[getNext[0]].priority == 1:
                    self.rl1.append(self.pcbList[getNext[0]])
                if self.pcbList[getNext[0]].priority == 2:
                    self.rl2.append(self.pcbList[getNext[0]])
            else:
                break
        self.scheduler()
        print(self.currprocess.id)
        self.putinFile(self.currprocess.id)
        

    def timeout(self):
        self.currprocess.state = "ready"

        if self.currprocess.priority == 0:
            self.rl0.append(self.currprocess)
        if self.currprocess.priority == 1:
            self.rl1.append(self.currprocess)
        if self.currprocess.priority == 2:
            self.rl2.append(self.currprocess)

        self.scheduler()
        self.putinFile(self.currprocess.id)
        print(self.currprocess.id)

    def scheduler(self):
        high_priority = None
        if self.rl0:
            high_priority = self.rl0[0]
        if self.rl2:
            for i in self.rl2:
                if i.state != "blocked":
                    high_priority = i
                    break
        elif self.rl1:
            for i in self.rl1:
                if i.state != "blocked":
                    high_priority = i
                    break

        if (not high_priority) or (self.currprocess.state == "running" and self.currprocess.priority >= high_priority.priority):
            return
        # if ((high_priority.priority < self.currprocess.priority) or (self.currprocess.state=="running") or(self.currprocess in self.pcbList)):
        #     return
        if self.currprocess.state == "running":
            self.currprocess.state = "ready"
            if self.currprocess.priority == 0:
                self.rl0.append(self.currprocess)
            if self.currprocess.priority == 1:
                self.rl1.append(self.currprocess)
              
            if self.currprocess.priority == 2:
                self.rl2.append(self.currprocess)

        high_priority.state = "running"
        if high_priority.priority == 0:
            self.rl0.remove(high_priority)

        if high_priority.priority == 1:
            self.rl1.remove(high_priority)

        if high_priority.priority == 2:
            self.rl2.remove(high_priority)

        self.currprocess = high_priority


    def initialize(self): #first command is in
        #print("0")
        #self.putinFile("0")
        self.pcbList = [None]*16 #h
        #print(self.pcbList,"\n")
        #process(state,priority,id)
        newProcess = Processes("running",0,0) #running priority 0
        self.pcbList[0] = newProcess
        self.rl0.append(newProcess)
        self.rl1 = deque()
        self.rl2 = deque()
        #newProcess.id = 0

        #make rcblist for the resources
        resource1 = Resources("0",1, "free")
        resource2 = Resources("1",1, "free")
        resource3 = Resources("2",2, "free")
        resource4 = Resources("3",3, "free")

        self.rcbList.append(resource1)
        self.rcbList.append(resource2)
        self.rcbList.append(resource3)
        self.rcbList.append(resource4)

        self.currprocess = newProcess
        self.putinFile("start")


if __name__ == "__main__":
  
    startMan = Manager()
    makeoutput = open("output.txt", "w")
    makeoutput.close()

    filename = input("filename is: ")
    pathtofile = os.path.join(os.path.dirname(__file__), filename)
    with open(pathtofile,'r') as inputfiles:
        for line in inputfiles:
            #print(line)
            tokens = line.strip().split()
            if(len(tokens)>0):
                if(tokens[0] == "in"):
                    startMan.initialize()
                #print('0')
                elif(tokens[0] == "cr"):
                    startMan.create(int(tokens[1]))
                elif(tokens[0] == "de"):
                    startMan.destroy(int(tokens[1]))
                    startMan.putinFile(startMan.currprocess.id)
                    #startMan.putinFile("-1")
                    #print(startMan.currprocess.id)
                elif(tokens[0] == "rq"):
                    startMan.request(int(tokens[1]), int(tokens[2]))
                elif(tokens[0] =="rl"):
                    startMan.release(int(tokens[1]), int(tokens[2]))
                elif(tokens[0] == "to"):
                    startMan.timeout()


