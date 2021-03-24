import rsa
import hashlib
import time

# names: entente, consensum, ostraka, conchord

def hashThenSignMessage (msg, privateKey):
    h = rsa.compute_hash(msg, 'SHA-256')
    return rsa.sign_hash(h, privateKey, 'SHA-256')

def verifySignature (msg, signature, publicKey):
    return rsa.verify(msg, signature, publicKey)

class publicWallet:
    def __init__ (self, publicKey):
        self.pubkey = publicKey
        self.value = 0

class wallet:
    def __init__ (self):
        (pub, self.privkey) = rsa.newkeys(512)
        self.pwallet = publicWallet(pub)

    def sendTx (self, receiever, amount):
        msg = ("send", self.pwallet.pubkey, time.gmtime(), receiever, amount)
        # print(msg)
        return (msg, hashThenSignMessage(str(msg).encode('utf8'), self.privkey))

    def makeBlock (self, msg):
        return Block(msg)

    def verifyTx (self, transaction):
        (msg, signature) = transaction
        op, pub, *rest = msg
        try:
            verifySignature(str(msg).encode('utf8'), signature, pub)
        except:
            return False
        return True

    def getPublicKey (self):
        return self.pwallet.pubkey

class Block:
    def __init__ (self, msg=""):
        self.prevHash = bytes()
        self.msg = msg # signature in msg
        self.index = 0

    def getHash (self):
        info = (self.prevHash, str(self.msg).encode('utf8'), self.index)
        return rsa.compute_hash(str(info).encode('utf8'), 'SHA-256')

    def __str__ (self):
        return str((self.index, self.msg, self.prevHash))

class BlockChain:
    def __init__ (self):
        self.chain = [Block()]

    def __len__ (self):
        return len(self.chain)
    
    def addBlock (self, newBlock):
        newBlock.prevHash = self.chain[len(self)-1].getHash()
        newBlock.index = len(self)
        self.chain.append(newBlock)

    def __str__ (self):
        s = ""
        for block in self.chain:
            s += str(block) + "\n"
        return s

wallets = [wallet(), wallet(), wallet()]
myWallet = wallet()
bc = BlockChain()

bc.addBlock(myWallet.makeBlock(myWallet.sendTx(wallets[0].getPublicKey(), 10)))
bc.addBlock(myWallet.makeBlock(myWallet.sendTx(wallets[1].getPublicKey(), 100)))
bc.addBlock(myWallet.makeBlock(myWallet.sendTx(wallets[0].getPublicKey(), 50)))
print("bc=", bc)
