import os
import ctypes
import tkinter as tk
from pathlib import Path
from PIL import Image
from pystray import Icon, Menu, MenuItem


def hide_console():
    """
    Hides the console window.
    """
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


def show_console():
    """
    Shows the console window.
    """
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)


def toggle_console():
    """
    Toggles the visibility of the console window.
    """
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if ctypes.windll.user32.IsWindowVisible(hwnd):
        hide_console()
    else:
        show_console()


def open_settings(config):
    """
    Opens the configuration file in the default text editor.
    :param config: The configuration object from `createConfig`.
    """
    os.startfile(os.path.join(config.mainDir, "data", "SupplySync.ini"))

def open_about(version):
    """
    Opens the about window of SupplySync.

    This function creates a new Tkinter window with the title "About SupplySync",
    sets the favicon of the window, and displays application information.
    """
    about_window = tk.Tk()
    about_window.title("About SupplySync")

    # Set the favicon
    icon_path = Path("assets/favicon.ico")
    if icon_path.exists():
        about_window.wm_iconbitmap(str(icon_path))
    else:
        print("Favicon not found: assets/favicon.ico")

    about_window.resizable(False, False)

    # Display the logo
    logo_path = Path("assets/SupplySync_logo.png")
    if logo_path.exists():
        logo = tk.PhotoImage(file=str(logo_path))
        logo_label = tk.Label(about_window, image=logo)
        logo_label.image = logo  # Keep a reference to prevent garbage collection
        logo_label.pack()

    # Display application information
    info_text = (
        f"SupplySync version {version}\n\n"
        "Copyright © 2021 Brandon Henness\n"
        "All rights reserved.\n\n"
        "SupplySync facilitates the integration of ARRAY and MEDITECH systems, enabling "
        "seamless synchronization of inventory. It processes supply usage batch files "
        "from ARRAY into a handheld terminal (HHT) transmission file, adhering to the "
        "MEDITECH Materials Management Interface Specifications."
    )
    label = tk.Label(about_window, text=info_text, justify="center", padx=20, pady=20)
    label.pack()

    # Close button
    close_button = tk.Button(about_window, text="Close", command=about_window.destroy)
    close_button.pack(padx=20, pady=20)

    # Run the Tkinter main loop
    about_window.mainloop()

def exit_program():
    """
    Exits the application.
    """
    os._exit(0)


def create_tray_menu(config, version):
    """
    Creates the system tray menu.
    :param config: The configuration object from `createConfig`.
    :param version: The current version of the application.
    :return: A pystray Menu object.
    """
    return Menu(
        MenuItem("About SupplySync", lambda: open_about(version)),
        Menu.SEPARATOR,
        MenuItem("Show/Hide Console", toggle_console),
        MenuItem("Settings", lambda: open_settings(config)),
        MenuItem("Exit", exit_program),
    )


def create_tray_icon(config, version):
    """
    Creates and runs the system tray icon.
    :param config: The configuration object from `createConfig`.
    :param version: The current version of the application.
    """
    icon_path = os.path.join("assets", "SupplySync_icon.png")
    tray_icon = Icon(
        "SupplySync",
        Image.open(icon_path),
        menu=create_tray_menu(config, version),
    )
    tray_icon.run()
