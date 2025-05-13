from core.interfaccia_plugin import Interfaccia_Plugin 

class Plugin(Interfaccia_Plugin):
    def __init__(self):
        self.params = []
        self.keys = ["primoNumero", "secondoNumero"]

    def execute(self):
        return self.params[0] + self.params[1]

    def get_param(self):
        return self.keys

    def set_param(self, vet_param):
        try:
            self.params.append(float(vet_param["primoNumero"]))
            self.params.append(float(vet_param["secondoNumero"]))
        except (ValueError, KeyError):
            return False
        return True