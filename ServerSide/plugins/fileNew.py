from core.interfaccia_plugin import Interfaccia_Plugin 

class Plugin(Interfaccia_Plugin):
    def __init__(self):
        self.primoNumero = None
        self.secondoNumero = None
        self.params = ["primoNumero", "secondoNumero"]

    def execute(self):
        return self.primoNumero + self.secondoNumero

    def get_param(self):
        return self.params

    def set_param(self, vet_param):
        try:
            self.primoNumero = float(vet_param["primoNumero"])
            self.secondoNumero = float(vet_param["secondoNumero"])
        except (ValueError, KeyError):
            return False
        return True