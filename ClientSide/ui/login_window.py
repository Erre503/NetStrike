# login_window.py
import tkinter as tk

def get_ip_address():
    """Create a Tkinter window to prompt for the IP address."""
    ip_address = None  # Default value in case the user cancels or closes the window

    def submit_ip():
        nonlocal ip_address  # Access the outer function's variable
        ip_address = ip_entry.get()
        root.quit()
        root.destroy()
    root = tk.Tk()
    root.title("IP Address Login")

    ip_label = tk.Label(root, text="Enter IP Address:")
    ip_label.pack(pady=10)

    ip_entry = tk.Entry(root)
    ip_entry.pack(pady=5)

    submit_button = tk.Button(root, text="Submit", command=submit_ip)
    submit_button.pack(pady=10)

    root.mainloop()  # Start the Tkinter main event loop

    return ip_address  # Return the IP address after the window is closed
