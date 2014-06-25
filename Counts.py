class Counts(object):
    def __init__(self, key_padding, number_padding=5):
        self.counts = {}
        self.key_padding = key_padding
        self.number_padding = number_padding


    def add(self, key, incr=1):
        val = self.counts.get(key, None)
        if val is not None:
            self.counts[key] = self.counts[key] + incr
        else:
            self.counts[key] = incr
    

    def get(self, key):
        return self.counts.get(key)


    def combine(self, other):
        for k,v in other.items():
            self.add(k,v)


    def items(self):
        return self.counts.items()


    @property
    def mkString(self):
        items = sorted(self.counts.items(), key=lambda item: -1 * item[1])
        out = ''
        if (len(items) > 0):
            out += "size ".rjust(self.key_padding) + " | count\n".rjust(self.number_padding)
            for item in items:
                out += "%s | %s\n" % (str(item[0]).rjust(self.key_padding),
                                   str(item[1]).rjust(self.number_padding))
        return out + "\n"
