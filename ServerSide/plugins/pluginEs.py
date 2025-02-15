from core.interfaccia_plugin import Interfaccia_Plugin
class Plugin(Interfaccia_Plugin):
    def __init__(self):
        self.params = []
        self.keys = []

    def execute(self):
        return "Io sono Nessunooo"

    def get_param(self):
        return self.keys

    def set_param(self, vet_param):
        self.params = vet_param
        return True
