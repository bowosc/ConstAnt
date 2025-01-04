from gmpy2 import *
import math
from sympy import sympify, pi, evalf, Expr, E, I
from rpn import rpn

# long comment long comment long comment long comment long comment long comment 
# long comment long comment long comment long comment long comment long comment 
# long comment long comment long comment long comment long comment long comment 
# long comment long comment long comment long comment long comment long comment 
# long comment long comment long comment long comment long comment long comment 
bob = "I"
print(Expr.evalf(sympify(bob)))





import bcrypt 
  
# example password 
password = 'password000'
  
# converting password to array of bytes 
bytes = password.encode('utf-8') 
  
# generating the salt 
salt = bcrypt.gensalt() 
  
# Hashing the password 
hash = bcrypt.hashpw(bytes, salt) 
  
# Taking user entered password  
userPassword =  'password000'
  
# encoding user password 
userBytes = userPassword.encode('utf-8') 
  
# checking password 
result = bcrypt.checkpw(userBytes, hash) 
  
print(result)