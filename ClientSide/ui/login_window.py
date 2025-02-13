import tkinter as tk

def get_login_info():
    """Create a Tkinter window to prompt for the IP address, username, and password."""
    ip_address = None  # Default value in case the user cancels or closes the window
    username = None
    password = None

    def submit_info():
        nonlocal ip_address, username, password  # Access the outer function's variables
        ip_address = ip_entry.get()
        username = username_entry.get()
        password = password_entry.get()
        root.quit()
        root.destroy()

    root = tk.Tk()
    root.title("Login Window")

    # IP Address
    ip_label = tk.Label(root, text="Enter IP Address:")
    ip_label.pack(pady=5)

    ip_entry = tk.Entry(root)
    ip_entry.pack(pady=5)

    # Username
    username_label = tk.Label(root, text="Enter Username:")
    username_label.pack(pady=5)

    username_entry = tk.Entry(root)
    username_entry.pack(pady=5)

    # Password
    password_label = tk.Label(root, text="Enter Password:")
    password_label.pack(pady=5)

    password_entry = tk.Entry(root, show='*')  # Use show='*' to hide the password input
    password_entry.pack(pady=5)

    # Submit Button
    submit_button = tk.Button(root, text="Submit", command=submit_info)
    submit_button.pack(pady=10)

    root.mainloop()  # Start the Tkinter main event loop

    return ip_address, username, password  # Return the IP address, username, and password after the window is closed

# Example usage
