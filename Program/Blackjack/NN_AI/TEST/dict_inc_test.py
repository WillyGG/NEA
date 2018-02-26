from test2 import increment_dictionary

dictionary = {
    "a": 1,
    "b": 1000
}

for x in range(3):
    increment_dictionary(dictionary)
print(dictionary["a"])