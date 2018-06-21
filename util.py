from secretsharing import PlaintextToHexSecretSharer
import subprocess
import json
from Crypto.Cipher import AES
from more_itertools import sliced

# This function splits the secret and returns a list of shares
def splitSecret(secret,threshold,splits):
	shares = PlaintextToHexSecretSharer.split_secret(secret, threshold, splits)
	return shares

# This function recovers the secret using the list of shares and returns the reconstructed secret
def recoverSecret(shares):
	secret = PlaintextToHexSecretSharer.recover_secret(shares)
	return secret

def writeUnitToBlockchain(text,receiver):
	txid = subprocess.check_output(["flo-cli", "sendtoaddress",receiver,"0.01",'""','""',"true","false","10",'UNSET',str(page_html)])
	txid = str(txid)
	txid = txid[2:-3]
	return txid

def readUnitFromBlockchain(txid):
	rawtx = subprocess.check_output(["flo-cli", "getrawtransaction", str(txid)])
	rawtx = str(rawtx)
	rawtx = rawtx[2:-3]
	tx = subprocess.check_output(["flo-cli",, "decoderawtransaction", str(rawtx)])
	content = json.loads(tx)
	text = content['floData']
	return text

#write data chunk to blockchain
def writeDatatoBlockchain(text):
	n_splits = len(text)//350 + 1				#number of splits to be created
	splits = list(sliced(text, n_splits))		#create a sliced list of strings
	tail = writeUnitToBlockchain(splits[n_splits]) 		#create a transaction which will act as a tail for the data
	cursor = tail
	if n_splits == 1:
		return cursor							#if only single transaction was created then tail is the cursor

	#for each string in the list create a transaction with txid of previous string
	for i in range(n_splits-1,0):
		splits[i] = 'next:'+cursor+splits[i]
		cursor = writeUnitToBlockchain(splits[i])
	return cursor

#TODO read data chunk from blockchain
def readDatafromBlockchain(cursor):
	text = []
	cursor_data = readUnitFromBlockchain(cursor)
	text.append(cursor_data[:])
	while(cursor_data[:5]=='next:'):
		cursor = cursor_data[:]
		cursor_data = readUnitFromBlockchain(cursor)
		text.append(cursor_data[:])
	text.join('')
	return text