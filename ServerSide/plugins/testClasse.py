from interfaccia_plugin import Interfaccia_Plugin

class Plugin(Interfaccia_Plugin):
    ip = ""
    metodo = ""

    @classmethod
    def execute(cls):
        print(cls.ip)
        print(cls.metodo)

    @classmethod
    def get_param(cls):
        vet_param = [{'key': 'ip', 'description': 'Questo parametro serve per indicare l indirizzo ip tramite stringa. es: -197.168.0.1-'}, 
                     {'key': 'metodo', 'description': 'Questo parametro serve per specificare il tipo di attacco che vuoi eseguire puoi scegliere tra -forte-, -debole-, -massimo-'}]
        return vet_param
    
    @classmethod
    def set_param(cls, vet_param):
        cls.ip = vet_param['ip']
        cls.metodo = vet_param['metodo']
        return True