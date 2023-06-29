import hashlib

def hash_sha1(data, encode='utf-8'):
    return hashlib.sha1(data.encode(encode)).hexdigest()