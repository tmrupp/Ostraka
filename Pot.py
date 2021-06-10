from pyipv8.ipv8.messaging.serialization import Serializable, VarLen

from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import typing

import time

class Pot ():
    def export_key (self):
        return self.key.export_key(format='PEM')

    def import_key (self, imported_key):
        self.key = ECC.import_key(imported_key)
        self.signer = DSS.new(self.key,'fips-186-3')
        
    def __init__ (self, imported_key=None):
        if imported_key is None:
            self.key = ECC.generate(curve='p256')
            self.signer = DSS.new(self.key,'fips-186-3')
        else:
            self.import_key(imported_key)

    def __str__(self) -> str:
        return str(self.key)

    def sign (self, msg) -> bytes:
        h = SHA256.new(str(msg).encode('utf8'))
        return self.signer.sign(h)

    def signedMsg (self, msg):
        return (msg, self.sign(str(msg).encode('utf8')))

    def get_public_key (self):
        return self.key.public_key().export_key(format='DER') # DER is smaller than PEM

    def import_public_key (exported_key):
        return ECC.import_key(exported_key)

    def verify_signature (pub: ECC.EccKey, msg, signature):
        h = SHA256.new(msg)
        verifier = DSS.new(pub, 'fips-186-3')
        try:
            verifier.verify(h, signature)
            return True
        except ValueError:
            return False

    def testTx (self, text):
        tx = Transaction()
        tx.compose('c', self, text)
        return tx

    def sendTx (self, receiever : str, amount : float):
        msg = ("send", self.get_public_key(), time.gmtime(), receiever, amount)
        # print(msg)
        return self.signedMsg(msg)

    def grantTx (self, newVoters : list):
        msg = ("grant", self.get_public_key(), time.gmtime(), newVoters)
        return self.signedMsg(msg)

    # Y:yes N:no A:abstain
    def respondTx (self, index : int, response : str):
        msg = ("respond", self.get_public_key(), time.gmtime(), response, index)
        return self.signedMsg(msg)

    def modifyTx (self, code : str):
        msg = ("modify", self.get_public_key(), time.gmtime(), code)
        return self.signedMsg(msg)

    #revoke op, remove voters

class Transaction (Serializable):
    format_list = ['B', 'varlenI', 'varlenI', 'varlenI', 'varlenI']

    def __init__ (self, op='', sender='', time='', text='', signature=''):
        self.op = op  # char?
        self.sender = sender
        self.time = time
        self.text = text # long string
        self.signature = signature

    def compose (self, op, sender: Pot, text):
        self.op = op  # char?
        self.sender = sender.get_public_key() # string of 91 size
        self.time = time.gmtime() # string of 121 size
        self.text = text # long string
        self.msg = (self.op, self.sender, self.time, self.text)
        self.signature = sender.sign(self.msg) # string of 64 size

    def to_pack_list (self) -> typing.List[tuple]:
        return [
            ('B', self.op),
            ('varlenI', self.sender),
            ('varlenI', self.time),
            ('varlenI', self.text),
            ('varlenI', self.signature),
        ]

    def __str__ (self):
        s = ''
        s = s + "op:" + str(self.op) + ' '
        s = s + "sender:" + str(self.sender) + " "
        s = s + "time:" + str(self.time) + " "
        s = s + "text:" + str(self.text) + " "
        s = s + "signature:" + str(self.signature) 

        return s


    @classmethod
    def from_unpack_list(cls, *args) -> Serializable:  # pylint: disable=E0213
        return cls(*args)

def test ():
    myPot = Pot()
    yourPot = Pot()
    print(myPot)

    message = b'hey how\'s it going'

    mySignature = myPot.sign(message)
    print(len(mySignature))

    # verified = Pot.verify_signature(myPot.get_public_key(), message, mySignature)
    # print(verified)

    # Tx = myPot.sendTx(yourPot.get_public_key(), 34.65)
    # TxBytes = dumps(Tx)
    # print (TxBytes)

    print (len(myPot.get_public_key()))
    print (len(myPot.key.public_key().export_key(format='DER')))
    print (len(str(time.gmtime())))


    myTx = myPot.testTx("hey how are u?")
    print(myTx)
    my_packed_tx = myTx.to_pack_list()
    print(my_packed_tx)
    newTx = Transaction.from_unpack_list(my_packed_tx)
    print(newTx)

    # t0 = Transaction("tombsdf")
    # t1 = Transaction.from_unpack_list(t0.to_pack_list())

    # print (t1)
    # print (t0)




test()