"""
Taken from 
https://github.com/bitcoin-abe/bitcoin-abe
"""
class EnumException(Exception):
    pass


class Enumeration:
    def __init__(self, name, enumList):
        self.__doc__ = name
        lookup = {}
        reverseLookup = {}
        i = 0
        uniqueNames = []
        uniqueValues = []
        for x in enumList:
            if type(x) == tuple:
                x, i = x
            if type(x) != str:
                raise EnumException("enum name is not a string: " + x)
            if type(i) != int:
                raise EnumException("enum value is not an integer: " + i)
            if x in uniqueNames:
                raise EnumException("enum name is not unique: " + x)
            if i in uniqueValues:
                raise EnumException("enum value is not unique for " + x)
            uniqueNames.append(x)
            uniqueValues.append(i)
            lookup[x] = i
            reverseLookup[i] = x
            i = i + 1
        self.lookup = lookup
        self.reverseLookup = reverseLookup
    def __getattr__(self, attr):
        return self.lookup[attr]
    def whatis(self, value):
        return self.reverseLookup[value]