#VERSIONE DA CAMBIARE , GIUSTO PER PROVARE IL CARICAMENTO DEI FILE
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Variabili globali per memorizzare il percorso dei file
file_caricato = None
files_caricati = []

def seleziona_file():
    """Apre la finestra di dialogo per la selezione del file .py"""
    global file_caricato

    # Finestra di dialogo per la selezione del file
    file_path = filedialog.askopenfilename(
        title="Seleziona un file .py",
        filetypes=[("File Python", "*.py")]
    )
    
    if file_path:
        # Verifica se il file è già stato caricato
        if file_path in files_caricati:
            messagebox.showinfo("Info", "Hai già caricato questo file.")
            return
        
        # Aggiungi il file alla lista dei file caricati
        files_caricati.append(file_path)
        aggiorna_lista_files()
        
        # Aggiorna il percorso del file caricato
        file_caricato = file_path

def carica_da_entry(event=None):
    """Carica il file dal percorso scritto nella casella di testo"""
    global file_caricato

    # Ottieni il percorso del file dalla casella di testo
    file_path = input_file.get().strip()
    
    if not file_path:
        messagebox.showwarning("Avviso", "Inserisci un percorso valido.")
        return
    
    # Verifica se il percorso è valido e il file esiste
    if not os.path.isfile(file_path) or not file_path.endswith('.py'):
        messagebox.showerror("Errore", "Per favore seleziona un file Python valido.")
        return
    
    # Verifica se il file è già stato caricato
    if file_path in files_caricati:
        messagebox.showinfo("Info", "Hai già caricato questo file.")
        return
    
    # Aggiungi il file alla lista dei file caricati
    files_caricati.append(file_path)
    aggiorna_lista_files()
    
    # Aggiorna il percorso del file caricato
    file_caricato = file_path

def aggiorna_lista_files():
    """Aggiorna la lista dei file caricati nel Listbox"""
    lista_box.delete(0, tk.END)  # Pulisce la lista
    for file in files_caricati:
        lista_box.insert(tk.END, os.path.basename(file))  # Aggiunge il nome del file alla lista

# Creazione della finestra principale
finestra = tk.Tk()
finestra.geometry("1920x1080")  
finestra.title("PLUG INC") 
finestra.config(bg='#eeeeee') 

# Etichetta "Plug Inc"
scrittaInCima = tk.Label(finestra, text="Plug Inc", font=("Arial", 24), bg="white")
scrittaInCima.place(relx=0.5, rely=0.05, anchor="center") 

# Linea orizzontale
lineaOrizzontale = tk.Canvas(finestra, width=1920, height=2, bg="black", bd=0, highlightthickness=0)
lineaOrizzontale.place(relx=0.5, rely=0.1, anchor="center") 

# Linea verticale
lineaVerticale = tk.Canvas(finestra, width=2, height=1150, bg="black", bd=0, highlightthickness=0)
lineaVerticale.place(relx=0.5, rely=0.65, anchor="center") 

# Sezione a sinistra della linea verticale
frame_left = tk.Frame(finestra, bg='#eeeeee')
frame_left.place(relx=0.05, rely=0.3, anchor="nw")  # Spostato vicinissimo al bordo sinistro

# Label "LOAD PLUG-IN:"
label_load = tk.Label(frame_left, text="LOAD PLUG-IN:", font=("Arial", 12), bg='#eeeeee')
label_load.grid(row=0, column=0, padx=10, pady=10, sticky="w")

# Input per il nome del file (sullo stesso livello della riga 0)
input_file = tk.Entry(frame_left, font=("Arial", 12), width=30)
input_file.grid(row=1, column=0, padx=10, pady=10)

# Bottone "BROWSE"
button_browse = tk.Button(frame_left, text="BROWSE", font=("Arial", 12), command=seleziona_file)
button_browse.grid(row=1, column=1, padx=10, pady=10)

# Label "AVAILABLE PLUG-IN:" (riga separata dalla Listbox)
label_available = tk.Label(frame_left, text="AVAILABLE PLUG-IN:", font=("Arial", 12), bg='#eeeeee')
label_available.grid(row=2, column=0, padx=10, pady=10, sticky="w")

# Lista per visualizzare i file caricati
lista_box = tk.Listbox(frame_left, width=30, height=10, font=("Arial", 12))
lista_box.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

# Avvia la finestra principale
finestra.mainloop()
