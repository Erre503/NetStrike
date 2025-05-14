import os
import importlib
import sys
import abc
import inspect
import subprocess
from pathlib import Path
from datetime import datetime
import platform
import json
"""
FOLDER : path ricavato che punta alla cartella con gli script 

TIMEOUT : massimo tempo di esecuzione dentro ad un container prima che venga terminato
"""
FOLDER = Path(__file__).resolve().parent.parent / "plugins"
TIMEOUT = 60  # seconds


def get_plugin_extension(nome_file):
    if nome_file.endswith('.sh'):
        return '.sh'
    if nome_file.endswith('.py'):
        return '.py'
    return None


def lista_plugin():
    return [f for f in os.listdir(FOLDER) if f.endswith(('.py', '.sh'))]


def rinomina_plugin(nomeVecchio, nomeNuovo):
    try:
        (FOLDER / nomeVecchio).rename(FOLDER / nomeNuovo)
        return True
    except Exception:
        return False


def elimina_plugin(nome):
    try:
        os.remove(FOLDER / nome)
        return True
    except Exception:
        return False


def interfacciaBash(content):
    return all(cmd in content for cmd in ['set_param', 'get_param', 'execute'])


def creaPluginPy(nome_file, contenuto):
    if not nome_file.endswith('.py'):
        nome_file += '.py'
    file = FOLDER / nome_file
    if os.path.isfile(file):
        return f"Error: File {nome_file} already exists"

    full_content = f"from core.interfaccia_plugin import Interfaccia_Plugin\n\n{contenuto}"
    try:
        file.write_text(full_content, encoding="utf-8")
        spec = importlib.util.spec_from_file_location(nome_file[:-3], file)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)

        if not hasattr(modulo, "Plugin") or not inspect.isclass(modulo.Plugin):
            os.remove(file)
            raise TypeError("Missing or invalid 'Plugin' class")

        from core.interfaccia_plugin import Interfaccia_Plugin
        if not issubclass(modulo.Plugin, Interfaccia_Plugin):
            os.remove(file)
            raise TypeError("Must inherit from Interfaccia_Plugin")

        if len(modulo.Plugin.__abstractmethods__) > 0:
            os.remove(file)
            raise NotImplementedError(f"Unimplemented abstract methods: {modulo.Plugin.__abstractmethods__}")

        return f"Plugin created successfully: {nome_file}"

    except Exception as e:
        return f"Validation failed: {e}"


def creaPluginSh(nome_file, contenuto):
    if not nome_file.endswith('.sh'):
        nome_file += '.sh'
    if nome_file in os.listdir(FOLDER):
        return False
    if interfacciaBash(contenuto):
        with open(FOLDER / nome_file, "w", encoding="utf-8") as file:
            file.write(contenuto)
        return True
    return False


def creaPlugin(nome_file, contenuto):
    if nome_file.endswith('.sh'):
        return creaPluginSh(nome_file, contenuto)
    if nome_file.endswith('.py'):
        return creaPluginPy(nome_file, contenuto)
    print("Tipo di file non supportato")
    return None

"""
Viene fatto un check per il tipo di file e viene eseguito un comando
per docker di conseguenza, al momento ho gestito solo .py e .sh

"""
def avvia_plugin(nome_plugin, vet_param, type):
    res = {'datetime': datetime.now()}
    percorso_plugin = FOLDER / nome_plugin

    if not percorso_plugin.exists():
        res['status'] = 'failed'
        res['log'] = f"File non trovato: {nome_plugin}"
        return res

    try:
        if type == 'py':
            comando = [
                'docker', 'run', '--rm',
                '-v', f"{FOLDER}:/plugins",
                '-e', f"PARAMS={json.dumps(vet_param)}",
                'python:3.11',
                'python', f'/plugins/{nome_plugin}'
            ]
        elif type == 'sh':
            comando = [
                'docker', 'run', '--rm',
                '-v', f"{FOLDER}:/plugins",
            ]
            for k, v in vet_param.items():
                comando.extend(['-e', f"{k}={v}"])
            comando += ['bash:5.2', f"/plugins/{nome_plugin}"]
        else:
            res['status'] = 'failed'
            res['log'] = 'Tipo di plugin non supportato'
            return res

        output = subprocess.run(comando, capture_output=True, text=True, timeout=TIMEOUT)
        res['log'] = output.stdout.strip() or output.stderr.strip()
        res['status'] = 'finished' if output.returncode == 0 else 'failed'
    except subprocess.TimeoutExpired:
        res['status'] = 'failed'
        res['log'] = 'Timeout durante l''esecuzione del container'
    except Exception as e:
        res['status'] = 'failed'
        res['log'] = f"Errore generico: {e}"

    return res
