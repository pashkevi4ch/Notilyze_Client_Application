class Verification():
    def __init__(self):
        self.id = None
        self.verificated = False

    def Verificate(self, id):
        self.id = id
        self.verificated = True

    def SignOut(self):
        self.id = None
        self.verificated = False


class Admin():
    def __init__(self):
        self.verificated=False

    def SignOut(self):
        self.verificated=False