import customtkinter as ctk
from tkinter import messagebox
import os

def get_login_info():
    ip_address = None
    username = None
    password = None

    root = ctk.CTk()
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("green")
    root.title("NetStrike Login")
    root.geometry("500x500")
    root.resizable(False, False)
    icona = os.path.join(os.path.dirname(__file__), 'er.ico')
    root.wm_iconbitmap(icona)
    def submit_info():
        nonlocal ip_address, username, password
        ip_address = ipEntry.get()
        username = usernameEntry.get()
        password = passwordEntry.get()
        if not ip_address or not username or not password:
            messagebox.showerror("Error", "all the fields are required!")
            return
        else:
            root.quit()
            root.destroy()

    def inviaSubmit(event):
        submit_info()
    
    frame_titolo = ctk.CTkFrame(root, fg_color="transparent")
    frame_titolo.pack(pady=25)

    label_net = ctk.CTkLabel(frame_titolo,text="Net",font=("Felix Titling", 50))
    label_net.pack(side="left") 

    label_strike = ctk.CTkLabel(frame_titolo,text="Strike",font=("Felix Titling", 50),text_color="#76ca7f")
    label_strike.pack(side="left")
    
    ipLabel = ctk.CTkLabel(root, text="ENTER IP ADDRESS:", font=("Felix Titling", 25))
    ipLabel.pack(pady=5)

    ipEntry = ctk.CTkEntry(root)
    ipEntry.pack(pady=10)

    usernameLabel = ctk.CTkLabel(root, text="ENTER USERNAME:", font=("Felix Titling", 25))
    usernameLabel.pack(pady=5)

    usernameEntry = ctk.CTkEntry(root)
    usernameEntry.pack(pady=10)

    passwordLabel = ctk.CTkLabel(root, text="ENTER PASSWORD:", font=("Felix Titling", 25))
    passwordLabel.pack(pady=5)

    passwordEntry = ctk.CTkEntry(root, show='*') 
    passwordEntry.pack(pady=10)

    submitButton =  ctk.CTkButton(root, text="SUBMIT", corner_radius=5, command=submit_info)
    submitButton.pack(pady=50)
    
    root.bind('<Return>', inviaSubmit)
    
    root.mainloop()

    return ip_address, username, password