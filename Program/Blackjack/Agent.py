"""
    - Abstract class implementing and initialise needed properties and methods
    - every agent should inheret from this and overrdide the behaviours implemented in this class
"""
from abc import ABC, abstractmethod

class Agent(ABC):
    def __init__(self, ID="", type=None):
        self.ID = ID
        self.type = type
        super().__init__()

    @abstractmethod
    def update_end_game(self):
        pass

    @abstractmethod
    def get_move(self):
        pass

    def set_parameters(self, setting="default"):
        pass
