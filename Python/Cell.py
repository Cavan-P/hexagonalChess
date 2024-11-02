class Cell:
    def __init__(self, num, q, r, s):
        self.num = num
        self.q = q
        self.r = r
        self.s = s
        self.occupied_by = None

    def is_occupied(self):
        return self.occupied_by is not None