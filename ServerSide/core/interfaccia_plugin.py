from abc import ABC, abstractmethod

class Interfaccia_Plugin(ABC) :
    @abstractmethod
    def execute():
        pass

    @abstractmethod
    def get_param():
        pass

    @abstractmethod
    def set_param(vet_param):
        pass