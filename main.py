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
from fpdf import FPDF
import pyperclip

# This function splits the secret and returns a list of shares
def splitSecret(secret,threshold,splits):
    #Formatting key inorder to convert bytes of string using base64
    secret = base64.b64encode(secret).decode('utf-8')
    shares = PlaintextToHexSecretSharer.split_secret(secret, threshold, splits)
    for i in range(splits):
        shares[i]=base64.b64encode(shares[i].encode('utf-8')).decode('utf-8')
    return shares

# This function recovers the secret using the list of shares and returns the reconstructed secret
def recoverSecret(shares):
    for i in range(len(shares)):
        shares[i] = (base64.b64decode(shares[i])).decode('utf-8')
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
    # Genarating Initialization vector for AES (16 bytes)
    IV = os.urandom(16)
    # Encrypting The plaintext
    cipher = AES.new(key, AES.MODE_CBC, IV)
    plaintext=base64.b64encode(plaintext.encode('utf-8')).decode('utf-8')
    ciphertext = cipher.encrypt(pad(plaintext))
    # Append IV and Ciphertext
    ciphertext = base64.b64encode(IV).decode('utf-8') + base64.b64encode(ciphertext).decode('utf-8')
    return ciphertext


def decryptMsg(ciphertext, key):
    # Initialization vector in AES should be 16 bytes
    IV = base64.b64decode(ciphertext[:24])
    ciphertext=base64.b64decode(ciphertext[24:])
    # Creation of encryptor and decryptor object using above details
    cipher = AES.new(key, AES.MODE_CBC, IV)
    plaintext=unpad(cipher.decrypt(ciphertext));
    plaintext = (base64.b64decode(plaintext)).decode('utf-8')
    return plaintext

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
    n_splits = len(text)//350 + 1                                                               #number of splits to be created
    splits = list(sliced(text, 350))                                                            #create a sliced list of strings
    tail = writeUnitToBlockchain(splits[n_splits-1],'oV9ZoREBSV5gFcZTBEJ7hdbCrDLSb4g96i')       #create a transaction which will act as a tail for the data
    cursor = tail
    if n_splits == 1:
        return cursor                                                                           #if only single transaction was created then tail is the cursor

    #for each string in the list create a transaction with txid of previous string
    for i in range(n_splits-2,-1,-1):
        splits[i] = 'next:'+cursor+" "+splits[i]
        cursor = writeUnitToBlockchain(splits[i],'oV9ZoREBSV5gFcZTBEJ7hdbCrDLSb4g96i')
    return cursor

def readDatafromBlockchain(cursor):
    text = []
    cursor_data = readUnitFromBlockchain(cursor)              
    while(cursor_data[:5]=='next:'):
        cursor = cursor_data[5:69]
        #print("fetching this transaction->>"+cursor)
        text.append(cursor_data[70:])
        cursor_data = readUnitFromBlockchain(cursor)
    text.append(cursor_data)
    #print(text)
    text=('').join(text)
    return text

#This function is for generating the main pdf
def generatePDFmain(splits,threshold,shared_key,txid):
    pdf=FPDF()
    pdf.add_page()
    try:
        pdf.image('Flo.png',80,20,33)
        pdf.ln(50)
    except:
        pdf.set_font('Courier', '', 12)
        pdf.cell(40,40,'No Image',1,10,'C')
        pdf.ln(10)
    pdf.set_font('Courier', '', 50)
    pdf.multi_cell(0,10,'FLO Secret',0,'C',False)
    pdf.set_font('Courier', '', 12)
    pdf.multi_cell(0,10,'Powered by the FLO Blockchain',0,'C',False)
    pdf.set_font('Times', '', 16)
    pdf.ln(20)
    pdf.multi_cell(0,10,'A secret has been encrypted and posted on the blockchain of the FLO cryptocurrency and your Secret ID is: ',0,'J',False)
    pdf.set_font('Courier', '', 12)
    pdf.multi_cell(0,10,str(txid),1,'C',False)
    pdf.set_font('Times', '', 16)
    pdf.ln(10)
    pdf.multi_cell(0,10,'The key to decrypt this secret has been split in '+str(splits)+' shares. By design, the secret can be decrypted with any '+str(threshold)+' of these shares.',0,'J',False)
    for i in range(splits):
        pdf.set_font('Courier', '', 12)
        pdf.multi_cell(0,5,str(shared_key[i]),1,'L',False)
        pdf.ln(5)
    pdf.set_font('Times', '', 16)
    pdf.ln(10)
    pdf.multi_cell(0,10,'Use the FLO Secret app to decrypt the secret',0,'J',False)
    pdf.multi_cell(0,20,'Download FLO Secret from the below link',0,'J',False)
    pdf.set_font('Courier', '', 14)
    pdf.cell(0,0 ,'https://github.com/akhil2015/FLO-shared-secret',0,0,'L',False, "https://github.com/akhil2015/FLO-shared-secret");
    filename = 'Flo_Secret_'+txid+'.pdf'
    pdf.output(filename,'F')
    generatePDFshares(splits,threshold,shared_key,txid)

#This function is for generating the share pdf
def generatePDFshares(splits,threshold,shared_key,txid):
    for i in range(splits):
        pdf=FPDF()
        pdf.add_page()
        try:
            pdf.image('Flo.png',80,20,33)
            pdf.ln(50)
        except:
            pdf.set_font('Courier', '', 12)
            pdf.cell(40,40,'No Image',1,10,'C')
            pdf.ln(10)
        pdf.set_font('Courier', '', 50)
        pdf.multi_cell(0,10,'FLO Secret',0,'C',False)
        pdf.set_font('Courier', '', 12)
        pdf.multi_cell(0,10,'Powered by the FLO Blockchain',0,'C',False)
        pdf.set_font('Times', '', 16)
        pdf.ln(20)
        pdf.multi_cell(0,10,'A secret has been encrypted and posted on the blockchain of the FLO cryptocurrency and your Secret ID is : ',0,'J',False)
        pdf.set_font('Courier', '', 12)
        pdf.multi_cell(0,10,str(txid),1,'C',False)
        pdf.set_font('Times', '', 16)
        pdf.ln(10)
        pdf.multi_cell(0,10,'The key to decrypt this secret has been split in '+str(splits)+' shares like this one. By design, the secret can be decrypted with any '+str(threshold)+' of these shares.',0,'J',False)
        pdf.ln(10)
        pdf.multi_cell(0,10,'Below is the part of the key that belongs to this share',0,'J',False)
        pdf.set_font('Courier', '', 12)
        pdf.multi_cell(0,5,str(shared_key[i]),1,'L',False)
        pdf.set_font('Times', '', 16)
        pdf.ln(10)
        pdf.multi_cell(0,10,'Use the FLO Secret app to decrypt the secret',0,'J',False)
        pdf.multi_cell(0,20,'Download FLO Secret from the below link',0,'J',False)
        pdf.set_font('Courier', '', 14)
        pdf.cell(0,0 ,'https://github.com/akhil2015/FLO-shared-secret',0,0,'L',False, "https://github.com/akhil2015/FLO-shared-secret");
        filename = 'Flo_Secret_'+txid+'/sharedkey_'+str(i+1)+'.pdf'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        pdf.output(filename,'F')
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
        contentText = "\n\nWhat is this?\n\tThis app let you save encrypted secret in the FLO blockchain and produces a number of keys that must be combined to be able to decrypt the secret.\n\nThis is a zero knowledge application.\n\tThe creation of the master key and shared keys and the encryption of the secret with the main key happens in the app. The app then writes the encrypted information on the FLO blockchain. And the application generates a pdf with the secret ID and the shares of the encryption key\n\nHow to encrypt an information? \n\tCurrently, we are only supporting messages typed or copied to a text area. Click in POST, select the number of total shares and the number of required shares, type or paste the information and click Submit.\n\nHow to decrypt a secret?\n\tClick in GET, type the number of minimum required shares and Secret ID and press Find secret. Then insert the hash of each share and click decrypt. If everything is ok, you should be able to see the decrypted information."
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
        if (threshold > splits or threshold<2) :
            messagebox.showwarning("Invalid!", "Minimum-Shares-Required should be greater than 2 and lesser than or equal to Total-Shares")
            return
        key = keyGen() 
        plaintext = self.PTextBox.get("1.0",'end-1c')
        if (plaintext== ""):
            messagebox.showwarning("Invalid!","Message Text Box Cannot Be Left Blank!")
            return
        self.PE1.config(state='disabled')
        self.PE2.config(state='disabled')
        self.PTextBox.config(state='disabled')
        shared_key = splitSecret(key,threshold,splits)
        ciphertext = encryptMsg(plaintext,key)
        try:
            txid = writeDatatoBlockchain(ciphertext)
        except:
            messagebox.showerror("Connection Failed!", "Please run the node(Flo-Core)!")
            return
        self.PNextButton.destroy()
        messagebox.showinfo("Encryption Successful!", "Your data is successfully encrypted and stored in the FLO Blockchain!\nSecret ID : "+txid+"\nPlease wait until the pdfs are generated!")
        try:
            generatePDFmain(splits,threshold,shared_key,txid)
            messagebox.showinfo("PDFs Generated!", "The pdfs containing the details of the transaction hash and shared keys required to retrieve the data are generated!\nSecret ID : "+txid)
        except:
            messagebox.showwarning("PDF Error!", "The pdf generation has failed! \nPlease note the details required to retrive the data manually!")
            print('Secret ID : ',txid)
            print('The secret can be decrypted using '+str(threshold)+' of the following '+str(splits)+' shares')
            for i in range(splits):
                print('Shared Key#'+str(i+1)+" : "+shared_key[i])

    def Get(self):
        self.MainFrame.destroy()
        self.GetFrame = Frame(self.root)
        self.GetFrame.pack()
        GL1 = Label(self.GetFrame,text="Enter Number of required shares :  ")
        GL1.grid(row=1,column=1)
        self.GE1 = Spinbox(self.GetFrame, from_ = 2, to = 1000, validate="key", validatecommand=self.vcmd)
        self.GE1.grid(row=1,column=2)
        GL2 = Label(self.GetFrame,text="Enter Secret ID : ")
        GL2.grid(row=2,column=1)
        self.GE2 = Entry(self.GetFrame)
        self.GE2.grid(row=2,column=2)
        txid = self.GE2.get()
        self.GFindButton = Button(self.GetFrame,text="Find Secret",command=self.GetSharedKey)
        self.GFindButton.grid(row=3,column=2)
        self.GBackButton=Button(self.GetFrame,text="Back",command=self.Main)
        self.GBackButton.grid(row=3,column=1)

    def GetSharedKey(self):
        try:
            txid = self.GE2.get()
            self.ciphertext = readDatafromBlockchain(txid)
        except:
            messagebox.showerror("Data retrieval Failed!", "Please enter valid Secret ID \nAlso run the node(Flo-Core)!")
            return
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
        shares = [None] * self.numOfShares
        for i in range(self.numOfShares):
            shares[i] = self.GEArray[i].get()
        try:
            key=recoverSecret(shares) 
            plaintext = decryptMsg(self.ciphertext,key)
        except:
            messagebox.showerror("Decryption Failed!", "Please enter the correct shared keys!")
            return
        for i in range(self.numOfShares):
            shares[i] = self.GEArray[i].config(state='disabled')
        self.GDecryptButton.destroy()
        self.GBackButton.destroy()
        GL3 = Label(self.GetFrame, text="Found Secret Message")
        GL3.grid(column=1, columnspan=2)       
        GTextFrame = Frame(self.GetFrame)
        self.GLMsg = Text(GTextFrame,height=10,width=50)
        self.GLMsg.insert(END, plaintext)
        self.GLMsg.config(state='disabled')
        GScroll = Scrollbar(GTextFrame)
        GScroll.config( command = self.GLMsg.yview )
        self.GLMsg.pack(side = LEFT)
        GScroll.pack(side = RIGHT,fill = Y)
        GTextFrame.grid(column=1,columnspan=2)
        self.CopyButton = Button(self.GetFrame, text="Copy", command=pyperclip.copy(plaintext))
        self.CopyButton.grid(column=1)
        self.GBackButton=Button(self.GetFrame,text="Back",command=self.Main)
        self.GBackButton.grid(column=1)


root = Tk()
root.title("FloSecret")
gui = GUI(root)
gui.Main()
root.mainloop()
    
        
