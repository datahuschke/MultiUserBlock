import hmac
import os

#read the salt from a file which contains a very long random string
file = os.path.join(os.path.dirname(__file__), 'secret.txt')
SECRET = open(file).read().replace('\n', '')


def hash_str(s):
    #return hashlib.md5(s).hexdigest()
    return hmac.new(SECRET, s).hexdigest()


def valid_user_password(pw, pw_hash):
    return hash_str(pw) == pw_hash


def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))


def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val
