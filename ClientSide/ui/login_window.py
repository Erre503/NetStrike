import customtkinter as ctk  # Import the customtkinter library for creating custom GUI elements
from tkinter import messagebox  # Import messagebox for displaying error messages
import os  # Import os for operating system related functionalities (not used in this code)

def get_login_info():
    # Initialize variables to store login information
    ip_address = None
    username = None
    password = None

    # Create the main application window
    root = ctk.CTk()
    ctk.set_appearance_mode("Dark")  # Set the appearance mode to dark
    ctk.set_default_color_theme("green")  # Set the default color theme to green
    root.title("NetStrike Login")  # Set the window title
    root.geometry("500x500")  # Set the window size
    root.resizable(False, False)  # Disable window resizing

    def submit_info():
        # Function to collect and validate user input
        nonlocal ip_address, username, password  # Access outer function variables
        ip_address = ipEntry.get()  # Get the IP address from the entry field
        username = usernameEntry.get()  # Get the username from the entry field
        password = passwordEntry.get()  # Get the password from the entry field
        
        # Check if any field is empty
        if not ip_address or not username or not password:
            messagebox.showerror("Error", "all the fields are required!")  # Show error message
            return
        else:
            root.quit()  # Exit the main loop
            root.destroy()  # Destroy the main window

    def inviaSubmit(event):
        # Function to handle the Enter key press event
        submit_info()  # Call the submit_info function
    
    # Create a frame for the title
    frame_titolo = ctk.CTkFrame(root, fg_color="transparent")
    frame_titolo.pack(pady=25)  # Add padding around the frame

    # Create and pack the "Net" label
    label_net = ctk.CTkLabel(frame_titolo, text="Net", font=("Felix Titling", 50))
    label_net.pack(side="left") 

    # Create and pack the "Strike" label with a different text color
    label_strike = ctk.CTkLabel(frame_titolo, text="Strike", font=("Felix Titling", 50), text_color="#76ca7f")
    label_strike.pack(side="left")
    
    # Create and pack the IP address label and entry field
    ipLabel = ctk.CTkLabel(root, text="ENTER IP ADDRESS:", font=("Felix Titling", 25))
    ipLabel.pack(pady=5)

    ipEntry = ctk.CTkEntry(root)  # Entry field for IP address
    ipEntry.pack(pady=10)

    # Create and pack the username label and entry field
    usernameLabel = ctk.CTkLabel(root, text="ENTER USERNAME:", font=("Felix Titling", 25))
    usernameLabel.pack(pady=5)

    usernameEntry = ctk.CTkEntry(root)  # Entry field for username
    usernameEntry.pack(pady=10)

    # Create and pack the password label and entry field
    passwordLabel = ctk.CTkLabel(root, text="ENTER PASSWORD:", font=("Felix Titling", 25))
    passwordLabel.pack(pady=5)

    passwordEntry = ctk.CTkEntry(root, show='*')  # Entry field for password with masked input
    passwordEntry.pack(pady=10)

    # Create and pack the submit button
    submitButton = ctk.CTkButton(root, text="SUBMIT", corner_radius=5, command=submit_info)
    submitButton.pack(pady=50)
    
    # Bind the Enter key to the inviaSubmit function
    root.bind('<Return>', inviaSubmit)
    
    root.mainloop()  # Start the main event loop

    # Return the collected login information
    return ip_address, username, password
