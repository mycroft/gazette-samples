#!/usr/bin/env python

# To use:
# virtualenv-3 env
# source env/bin/activate
# pip install base58 ecdsa
# ./encode-priv.py 4e7b7fb13697e6940c08d0bd9adefdea127047797bcdea85bb25d8bdd101aa33


import base58
import binascii
import ecdsa
import hashlib
import sys

if len(sys.argv) != 2:
    print("Usage: %s <private key in hex format>" % sys.argv[0])
    sys.exit(1)

"""
Using ecdsa primitives, retrieve public key from private key.
"""
def get_public_key(privkey):
    sk = ecdsa.SigningKey.from_string(privkey, curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    return (b'\04' + sk.verifying_key.to_string())

def sha256(content):
    m = hashlib.new('sha256')
    m.update(content)
    return m.digest()

def ripemd160(content):
    m = hashlib.new('ripemd160')
    m.update(content)
    return m.digest()

privkeyhex = sys.argv[1]
privkey = binascii.unhexlify(privkeyhex)
pubkey = get_public_key(privkey)

# Perform sha256 on publickey
addr_sha256 = sha256(pubkey)

# Then, ripemd160 on result
addr_ripemd160 = ripemd160(addr_sha256)

# And add network byte as a prefix (0x00 on bitcoin's mainnet)
extended_ripemd160 = b'\x00' + addr_ripemd160

# Let's compute hash check on this string, using sha256 twice:
check = sha256(extended_ripemd160)
check = sha256(check)

# Add the first 4 bytes of check at the end of address (extended_ripe160):
addr = extended_ripemd160 + check[:4]

# Perform base58 encode to get final address:
addr = base58.b58encode(addr)

print("Public address: %s" % addr)

extprivkey = b'\x80' + privkey

check_privkey = sha256(extprivkey)
check_privkey = sha256(check_privkey)

extprivkey = extprivkey + check_privkey[:4]

privaddr = base58.b58encode(extprivkey)

print("Private WIF address: %s" % privaddr)

