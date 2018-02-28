from test2 import increment_dictionary
from enum import Enum

class E(Enum):
    J = 10
    Q = 11
a = E.J
print(a == E.J)

dictionary = {
    "a": 1,
    "b": 1000
}

for x in range(3):
    increment_dictionary(dictionary)
print(dictionary["a"])