from secretsharing import PlaintextToHexSecretSharer
import subprocess
import json
from Crypto.Cipher import AES

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

#TODO write data chunk to blockchain
#TODO read data chunk from blockchain
def writeDatatoBlockchain(text):
	splits = len(text)//350 + 1
	#TODO create a sliced list of strings
	#TODO for each string in the list create a transaction with txid of previous string
