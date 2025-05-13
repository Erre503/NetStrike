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
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
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
        self.keys = ["reciver_email", "target_url", "seconds"]

    def invioGrafico(self, dati):
        x = [d[0] for d in dati if d[1] is not None]
        y = [d[1] for d in dati if d[1] is not None]

        if not x or not y:
            print("No data to plot.")
            return

        larghezza = 10 + min(len(x) // 20, 20)

        fig = Figure(figsize=(larghezza, 5))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        if len(x) > 10:
            x_num = [dt.timestamp() for dt in x]
            x_np = np.array(x_num)
            y_np = np.array(y)

            x_smooth = np.linspace(x_np.min(), x_np.max(), 500)
            spline = make_interp_spline(x_np, y_np, k=3)
            y_smooth = spline(x_smooth)
            x_smooth_dt = [datetime.fromtimestamp(ts) for ts in x_smooth]
            ax.plot(x_smooth_dt, y_smooth, label='Ping (smoothed)', color='blue')
        else:
            ax.plot(x, y, marker='o', label='Ping', color='blue')

        ax.set_title(f'Ping Monitor - {self.params[1]}')
        ax.set_xlabel('Orario')
        ax.set_ylabel('Ping (ms)')
        ax.grid(True)

        if isinstance(x[0], datetime):
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        fig.autofmt_xdate()

        img_path = os.path.join(os.getcwd(), 'ping_graph.png')
        canvas.print_png(img_path)

        # --- Email sending remains the same ---
        msg = EmailMessage()
        msg['Subject'] = f'Grafico Monitoraggio - {self.params[1]}'
        msg['From'] = 'nicolacasagrande54@gmail.com'
        msg['To'] = self.params[0]
        msg.set_content('In allegato il grafico con i risultati del monitoraggio.')

        with open(img_path, 'rb') as f:
            img_data = f.read()
            msg.add_attachment(img_data, maintype='image', subtype='png', filename='ping_graph.png')

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login('nicolacasagrande54@gmail.com', 'nizh qsff zgzv zasd')
            smtp.send_message(msg)

        def invioEmailAvviso(self):
            msg = EmailMessage()  # crea una nuova email
            msg['Subject'] = f' Server Offline - {self.params[1]}'  # oggetto dellâ€™email
            msg['From'] = 'nicolacasagrande54@gmail.com'  # mittente (puoi cambiarlo)
            msg['To'] = self.params[0]  # destinatario
            msg.set_content(f'Il server {self.params[1]} Ã¨ stato rilevato come offline.')  # contenuto del messaggio

            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:  # connessione al server SMTP
                smtp.starttls()  # cifratura della connessione
                smtp.login('nicolacasagrande54@gmail.com', 'nizh qsff zgzv zasd')  # login al server
                smtp.send_message(msg)  # invia lâ€™email

    def execute(self):
        matplotlib.use("Agg")# Use non-interactive backend for thread safety
        intervallo_ping = 0  # ogni N secondi fa un ping , per ora 1
        max_fail = 10  # ogni N tentativi manda l'avviso, per ora 2
        fail_count = 0  # contatore di ping falliti per fermare poi il ciclo
        dati_ping = []  # salva il futuro output
        start_time = time.time()  # orario di inizio del monitoraggio
        # loop che continua finchÃ© non finisce il tempo di monitoraggio o N tentativi falliscono
        while (time.time() - start_time) < self.params[2]: #time.time() da l'orario in quel momento
            try:
                # comando diverso a seconda del sistema operativo
                if platform.system().lower() == "windows":
                    comando = ["ping", "-n", "1", self.params[1]]
                else:
                    comando = ["ping", "-c", "1", self.params[1]] #linux e ios

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
                self.invioEmailAvviso()  # se ha fallito troppe volte, manda avviso
                break

            time.sleep(intervallo_ping)  # aspetta prima del prossimo ping

        # dopo il monitoraggio manda il grafico via email
        self.invioGrafico(dati_ping)
        return f"Mail sent to {self.params[0]} for ping analisys on {self.params[1]} for {self.params[2]} seconds"  # ritorna i dati raccolti 

    def get_param(self):
        return self.keys

    def set_param(self, vet_param):
        try:
            self.params = []
            self.params.append(vet_param["reciver_email"])
            self.params.append(vet_param["target_url"])
            self.params.append(float(vet_param["seconds"]))
        except (ValueError, KeyError):
            return False
        return self.keys   