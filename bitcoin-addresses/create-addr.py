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
import os

prefix_pubkey = b'\x6f'
prefix_script = b'\xc4'
prefix_private = b'\xef'

if len(sys.argv) != 2:
    print("Usage: %s <private key in hex format>" % sys.argv[0])
    sys.exit(1)

use_compression = True

if os.getenv('COMPRESS'):
    use_compression = True

"""
Using ecdsa primitives, retrieve public key from private key.
"""
def get_public_key(privkey, use_compression = False):
    sk = ecdsa.SigningKey.from_string(privkey, curve=ecdsa.SECP256k1)
    vk = sk.verifying_key

    if use_compression:
        p = vk.pubkey.point
        order = sk.curve.generator.order()

        x_str = ecdsa.util.number_to_string(p.x(), order)
        prefix = bytes(chr((p.y() & 0x01) + 2), 'ascii')

        return (prefix + x_str)

    # Uncompressed
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

from_wif = None
try:
    from_wif = base58.b58decode(privkeyhex)
except Exception:
    pass

if from_wif != None:
    privkey = from_wif[1:33]
else:
    privkey = binascii.unhexlify(privkeyhex)

pubkey = get_public_key(privkey, use_compression)

print("Private key (hex): %s" % privkey.hex())
print("Public key: %s" % pubkey.hex())

# Perform sha256 on publickey
addr_sha256 = sha256(pubkey)

# Then, ripemd160 on result
addr_ripemd160 = ripemd160(addr_sha256)

# And add network byte as a prefix (0x00 on bitcoin's mainnet)
extended_ripemd160 = prefix_pubkey + addr_ripemd160

# Let's compute hash check on this string, using sha256 twice:
check = sha256(extended_ripemd160)
check = sha256(check)

# Add the first 4 bytes of check at the end of address (extended_ripe160):
addr_raw = extended_ripemd160 + check[:4]

# Perform base58 encode to get final address:
addr = base58.b58encode(addr_raw)

print("Public address: %s" % addr)
print("Public address (compressed): %s" % get_public_key(privkey, True).hex())

extprivkey = prefix_private + privkey

if use_compression:
    extprivkey += b'\x01'

check_privkey = sha256(extprivkey)
check_privkey = sha256(check_privkey)

extprivkey = extprivkey + check_privkey[:4]

print("Private key: %s" % extprivkey.hex())

privaddr = base58.b58encode(extprivkey)

print("Private WIF address: %s" % privaddr)

# Create script address from this pubkey
# \x51 is OP_TRUE
# \xae is OP_MULTICHECKSIG
public_key = get_public_key(privkey, True)
script = b'\x51' + bytes(chr(len(public_key)), 'ascii') + public_key + b'\x51' + b'\xae'

addr_sha256 = sha256(script)
addr_ripemd160_p2sh = ripemd160(addr_sha256)

extended_ripemd160 = prefix_script + addr_ripemd160_p2sh

check = sha256(extended_ripemd160)
check = sha256(check)

addr = extended_ripemd160 + check[:4]
addr = base58.b58encode(addr)

print("Redeem script: %s" % script.hex())
print("Public script address: %s" % addr)

sys.path.append(os.path.abspath("."))
import segwit_addr

# tb for testnet, bc for mainnet
bc32 = segwit_addr.encode("tb", 0, addr_ripemd160)
print("bech32 (p2wpkh): %s" % bc32)

bc32 = segwit_addr.encode("tb", 0, addr_sha256)
print("bech32 (p2wsh): %s" % bc32)

