from gmpy2 import *
import math
from sympy import sin, pi, evalf, Expr
from rpn import rpn
print(gmpy2.add(2, 8))

print(rpn.calculateInfix("sin(pi)^(1/4)"))
print(rpn.calculateInfix("sin(pi)"))
print(math.sin(math.pi))
print(gmpy2.sin(gmpy2.const_pi()))
# long comment long comment long comment long comment long comment long comment 
# long comment long comment long comment long comment long comment long comment 
# long comment long comment long comment long comment long comment long comment 
# long comment long comment long comment long comment long comment long comment 
# long comment long comment long comment long comment long comment long comment 
bob = sin(pi/4)
print(Expr.evalf(bob))

print(rpn.calculateInfix("sin(pi/4)"))
print(rpn.calculateInfix("sqrt(2)/2"))