# Distribute and use freely; there are no restrictions on further
# dissemination and usage except those imposed by the laws of your
# country of residence.  This software is provided "as is" without
# warranty of fitness for use or suitability for any purpose, express
# or implied. Use at your own risk or not at all.

"""Verify a DSA signature, for use with PyPI mirrors.

Verification should use the following steps:
1. Download the DSA key from http://pypi.python.org/serverkey, as key_string
2. key = load_key(key_string)
3. Download the package page, from <mirror>/simple/<package>/, as data
4. Download the package signature, from <mirror>/serversig/<package>, as sig
5. Check verify(key, data, sig)
"""


# DSA signature algorithm, taken from pycrypto 2.0.1
# The license terms are the same as the ones for this module.
def _inverse(u, v):
    """_inverse(u:long, u:long):long
    Return the inverse of u mod v.
    """
    u3, v3 = long(u), long(v)
    u1, v1 = 1L, 0L
    while v3 > 0:
        q = u3 / v3
        u1, v1 = v1, u1 - v1 * q
        u3, v3 = v3, u3 - v3 * q
    while u1 < 0:
        u1 = u1 + v
    return u1


def _verify(key, M, sig):
    p, q, g, y = key
    r, s = sig
    if r <= 0 or r >= q or s <= 0 or s >= q:
        return False
    w = _inverse(s, q)
    u1, u2 = (M * w) % q, (r * w) % q
    v1 = pow(g, u1, p)
    v2 = pow(y, u2, p)
    v = ((v1 * v2) % p)
    v = v % q
    return v == r

# END OF pycrypto


def _bytes2int(b):
    value = 0
    for c in b:
        value = value * 256 + ord(c)
    return value

_SEQUENCE = 0x30  # cons
_INTEGER = 2      # prim
_BITSTRING = 3    # prim
_OID = 6          # prim


def _asn1parse(string):
    #import pdb; pdb.set_trace()
    tag = ord(string[0])
    assert tag & 31 != 31  # only support one-byte tags
    length = ord(string[1])
    assert length != 128  # indefinite length not supported
    pos = 2
    if length > 128:
        # multi-byte length
        val = 0
        length -= 128
        val = _bytes2int(string[pos:pos + length])
        pos += length
        length = val
    data = string[pos:pos + length]
    rest = string[pos + length:]
    assert pos + length <= len(string)
    if tag == _SEQUENCE:
        result = []
        while data:
            value, data = _asn1parse(data)
            result.append(value)
    elif tag == _INTEGER:
        assert ord(data[0]) < 128  # negative numbers not supported
        result = 0
        for c in data:
            result = result * 256 + ord(c)
    elif tag == _BITSTRING:
        result = data
    elif tag == _OID:
        result = data
    else:
        raise ValueError("Unsupported tag %x" % tag)
    return (tag, result), rest


def load_key(string):
    """load_key(string) -> key

    Convert a PEM format public DSA key into
    an internal representation."""
    import base64
    lines = [line.strip() for line in string.splitlines()]
    assert lines[0] == "-----BEGIN PUBLIC KEY-----"
    assert lines[-1] == "-----END PUBLIC KEY-----"
    data = base64.decodestring(''.join(lines[1:-1]))
    spki, rest = _asn1parse(data)
    assert not rest
    # SubjectPublicKeyInfo  ::=  SEQUENCE  {
    #  algorithm            AlgorithmIdentifier,
    #  subjectPublicKey     BIT STRING  }
    assert spki[0] == _SEQUENCE
    algoid, key = spki[1]
    assert key[0] == _BITSTRING
    key = key[1]
    # AlgorithmIdentifier  ::=  SEQUENCE  {
    #  algorithm               OBJECT IDENTIFIER,
    #  parameters              ANY DEFINED BY algorithm OPTIONAL  }
    assert algoid[0] == _SEQUENCE
    algorithm, parameters = algoid[1]
    assert algorithm[0] == _OID and algorithm[1] == '*\x86H\xce8\x04\x01'  # dsaEncryption
    # Dss-Parms  ::=  SEQUENCE  {
    #  p             INTEGER,
    #  q             INTEGER,
    #  g             INTEGER  }
    assert parameters[0] == _SEQUENCE
    p, q, g = parameters[1]
    assert p[0] == q[0] == g[0] == _INTEGER
    p, q, g = p[1], q[1], g[1]
    # Parse bit string value as integer
    assert key[0] == '\0'  # number of bits multiple of 8
    y, rest = _asn1parse(key[1:])
    assert not rest
    assert y[0] == _INTEGER
    y = y[1]
    return p, q, g, y


def verify(key, data, sig):
    """verify(key, data, sig) -> bool

    Verify autenticity of the signature created by key for
    data. data is the bytes that got signed; signature is the
    bytes that represent the signature, using the sha1+DSA
    algorithm. key is an internal representation of the DSA key
    as returned from load_key."""
    import sha
    data = sha.new(data).digest()
    data = _bytes2int(data)
    # Dss-Sig-Value  ::=  SEQUENCE  {
    #      r       INTEGER,
    #      s       INTEGER  }
    sig, rest = _asn1parse(sig)
    assert not rest
    assert sig[0] == _SEQUENCE
    r, s = sig[1]
    assert r[0] == s[0] == _INTEGER
    sig = r[1], s[1]
    return _verify(key, data, sig)
