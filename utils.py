
class Data:
    def __init__(self, data):
        self.__dict__.update(data)

    def __repr__(self):
        return str(self.__dict__)

def padWithZero(s, length):
    result = s    
    while len(result) < length:
        result = "0%s" % result
    return result
