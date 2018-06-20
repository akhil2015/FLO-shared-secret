#!/usr/bin/env python3
import os
from Crypto.Cipher import AES


key=os.urandom(32)
print("Key Generated")
print(key)
IV = 16*'\x00'
mode = AES.MODE_CBC
encryptor=AES.new(key,mode,IV=IV)
decryptor=AES.new(key,mode,IV=IV)

def encrypt(msg):
    n=len(msg)
    if n==0:
        return
    elif n%16!=0:
        msg+=' '*(16-(n%16))
    cipher=encryptor.encrypt(msg)
    print("Encrypted Text")
    print(cipher)
    print("Checking for decryption")
    text=decryptor.decrypt(cipher);
    length=len(text)
    if(length>n):
        plain_text=text[:n]
    else:
        plain_text=text
    print("Decrypted Text")
    print(plain_text)

msg=input('Enter The Message To Be Encrypted\n')
encrypt(msg)