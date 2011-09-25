class SDict(dict):
    """
    Copy from web.utils.Stroage
    Usage:
        >>> o = Storage(a=1)
        >>> o.a
        1
        >>> o['a']
        1
    """
    def __init__(self, dic=None):
        if dic:
            for k in dic.keys():
                self.__setattr__(k, dic[k])
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError, k:
            #raise AttributeError, k
            return None
    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError, k

    def __repr__(self):
        return '<Storage> ' + dict.__repr__(self)

    def stdout(self):
        dic = {}
        for k in self.keys():
            dic[k] = self[k]
        return dic
