#!/usr/bin/env python3
import os
from Crypto.Cipher import AES

def pad(data):
    padding = 16 - len(data) % 16
    return data + padding * ' '

def unpad(data):
    return data[:length]

def keyGen():
    #Generating random key of 32 bytes
    key=os.urandom(32)
    #print("Key Generated")
    #print(key)
    return key


def encryptMsg(plaintext,key):
    #Initialization vector in AES should be 16 bytes
    IV = 16*'\x00'
    #Creation of encryptor and decryptor object using above details 
    cipher=AES.new(key,AES.MODE_CBC,IV)
    return cipher.encrypt(pad(plaintext))

def decryptMsg(ciphertext, key):
    #Initialization vector in AES should be 16 bytes
    IV = 16*'\x00'
    #Creation of encryptor and decryptor object using above details 
    cipher=AES.new(key,AES.MODE_CBC,IV)
    return unpad(cipher.decrypt(ciphertext));
    

msg=input('Enter The Message To Be Encrypted : ')
length=len(msg)
key = keyGen()
print("Key generated : "+str(key))
ciphertext = encryptMsg(msg,key)
print("Encrypted Text : "+str(ciphertext))
plaintext = decryptMsg(ciphertext, key)
print("Decrypted Text : "+str(plaintext))
