import time
#import datetime
import string
from random import choice
from hashlib import md5

CHARS = string.letters + string.digits

def RandomHash(id):
    CHARS = string.digits
    LIMIT = 8
    id_str = str(id)
    prefix = ''.join([choice(CHARS) for i in range(LIMIT-len(id_str))])
    return prefix + id_str

def create_password(raw):
    PREFIX = 'NODEMIX_USER_PASSWORD'
    return md5(PREFIX+raw).hexdigest()

def check_password(raw, indb):
    return create_password(raw) == indb

def Md5(s):
    if not isinstance(s, str):
        s = s.encode('utf-8')
    return md5(s).hexdigest()

def GenerateAbsoluteID(name1, name2):
    s = '%s+%s+%s+%s' % (str(time.time()), name1, name2,
        ''.join([choice(CHARS) for i in range(4)]))
    return md5(s).hexdigest()

def CreateNid(id):
    limit = 9 # 100 million
    length = 8 # if id shorter than this
    id_len = len(str(id))
    if not id_len > length:
        nid = choice('123456789') + ''.join([choice(string.digits) for i in range(length-1-id_len)]) + str(id)
    else:
        nid = id
    return nid

def RandomString(length=10):
    return ''.join([choice(CHARS) for i in range(length)])

def SaltMd5(s):
    return Md5(s + RandomString(5))
