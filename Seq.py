class Seq:

    def __init__(self, strbases):
        self.strbases = strbases

    def getBase (self):
        return self.strbases
    def length(self):              # LENGTH OF THE SEQUENCE
        return len(self.strbases)

    def complement(self):
        comp_seq = ''
        for letter in self.strbases:
            if letter == 'A':
                comp_seq += 'T'
            if letter == 'T':        # CREATES THE COMPLEMENT SEQUENCE
                comp_seq += 'A'
            if letter == 'C':
                comp_seq += 'G'
            if letter == 'G':
                comp_seq += 'C'
        return Seq(comp_seq)

    def reverse(self):
        return Seq(self.strbases[::-1])    # CREATES THE REVERSE SEQUENCE

    def count(self, base):
        counter = 0
        for i in self.strbases:     # COUNTS THE INSTANCES EACH BASE APPEARS IN THE SEQUENCE
            if i == base:
                counter += 1
        return counter

    def perc(self, base):         # CALCULATES THE PERCENTAGES OF EACH BASE IN THE SEQUENCE
        return round(self.count(base)*100/self.length(),1)
