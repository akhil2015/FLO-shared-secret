#!/usr/bin/env python3
from secretsharing import PlaintextToHexSecretSharer
import base64
import os
from Crypto.Cipher import AES

# This function splits the secret and returns a list of shares
def splitSecret(secret,threshold,splits):
	shares = PlaintextToHexSecretSharer.split_secret(secret, threshold, splits)
	return shares

# This function recovers the secret using the list of shares and returns the reconstructed secret
def recoverSecret(shares):
	secret = PlaintextToHexSecretSharer.recover_secret(shares)
	return secret


def pad(data):
    padding = 16 - len(data) % 16
    return data + padding * ' '


def unpad(data):
    return data[:length]


def keyGen():
    # Generating random key of 32 bytes
    key = os.urandom(32)
    # print("Key Generated")
    # print(key)
    return key


def encryptMsg(plaintext, key):
    # Initialization vector in AES should be 16 bytes
    IV = 16 * '\x00'
    # Creation of encryptor and decryptor object using above details
    cipher = AES.new(key, AES.MODE_CBC, IV)
    return cipher.encrypt(pad(plaintext))


def decryptMsg(ciphertext, key):
    # Initialization vector in AES should be 16 bytes
    IV = 16 * '\x00'
    # Creation of encryptor and decryptor object using above details
    cipher = AES.new(key, AES.MODE_CBC, IV)
    return unpad(cipher.decrypt(ciphertext));


msg = input('Enter The Message To Be Encrypted : ')
length = len(msg)
key = keyGen()
print("Key generated : " + str(key))

#Enter Threshold And No of splits for key
threshold=0
splits=0
while(True):
    splits=input('Enter Max No of splits\n')
    splits=int(splits)
    threshold=input('Enter Threshold Value\n')
    threshold=int(threshold)
    if(splits>=threshold and threshold>=2):
        break
    else:
        print("Please Choose Correct Pair Of values bcoz threshold<=split and threshold>=2")

#Formatting key inorder to convert bytes of string using base64
key_formatted=base64.b64encode(key).decode('utf-8')
print("Formatted Key="+key_formatted)
#Generating shares of formatted key
shared_key=splitSecret(key_formatted,threshold,splits)
print("Shared Keys="+str(shared_key))

#Recovering Keys using first threshold
recovered_key=recoverSecret(shared_key[:threshold])
#Converting recovered_key to bytes using base64 module
recovered_key=base64.b64decode(recovered_key)
print("Recovered Key="+str(recovered_key))
print(type(recovered_key))

#issue why recovered key!=key?
if(recovered_key==key):
    print("True")

#Encryption using key generated
ciphertext = encryptMsg(msg,key)
print("Encrypted Text : " + str(ciphertext))

#Decryption using recovered key gives error(issue)
plaintext = decryptMsg(ciphertext,recovered_key)
print("Decrypted Text : " + str(plaintext))
