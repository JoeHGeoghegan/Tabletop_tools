# Imports
import pandas as pd

class Character:
    name : str
    health : int
    initiative : int
    team : str
    
    def __init__(self):
        self.name = ""
        self.health = 0
        self.initiative = 0
        self.team = None
    def __init__(self,name,health,initiative,team):
        self.name = name
        self.health = health
        self.initiative = initiative
        self.team = team

GroupLoop = pd.DataFrame()