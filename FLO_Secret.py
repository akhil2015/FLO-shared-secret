#!/usr/bin/env python3
from tkinter import *
from tkinter import messagebox
from secretsharing import PlaintextToHexSecretSharer
import base64
import os
from Crypto.Cipher import AES
import subprocess
from more_itertools import sliced
import json


# This function splits the secret and returns a list of shares
def splitSecret(secret,threshold,splits):
    #Formatting key inorder to convert bytes of string using base64
    secret = base64.b64encode(secret).decode('utf-8')
    shares = PlaintextToHexSecretSharer.split_secret(secret, threshold, splits)
    return shares

# This function recovers the secret using the list of shares and returns the reconstructed secret
def recoverSecret(shares):
    secret = PlaintextToHexSecretSharer.recover_secret(shares)
    #Converting recovered_key to bytes using base64 module
    secret=base64.b64decode(secret)
    return secret

def pad(data):
    padding = 16 - len(data) % 16
    return data + padding * chr(padding+97)

def unpad(data):
    data = str(data)
    padding =  ord(data[-2]) - 96
    return data[2:-padding]

def keyGen():
    # Generating random key of 32 bytes
    key = os.urandom(32)
    return key


def encryptMsg(plaintext, key):
    # Initialization vector in AES should be 16 bytes
    IV = 16 * '\x00'
    # Creation of encryptor and decryptor object using above details
    cipher = AES.new(key, AES.MODE_CBC, IV)
    ciphertext = cipher.encrypt(pad(plaintext))
    ciphertext = base64.b64encode(ciphertext).decode('utf-8')
    return ciphertext


def decryptMsg(ciphertext, key):
    # Initialization vector in AES should be 16 bytes
    IV = 16 * '\x00'
    # Creation of encryptor and decryptor object using above details
    cipher = AES.new(key, AES.MODE_CBC, IV)
    ciphertext=base64.b64decode(ciphertext)
    return unpad(cipher.decrypt(ciphertext));

def writeUnitToBlockchain(text,receiver):
    txid = subprocess.check_output(["flo-cli","--testnet", "sendtoaddress",receiver,"0.01",'""','""',"true","false","10",'UNSET',str(text)])
    txid = str(txid)
    txid = txid[2:-3]
    return txid

def readUnitFromBlockchain(txid):
    rawtx = subprocess.check_output(["flo-cli","--testnet", "getrawtransaction", str(txid)])
    rawtx = str(rawtx)
    rawtx = rawtx[2:-3]
    tx = subprocess.check_output(["flo-cli","--testnet", "decoderawtransaction", str(rawtx)])
    content = json.loads(tx)
    text = content['floData']
    return text

def writeDatatoBlockchain(text):
    n_splits = len(text)//350 + 1               #number of splits to be created
    splits = list(sliced(text, n_splits))       #create a sliced list of strings
    tail = writeUnitToBlockchain(splits[n_splits],'oV9ZoREBSV5gFcZTBEJ7hdbCrDLSb4g96i')      #create a transaction which will act as a tail for the data
    cursor = tail
    if n_splits == 1:
        return cursor                           #if only single transaction was created then tail is the cursor

    #for each string in the list create a transaction with txid of previous string
    for i in range(n_splits-1,0):
        splits[i] = 'next:'+cursor+splits[i]
        cursor = writeUnitToBlockchain(splits[i])
    return cursor

def readDatafromBlockchain(cursor):
    text = []
    cursor_data = readUnitFromBlockchain(cursor)
    text.append(cursor_data[69:])                  
    while(cursor_data[:5]=='next:'):
        cursor = cursor_data[5:69]
        cursor_data = readUnitFromBlockchain(cursor)
        text.append(cursor_data[69:])
    text.join('')
    return text

class GUI:
    
    def __init__(self, root):
        self.root = root
        self.frame = Frame(self.root)
        self.vcmd = (self.frame.register(self.onValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
    
    #validation for input as integers
    def onValidate(self, d, i, P, s, S, v, V, W):
        ind=int(i)
        if d == '1': #insert
            if not P[ind].isdigit():
                return False
        return True


    def Main(self):
        try:
            self.PostFrame.destroy()
        except:
            None
        try:
            self.GetFrame.destroy()
        except:
            None
        self.MainFrame = Frame(self.root, height=1000,width=500)
        self.MainFrame.pack()
        WelcomeLabel = Label(self.MainFrame,text="Welcome To FLO-Secret App",font=("Arial", 20))
        WelcomeLabel.grid(column = 1, columnspan =2)
        label =Label(self.MainFrame,text=" ")
        label.grid(row = 2, columnspan =2)
        PostButton = Button(self.MainFrame,text="POST",command=self.Post)
        PostButton.grid(row =3,column=1)
        GetButton = Button(self.MainFrame,text="GET",command=self.Get)
        GetButton.grid(row =3, column=2)
        contentText = "\n\nWhat is this?\n\tThis app let you save encrypted secret in the FLO blockchain and produces a number of keys that must be combined to be able to decrypt the secret.\n\nThis is a zero knowledge application.\n\tThe creation of the master key and shared keys and the encryption of the secret with the main key happens in the app. The app then sends the encrypted information to be posted in the FLO blockchain. This is the only information sent to our servers. The server reply with the hash of the transaction and the app produces the pdf containing information about the shares and the transaction.\n\nHow to encrypt an information? \n\tCurrently, we are only supporting messages typed or copied to a text area. Click in POST, select the number of total shares and the number of required shares, type or paste the information and click Submit.\n\nHow to decrypt a secret?\n\tClick in GET, type the number of minimum required shares and the hash of the transaction and press Find secret. Then insert the hash of each share and click decrypt. If everything is ok, you should be able to see the decrypted information."
        Context = Message(self.MainFrame, text = contentText)
        Context.grid(column = 1, columnspan =2)
        
    def Post(self):
        self.MainFrame.destroy()
        self.PostFrame = Frame(self.root)
        self.PostFrame.pack()
        PL1 = Label(self.PostFrame,text="Enter Total Number of shares : ")
        PL1.grid(row=1, column =1)
        self.PE1 = Spinbox(self.PostFrame, from_ = 2, to = 1000, validate="key", validatecommand=self.vcmd)
        self.PE1.grid(row=1, column =2)
        PL2 = Label(self.PostFrame,text="Enter Minimum Number of required shares : ")
        PL2.grid(row=2, column =1)
        self.PE2 = Spinbox(self.PostFrame, from_ = 2, to = 1000, validate="key", validatecommand=self.vcmd)
        self.PE2.grid(row=2, column =2)
        PL3 = Label(self.PostFrame,text="Enter the message to be encrypted")
        PL3.grid(row=3, column =1, columnspan=2)
        PTextFrame = Frame(self.PostFrame)
        self.PTextBox = Text(PTextFrame,height=10,width=50)
        PScroll = Scrollbar(PTextFrame)
        PScroll.config( command = self.PTextBox.yview )
        self.PTextBox.pack(side = LEFT)
        PScroll.pack(side = RIGHT,fill = Y )
        PTextFrame.grid(column=1,columnspan=2)
        PBackButton = Button(self.PostFrame,text="Back",command=self.Main)
        PBackButton.grid(row=5, column =1)
        self.PNextButton = Button(self.PostFrame,text="Submit",command=self.Encryption)
        self.PNextButton.grid(row=5, column =2)

    def Encryption(self):
        splits = int(self.PE1.get())
        threshold = int(self.PE2.get())
        if (threshold > splits) :
            messagebox.showwarning("Invalid", "Total-Shares should be greater than or equal to Minimum-Shares-Required")
            return
        self.PE1.config(state='disabled')
        self.PE2.config(state='disabled')
        self.PTextBox.config(state='disabled')
        key = keyGen() 
        plaintext = self.PTextBox.get("1.0",'end-1c')
        shared_key = splitSecret(key,threshold,splits)
        print("Shared Keys="+str(shared_key))
        ciphertext = encryptMsg(plaintext,key)
        print("Encrypted Text : " + ciphertext)
        txid = writeDatatoBlockchain(ciphertext)
        print('txid: ',txid)
        self.PNextButton.destroy()
        messagebox.showinfo("Successful", "Your message is successfully encrypted!!!")

        

    def Get(self):
        self.MainFrame.destroy()
        self.GetFrame = Frame(self.root)
        self.GetFrame.pack()
        GL1 = Label(self.GetFrame,text="Enter Number of required shares :  ")
        GL1.grid(row=1,column=1)
        self.GE1 = Spinbox(self.GetFrame, from_ = 2, to = 1000, validate="key", validatecommand=self.vcmd)
        self.GE1.grid(row=1,column=2)
        GL2 = Label(self.GetFrame,text="Enter Transaction id : ")
        GL2.grid(row=2,column=1)
        self.GE2 = Entry(self.GetFrame)
        self.GE2.grid(row=2,column=2)
        txid = self.GE2.get()
        self.GFindButton = Button(self.GetFrame,text="Find Secret",command=self.GetSharedKey)
        self.GFindButton.grid(row=3,column=2)
        self.GBackButton=Button(self.GetFrame,text="Back",command=self.Main)
        self.GBackButton.grid(row=3,column=1)

    def GetSharedKey(self):
        self.numOfShares = int(self.GE1.get())
        self.GFindButton.destroy()
        self.GBackButton.destroy()
        self.GE1.config(state='disabled')
        self.GE2.config(state='disabled')
        GLArray = [None] * self.numOfShares
        self.GEArray = [None] * self.numOfShares
        for i in range(self.numOfShares):
            GLArray[i] = Label(self.GetFrame, text="Shared key #"+str(i+1))
            GLArray[i].grid(column=1)
            self.GEArray[i] = Entry(self.GetFrame)
            self.GEArray[i].grid(column=2)
        self.GBackButton=Button(self.GetFrame,text="Back",command=self.Main)
        self.GBackButton.grid(column=1)
        self.GDecryptButton = Button(self.GetFrame,text="Decrypt",command=self.DecryptMsg)
        self.GDecryptButton.grid(column=2)

    def DecryptMsg(self):
        txid = self.GE2.get()
        ciphertext = readDatafromBlockchain(txid)
        shares = [None] * self.numOfShares
        for i in range(self.numOfShares):
            shares[i] = self.GEArray[i].get()
        try:
            key=recoverSecret(shares) 
            plaintext = decryptMsg(ciphertext,key)
        except:
            messagebox.showerror("Error", "Decryption Failed!!! Please insert the correct shared keys!")
            return
        for i in range(self.numOfShares):
            shares[i] = self.GEArray[i].config(state='disabled')
        self.GDecryptButton.destroy()
        self.GBackButton.destroy()
        GL3 = Label(self.GetFrame, text="Found Secret Message")
        GL3.grid(column=1, columnspan=2)       
        GTextFrame = Frame(self.GetFrame)
        GLMsg = Text(GTextFrame,height=10,width=50)
        GLMsg.insert(INSERT, plaintext)
        GLMsg.config(state='disabled')
        GScroll = Scrollbar(GTextFrame)
        GScroll.config( command = GLMsg.yview )
        GLMsg.pack(side = LEFT)
        GScroll.pack(side = RIGHT,fill = Y)
        GTextFrame.grid(column=1,columnspan=2)
        self.GBackButton=Button(self.GetFrame,text="Back",command=self.Main)
        self.GBackButton.grid(column=1)
            
        

root = Tk()
root.title("FloSecret")
gui = GUI(root)
gui.Main()
root.mainloop()
    
        
