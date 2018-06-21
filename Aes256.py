#!/usr/bin/env python3
import os
from Crypto.Cipher import AES

#Generating random key of 32 bytes
key=os.urandom(32)
print("Key Generated")
print(key)
#Initialization vector in AES should be 16 bytes
IV = 16*'\x00'
#Mode of encryption CBC
mode = AES.MODE_CBC
#Creation of encryptor and decryptor object using above details 
encryptor=AES.new(key,mode,IV=IV)
decryptor=AES.new(key,mode,IV=IV)

def encrypt(msg):
    n=len(msg)
    #Checking for length of msg to be multiple of 16 as it is required in aes encryption
    if n==0:
        return
    elif n%16!=0:
        msg+=' '*(16-(n%16))        #padding with spaces inorder to make the len of msg to be a multiple of 16 
    cipher=encryptor.encrypt(msg)
    print("Encrypted Text")
    print(cipher)
    print("Checking for decryption")
    text=decryptor.decrypt(cipher);
    #Checking if decrypted text is padded with spaces,so it has been removed by using orignal length of msg
    length=len(text)
    if(length>n):
        plain_text=text[:n]
    else:
        plain_text=text
    print("Decrypted Text")
    print(plain_text)

msg=input('Enter The Message To Be Encrypted\n')
#calling encrypt function
encrypt(msg)
