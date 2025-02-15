import customtkinter as ctk
from tkinter import messagebox

def get_login_info():
    """Create a Tkinter window to prompt for the IP address, username, and password."""
    ip_address = None
    username = None
    password = None

    root = ctk.CTk()
    root.title("LOGIN WINDOW")
    root.geometry("500x500")
    root.resizable(False, False)

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

    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")

    pluginInkLabel = ctk.CTkLabel(root, text="PLUG INK", font=("Felix Titling", 50))
    pluginInkLabel.pack(pady=25)

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
