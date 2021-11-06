class Household:
    def __init__(self, id, members):
        self.id = id
        self.members = members

    def __repr__(self):
        return  "Household(id:" + str(self.id) + ", members: " + str(self.members) + ")"