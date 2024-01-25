#to find starting address of pt, the pm[s] multiply the s by 2 and add 1 then multiply by 512
#PM[2s] is the size of a segment so that  S*2 AND THEN the corresponding value in pm table is the value
#line 1 is the triple of integers to define contents of segment table  st
#line 2 is the triple that dfins contents of pt
#segment table keeps track of starting address of all segments
#number of bits to represent s,p,w determine size of segment table, pt, and each page
#pmArr = [None] * 524288
from collections import deque
import os
import math

class PhysicalM: #ready and blocked state or running
    
   def __init__(self,filename):
      self.pmArr = [0] * 524288
      self.diskArr = [[0 for i in range(512)] for j in range(1024)]
      # self.freeFrame = [i for i in range(2,1024)] #ONLTY INITIALIZE FRAMES THAT ARE NOT FILLED SO CHECK THAT in a forl oop
      self.freeFrame = []
      self.s = None
      self.p = None
      self.w = None
      self.pw = None
      self.frames1 = [0,1]
      self.filename = filename
      if(filename=="init-dp.txt"):
         self.writefile = open("output-dp.txt","w")
      

   def putinFile(self, char):
        if char == "start" and self.newLine:
            self.writefile.write("\n0 ")
        elif char == "start":
            self.writefile.write("0 ")
            self.newLine = True
        else:
            self.writefile.write(str(char)+" ")

   def initializePM1(self,s,z,f): #st
      segment = s #8
      frame = f #3
      size = z #4000

      if frame>=0:
         self.frames1.append(frame)

      self.pmArr[2*segment] = size #size of segment s (in this case s)
      self.pmArr[2*segment+1] = frame  #frame f of segment s
 
   def initializePM2(self,s,p,f): #pt
      segment = s #8
      frame = f #8
      page = p #5

      if frame>=0:
         self.frames1.append(frame)
      if self.pmArr[2*segment+1] < 0:
         print("BRO", self.pmArr[2*segment+1])
         self.diskArr[abs(self.pmArr[2*segment+1])][page] = frame
         print("correct frame", self.diskArr[abs(self.pmArr[2*segment+1])][page])
      else:
         self.pmArr[self.pmArr[2*segment+1]*512+page] = frame

   def initfreeFrame(self):
      for i in range(2,1024):
         if i not in self.frames1:
            self.freeFrame.append(i)


   def extractOffset(self,address):
      self.s = address >> 18
      self.w = address & 0x1FF
      self.p = (address >> 9) & 0x1FF
      self.pw = address & 0x3FFFF


   def read_block(self,b, m):
      index = m
      for i in range(512):
         self.pmArr[index] = self.diskArr[b][i]
         index += 1
      #print(self.pmArr)
      #self.pmArr[m] = self.diskArr[b][m]
  
      

   def VAtoPA(self):
      if(self.pw >= self.pmArr[2*self.s]):
         self.putinFile(-1)
         return -1

      frameNumber = self.pmArr[(self.pmArr[2*self.s+1]*512)+self.p]
     
      block = self.pmArr[2*self.s+1]
    
      if(block < 0):#page fault need new pt
         print("BUS")

         f1 = self.freeFrame.pop(0)      
         self.read_block(abs(block),f1*512)

         self.pmArr[2*self.s+1] = f1
       

      frameNumber = self.pmArr[self.pmArr[2*self.s + 1]*512 + self.p] 
      #print(frameNumber)
      #print("framenum:",frameNumber)
      if (frameNumber < 0):
         print("FRAMEW")

         f2 = self.freeFrame.pop(0)
         #print(f2)
         self.read_block(abs(frameNumber),f2*512)

         self.pmArr[(self.pmArr[2*self.s+1]*512)+self.p] = f2
      
      
      pa = self.pmArr[self.pmArr[2*self.s + 1]*512 + self.p]*512 + self.w
      self.putinFile(pa)
      return pa
   

    
if __name__ == "__main__":

   #output reads va and translates to pa

   #open("output.txt","w")


   #init
   doneInit2 =0
   filename = input("Enter initialise file: ")
   test = PhysicalM(filename)
   lineCount = 0
   pathtofile = os.path.join(os.path.dirname(__file__), filename)
   with open(pathtofile,'r') as inputfiles:
        
        for line in inputfiles:
            #print(line)

            lst = line.strip().split()
            if(lineCount <3):
               triplets = [(lst[i], lst[i+1], lst[i+2]) for i in range(0, len(lst), 3)]
               print(triplets)

            lineCount += 1
            if lineCount == 1:
               for trip in triplets:
                  test.initializePM1(int(trip[0]),int(trip[1]),int(trip[2]))
            elif lineCount == 2:
               print("lenght list", len(triplets))
               for trip in triplets:
                  test.initializePM2(int(trip[0]),int(trip[1]),int(trip[2]))
                  doneInit2 += 1
               if doneInit2 == len(triplets):
                  test.initfreeFrame()
            elif lineCount >=3:
               print(lst)
               for i in lst:
                  test.extractOffset(int(i))
                  (test.VAtoPA())

