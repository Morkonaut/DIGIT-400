from passlib.hash import sha256_crypt

pass1 = "password1"

pass2 = "password2"

salt = "password3"

saltpass1 = pass1 + salt
saltpass2 = pass2 + salt

new_pass1 = sha256_crypt.encrypt("saltpass1")

new_pass2 = sha256_crypt.encrypt("saltpass2")

print(new_pass1)
print(new_pass2)

print(sha256_crypt.verify("password2"+salt, new_pass1))


"""

import hashlib

user_password = "cookies"

salt = "chocolate"

new_password = user_password + salt

hashpass = hashlib.md5(new_password.encode())

print(hashpass.hexdigest())

"""