# FLOShamir
This app let you save encrypted secret in the FLO blockchain and produces a number of keys that must be combined to be able to decrypt the secret.
A shared secret is a way of splitting a secret into n in keys such that m out of n keys are required to decrypt the message.  Built using Shamir's shared secret algorithm, this app stores the encrypted secret message on blockchain and splits the key into n shares and any of the m share holders can decrypt the message.
Storing secrets on the blockchain makes sure that the file can't be altered and is accessible from anywhere.Also allowing us to use shared secret algorithm for large  messages.

##requirements
1. linux operating system(working on a cross platform version).
2. You need to run a full flo-qt wallet to run it. Download it from here https://github.com/floblockchain/flo
3. Some amount of FLO if you want to post a secret

**WARNING: Currently the app is using the testnet**

##Usage
-> Clone/download this repository. (https://github.com/akhil2015/FLOShamir)
-> Run the binary file inside bin folder.
###To create a shared-secret
-> click on POST to create a new shared secret message 
-> You will get a pdf containing your Secret ID and the shares of the keys used to encrypt it.
-> It is a good practise to destroy the pdf once the shares have been distributed.
###To read a shared secret
-> Click on GET to read the message.
-> Enter the Secret ID and shares of the keys and your are done
-> You should get a screen with the secret message displayed there.


