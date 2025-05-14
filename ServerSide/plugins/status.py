from core.interfaccia_plugin import Interfaccia_Plugin

import os #libreria per poter lavorare con le cartelle e file dell'applicazione
import importlib #va a sostituire la funzione manuale di import dato che non siamo a conoscenza dei nomi dei file 
                 #e per rendere l'importazione dinamica
import sys  #serve per modificare a riga 38 i percorsi da cui prendere i file python
import abc
import inspect #serve per vedere i parametri
import subprocess #serve per eseguire comandi di sistema
import platform #serve per il multipiattaforma
import time #serve per operare con il tempo
from datetime import datetime #serve per l'ora esatta dei ping
import matplotlib.pyplot as plt #serve per creare il crafico dei ping
import smtplib #serve per inviare email via SMTP
from email.message import EmailMessage #usato per costruire l'email
from pathlib import Path #serve per ottenere il riferimento al percorso del file corrente
import matplotlib.dates as mdates
import numpy as np
from scipy.interpolate import make_interp_spline



class Plugin(Interfaccia_Plugin):
    vet_param = None
    
    def __init__(self):
        self.params = []
        self.keys = []

    def invioGrafico(self, email, dati, url):
        x = [d[0] for d in dati if d[1] is not None]
        y = [d[1] for d in dati if d[1] is not None]

        # Adatta la larghezza del grafico alla quantità di dati
        larghezza = 10 + min(len(x) // 20, 20)
        plt.figure(figsize=(larghezza, 5))

        # Se ci sono abbastanza dati, applica lo smoothing
        if len(x) > 10:
            # Converti datetime -> timestamp per l'interpolazione
            x_num = [dt.timestamp() for dt in x]
            x_np = np.array(x_num)
            y_np = np.array(y)

            # Interpolazione spline per rendere il grafico più liscio
            x_smooth = np.linspace(x_np.min(), x_np.max(), 500)
            spline = make_interp_spline(x_np, y_np, k=3)
            y_smooth = spline(x_smooth)

            # Converti di nuovo i timestamp in datetime
            x_smooth_dt = [datetime.fromtimestamp(ts) for ts in x_smooth]
            plt.plot(x_smooth_dt, y_smooth, label='Ping (smoothed)', color='blue')
        else:
            # Grafico normale se i dati sono pochi
            plt.plot(x, y, marker='o', label='Ping', color='blue')

        # Aggiunta titoli e griglia
        plt.title(f'Ping Monitor - {url}')
        plt.xlabel('Orario')
        plt.ylabel('Ping (ms)')
        plt.grid(True)

        # Gestione dinamica delle etichette X
        plt.xticks(rotation=45)
        if len(x) > 20:
            step = len(x) // 20
            plt.xticks(x[::step])

        # Formatta l'asse X se contiene datetime
        if isinstance(x[0], datetime):
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        # Salvataggio immagine
        plt.tight_layout()
        img_path = os.path.join(os.getcwd(), 'ping_graph.png')
        plt.savefig(img_path)
        plt.close()

        # prepara lâ€™email con lâ€™allegato
        msg = EmailMessage()
        msg['Subject'] = f'Grafico Monitoraggio - {url}'
        msg['From'] = 'nicolacasagrande54@gmail.com'
        msg['To'] = email
        msg.set_content('In allegato il grafico con i risultati del monitoraggio.')

        # allega lâ€™immagine
        with open(img_path, 'rb') as f:
            img_data = f.read()
            msg.add_attachment(img_data, maintype='image', subtype='png', filename='ping_graph.png')

        # invia lâ€™email con lâ€™allegato
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login('nicolacasagrande54@gmail.com', 'nizh qsff zgzv zasd')
            smtp.send_message(msg)

    def invioEmailAvviso(self, email, url):
        msg = EmailMessage()  # crea una nuova email
        msg['Subject'] = f' Server Offline - {url}'  # oggetto dellâ€™email
        msg['From'] = 'nicolacasagrande54@gmail.com'  # mittente (puoi cambiarlo)
        msg['To'] = email  # destinatario
        msg.set_content(f'Il server {url} Ã¨ stato rilevato come offline.')  # contenuto del messaggio

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:  # connessione al server SMTP
            smtp.starttls()  # cifratura della connessione
            smtp.login('nicolacasagrande54@gmail.com', 'nizh qsff zgzv zasd')  # login al server
            smtp.send_message(msg)  # invia lâ€™email

    def monitoraggio_server(self, email,url,tempo_monitoraggio):
        intervallo_ping = 0  # ogni N secondi fa un ping , per ora 1
        max_fail = 10  # ogni N tentativi manda l'avviso, per ora 2
        fail_count = 0  # contatore di ping falliti per fermare poi il ciclo
        dati_ping = []  # salva il futuro output
        start_time = time.time()  # orario di inizio del monitoraggio

        # loop che continua finchÃ© non finisce il tempo di monitoraggio o N tentativi falliscono
        while (time.time() - start_time) < tempo_monitoraggio: #time.time() da l'orario in quel momento
            try:
                # comando diverso a seconda del sistema operativo
                if platform.system().lower() == "windows":
                    comando = ["ping", "-n", "1", url]
                else:
                    comando = ["ping", "-c", "1", url] #linux e ios

                # esegue il ping con il comando salvato prima e salva il risultato
                result = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                if result.returncode == 0:  # se vero il ping Ã¨ riuscito
                    output = result.stdout  # prendiamo lâ€™output del ping
                    if platform.system().lower() == "windows": # comando diverso a seconda del sistema operativo
                        for line in output.splitlines():  # scorriamo ogni riga
                            if "durata=" in line:
                                time_part = line.split("durata=")[1].split("ms")[0].strip()
                                ping_ms = float(time_part)
                                break
                            elif "time=" in line:
                                time_part = line.split("time=")[1].split("ms")[0].strip()
                                ping_ms = float(time_part)
                                break
                            else:
                                ping_ms = 9999
                    else:
                        for line in output.splitlines():
                            if "time=" in line:
                                ping_ms = float(line.split("time=")[1].split(" ")[0])  
                                break
                        else:
                            ping_ms = 9999
                    #fail_count = 0   reset se il ping Ã¨ ok???
                else:
                    ping_ms = 9999  # ping fallito
                    fail_count += 1  
                    
            except Exception as e:  # errore nel ping
                ping_ms = 9999
                fail_count += 1

            oraPing = datetime.now()  # orario esatto del ping
            dati_ping.append((oraPing, ping_ms))  #salvo ora e tempo del ping

            if fail_count >= max_fail:
                self.invioEmailAvviso(email, url)  # se ha fallito troppe volte, manda avviso
                break

            time.sleep(intervallo_ping)  # aspetta prima del prossimo ping

        # dopo il monitoraggio manda il grafico via email
        self.invioGrafico(email, dati_ping, url)
        return dati_ping  # ritorna i dati raccolti 



    def execute(self):
        self.monitoraggio_server("samuele231106@gmail.com","vocari.me",60)
        return "Output"

    def get_param(self):
        return self.keys

    def set_param(self, vet_param):
        self.params = vet_param
        return True
