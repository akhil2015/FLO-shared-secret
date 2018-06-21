#!/usr/bin/env python3
from tkinter import *

class GUI:
    
    def __init__(self, root):
        self.root = root

    def Main(self):
        try:
            self.PostFrame.destroy()
        except:
            None
        try:
            self.GetFrame.destroy()
        except:
            None
        self.MainFrame = Frame(self.root)
        self.MainFrame.pack()
        WelcomeLabel = Label(self.MainFrame,text="Welcome To FloSecret App")
        WelcomeLabel.pack()
        PostButton = Button(self.MainFrame,text="POST",command=self.Post)
        PostButton.pack()
        GetButton = Button(self.MainFrame,text="GET",command=self.Get)
        GetButton.pack()
        
    def Post(self):
        self.MainFrame.destroy()
        self.PostFrame = Frame(self.root)
        self.PostFrame.pack()
        PL1 = Label(self.PostFrame,text="Enter Total Number of shares : ")
        PL1.grid(row=1, column =1)
        self.PE1 = Entry(self.PostFrame)
        self.PE1.grid(row=1, column =2)
        PL2 = Label(self.PostFrame,text="Enter Minimum Number of required shares : ")
        PL2.grid(row=2, column =1)
        self.PE2 = Entry(self.PostFrame)
        self.PE2.grid(row=2, column =2)
        PL3 = Label(self.PostFrame,text="Enter the message to be encrypted")
        PL3.grid(row=3, column =1, columnspan=2)
        self.PTextBox = Text(self.PostFrame,height=10,width=50)
        PScroll = Scrollbar(self.PostFrame)
        self.PTextBox.configure(yscrollcommand=PScroll.set)
        self.PTextBox.grid(row=4, column =1, columnspan=2)
        PScroll.grid(row=4, column =1,sticky = E,columnspan=2)
        PBackButton=Button(self.PostFrame,text="Back",command=self.Main)
        PBackButton.grid(row=5, column =1)
        PNextButton=Button(self.PostFrame,text="Post",command=self.SendToFlo)
        PNextButton.grid(row=5, column =2)

    

    def SendToFlo(self):
        #get a master key
        #encrypt using AES
        #store in FLO Blockchain
        #return the hash n shared keys
        return
        

    def Get(self):
        self.MainFrame.destroy()
        self.GetFrame = Frame(self.root)
        self.GetFrame.pack()
        GL1 = Label(self.GetFrame,text="Enter Number of required shares :  ")
        GL1.grid(row=1,column=1)
        self.GE1 = Entry(self.GetFrame)
        self.GE1.grid(row=1,column=2)
        GL2 = Label(self.GetFrame,text="Enter Transaction hash : ")
        GL2.grid(row=2,column=1)
        self.GE2 = Entry(self.GetFrame)
        self.GE2.grid(row=2,column=2)
        GButton = Button(self.GetFrame,text="Find Secret",command=self.GetSharedKey)
        GButton.grid(row=3,column=1)
        GBackButton=Button(self.GetFrame,text="Back",command=self.Main)
        GBackButton.grid(row=3,column=2)

    def GetSharedKey(self):
        try:
            numOfShares = int(self.GE1.get())
        except:
            print("Invalid Int")
            return
        GLArray = [None] * numOfShares
        GEArray = [None] * numOfShares
        for i in range(numOfShares):
            GLArray[i] = Label(self.GetFrame, text="Shared key #"+str(i+1))
            GLArray[i].grid(column=1)
            GEArray[i] = Entry(self.GetFrame)
            GEArray[i].grid(column=2)
        GButton2 = Button(self.GetFrame,text="Decrypt",command=self.DecryptMsg)
        GButton2.grid(column=1, columnspan=2)

    def DecryptMsg(self):
        #retrive the encryted data from the transaction in FLO blkchain
        #decrypt the message using AES and shared key
        #display the message
        return
            
        

root = Tk()
root.title("FloSecret")
gui = GUI(root)
gui.Main()
root.mainloop()
    
        
