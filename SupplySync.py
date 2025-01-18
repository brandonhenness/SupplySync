# TODO: Add version control to project
version = '3.1.2'
"""
SupplySync is a program that takes the supply usage batch download from ARRAY and converts it 
into a handheld terminal (HHT) transmission file. SupplySync uses the MEDITECH Materials 
Management (MM) Interface Specifications to create the HHT transmission file and import the data 
provided by the ARRAY supply usage batch into MEDITECH.

Program: SupplySync
Version: 3.1.2
Date: 10/6/2022
Author: Brandon Henness

Maintinace information:
The Materials Management Interface Specifications documentation can be found on the MEDITECH 
website at the following link:
https://www.meditech.com/Specifications/CS/MM_00_SPEC_HTM_Interface_Specification_CS_MM_HHT_R1247.htm

Copyright (C) 2022 Brandon Henness - All Rights Reserved
You may use, distribute and modify this code under the
terms of the XYZ license, which unfortunately won't be
written for another century.

You should have received a copy of the XYZ license with
this file. If not, please write to: , or visit :

"""

import os
import time
import logging
import configparser
import datetime
import ctypes
import pystray
import tkinter
import threading

from PIL import Image
from genericpath import exists
from datetime import date
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class createConfig:
    """
    class createConfig:
    The createConfig class is used to create and read from the SupplySync.ini configuration file.

    On initialization, it checks if the config file exists. If it does not exist, it creates one with the default settings.
    If it does exist, it reads the config file and assigns the values to class variables.

    Attributes:
        mainDir (str): The main directory of the program.
        userCode (str): The user code for the MEDITECH interface.
        departmentCode (str): The department code for the MEDITECH interface.
        downloadDir (str): The directory where the ARRAY supply usage batch is downloaded to.
        processedDir (str): The directory where processed files are moved to.
        uploadDir (str): The directory where the HHT transmission file is saved to.
        hhtFile (str): The file path of the HHT transmission file.

    Methods:
        __init__(): Initializes the class and creates or reads the config file.
    """
    def __init__(self):
        if not exists('SupplySync\\SupplySync.ini'):
            self.config = configparser.ConfigParser()
            self.config['DEFAULT'] = {
                'mainDir' : os.getcwd(),
                'userCode' : 'ARRAY.INTM',
                'departmentCode' : '01.7020',
                'downloadDir' : '%(mainDir)s\\BATCH',
                'processedDir' : '%(mainDir)s\\PROCESSED',
                'uploadDir' : '%(mainDir)s\\HHT',
                'hhtFile' : '%(uploadDir)s\\SupplySync.hht',
            }
            with open('SupplySync\\SupplySync.ini', 'w') as cFile:
                self.config.write(cFile)
            logging.info('CONFIG FILE CREATED')

        self.config = configparser.ConfigParser()
        self.config.read('SupplySync\\SupplySync.ini')

        self.mainDir = self.config['DEFAULT']['mainDir']
        self.userCode = self.config['DEFAULT']['userCode']
        self.departmentCode = self.config['DEFAULT']['departmentCode']
        self.downloadDir = self.config['DEFAULT']['downloadDir']
        self.processedDir = self.config['DEFAULT']['processedDir']
        self.uploadDir = self.config['DEFAULT']['uploadDir']
        self.hhtFile = self.config['DEFAULT']['hhtFile']
        logging.info('CONFIG FILE LOADED')
  
class watchDirectory():
    """
    This class creates an observer object that monitors a specified directory for changes.
    When a file is created or modified in the directory, the observer triggers the 'run' method.
    
    Attributes:
        observer (Observer): The observer object that monitors the directory for changes.

    Methods:
        __init__(self): Initialize the observer object.
        run(self): Start the observer and specify the event handler and directory to be watched.
    """
    def __init__(self):
        """
        Initialize the observer object.
        """
        self.observer = Observer()
  
    def run(self):
        """
        Start the observer and specify the event handler and directory to be watched.
        The observer runs indefinitely, monitoring the specified directory for changes.
        """
        logging.info('OBSERVER STARTED')
        event_handler = Handler()
        self.observer.schedule(event_handler, config.downloadDir, recursive = True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            logging.info("OBSERVER STOPPED")
  
        self.observer.join()
            
class Handler(PatternMatchingEventHandler):
    """
    Class that handles the events of files being created in the watched directory.

    Attributes:
        None
        
    Methods:
        __init__(self): Initialize the class by setting the patterns for PatternMatchingEventHandler to be .txt files, ignoring directories, and not being case-sensitive.
        on_created(self, event): Event that is called when a file is created in the watched directory.
    """

    def __init__(self):
        """
        Initialize the class by setting the patterns for PatternMatchingEventHandler to be .txt files, ignoring directories, and not being case-sensitive.
        
        :param self: The object being initialized.
        :return: None
        """
        PatternMatchingEventHandler.__init__(self, patterns=['*.txt'], ignore_directories=True, case_sensitive=False)
  
    def on_created(self, event):
        """
        Event that is called when a file is created in the watched directory.
        
        :param event: The event that triggered the call of this function.
        :return: None
        """
        logging.info(f'FILE | {event.src_path} | CREATED')

        parsed_files = []
        parsed_files.append(proccess.parseFile(event.src_path))
        proccess.createFile(parsed_files, config.hhtFile)
        
class proccess:
    """
    The proccess class contains methods for processing and parsing batch files in a directory.

    Attributes:
        None

    Methods:
        parseFile(file): Parses the batch file and returns a dictionary containing all the parsed data.
        createFile(batches, file): Creates an HHT file for upload into MEDITECH using the data parsed from the batch file.
        uploadFile(): Uploads the HHT file to MEDITECH.
        findAllFiles(dir): Finds all files in the upload directory and returns a list of them.
        parseAllFiles(dir): Parses all files in the upload directory and returns a list of dictionaries containing all the parsed data.
    """

    def parseFile(file):
        """
        parseFile(file)
        Parse the batch file and return a dictionary containing all the parsed data.

        :param file: str, the file path of the batch file to parse.
        :return: list, containing the parsed data in the form of a dictionary, the index of the last line of the parsed file, and the date of the batch file in the form of a string.
        """
        # check if file contains "END OF FILE" and if it does, parse the file.
        # Do this 100 times to make sure the file is done writing.
        for _ in range(100):
            with open(file) as f:
                for line in f:
                    if line.strip() == 'END OF FILE':
                        break
                else:
                    time.sleep(0.1)
                    continue
                break
        parsed_batch = {}
        with open(file) as f:
            for index, line in enumerate(f):
                data = line.strip().split(',')
                if data[0] == 'END OF FILE':
                    # End of file found.
                    # Retreive next line and parse date from it. The line will have the following format: 'OR+ SUPPLIES DOWNLOADED 01/16/23 AT 1011 ARRAY BATCH# 4607'
                    # The date will be used to create the HHT file.
                    date = datetime.datetime.strptime(f.readline().split(' ')[3], '%m/%d/%y').strftime('%Y%m%d')
                    logging.info(f'FILE | {file} | PARSED')
                    # Move the batch file to the processed directory.
                    # Close file and return the parsed data.
                    f.close()
                    os.replace(file, f'{config.processedDir}\\{os.path.basename(file)}')
                    logging.info(f'FILE | {file} | MOVED TO {config.processedDir}')
                    return [parsed_batch, index, date]
                if not data[0] in parsed_batch.keys():
                    parsed_batch[data[0]] = {}
                parsed_batch[data[0]][data[1]] = data[2]
    
    def createFile(batches, file_string):
        """
        Create an HHT file for upload into MEDITECH using the data parsed from the batch file.
        This function writes the parsed data into a file in the format that follows MEDITECH's Materials Management Interface Specifications.
        
        :param batches: list of dictionaries containing all the parsed data.
        :param file: file object to write the data into.
        :return: None
        """
        if not batches:
            return
        # TODO: Add a check to see if the file was created recently. If it was, add to it instead of deleting it and creating a new one.
        if exists(file_string):
            os.remove(file_string)
            logging.info(f'FILE | {file_string} | DELETED')
        file = open(file_string, "a")

        transmissionDate = date.today().strftime("%Y%m%d")
        totalTransactions = 0
        totalBatches = 0
            
        file.write(f'001 {transmissionDate}{config.userCode: <20}\n')
        for batch in batches:
            transmissionDate = batch[2]
            for inventory, transactions in batch[0].items():
                totalBatches += 1
                file.write(f'050 {inventory: <10}{transmissionDate}{config.departmentCode: <25}{config.userCode: <10}\n')
                for stocknumber, transactionQty in transactions.items():
                    file.write(f'051 {stocknumber: <20}{transactionQty:0>10}{" "*15}\n')
                file.write(f'990 {len(batch[0][inventory]):0>6}\n')
                totalTransactions += len(batch[0][inventory])
        file.write(f'999 {totalBatches:0>6}{totalTransactions:0>6}\n')
        logging.info(f'FILE | {file_string} | CREATED')

        file.close()

    def uploadFile():
        """
        Upload the HHT file to MEDITECH.
        This function is not yet implemented.

        :pram: None
        :return: None
        """
        pass

    def findAllFiles(dir):
        """
        Find all files in the upload directory and return a list of them.
        
        :param dir: str: The directory where the files will be searched for.
        :return: list: A list of file paths that were found in the directory
        """
        logging.info(f'FINDING ALL DERELICT FILES IN {dir}...')
        files = []
        for file in os.listdir(dir):
            if file.endswith('.TXT') or file.endswith('.txt'):
                logging.info(f'FILE FOUND | {file}')
                files.append(dir + '\\' + file)
        return files
    
    def parseAllFiles(dir):
        """
        Parse all files in the specified directory and return a list of dictionaries containing all the parsed data.

        :param dir: str: The directory to search for files in.
        :return: list: A list of dictionaries containing the parsed data from all files in the directory.
        """
        parsed_files = []
        files = proccess.findAllFiles(dir)
        if files:
            logging.info(f'PROCESSING ALL DERELICT FILES IN {dir}...')
            logging.info(f'FOUND {len(files)} FILES')
        for file in files:
            logging.info(f'PARSING FILE | {file}')
            parsed_files.append(proccess.parseFile(file))
        return parsed_files

def hide_console():
    """
    Hides the console window.
    This function uses ctypes library to hide the console window by calling ShowWindow() method from the user32 module and passing the handle of the console window and 0 as arguments.
    
    :pram: None
    :return: None
    """
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def show_console():
    """
    Shows the console window.
    This function uses ctypes library to show the console window by calling ShowWindow() method from the user32 module and passing the handle of the console window and 1 as arguments.
    
    
    :pram: None
    :return: None
    """
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)

def toggle_console():
    """
    Toggles the visibility of the console window.
    This function uses ctypes library to check the visibility of the console window by calling IsWindowVisible() method from the user32 module and passing the handle of the console window as argument.
    If the console window is visible it calls the hide_console() function, otherwise it calls the show_console() function.
    
    :pram: None
    :return: None
    """
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if ctypes.windll.user32.IsWindowVisible(hwnd):
        hide_console()
    else:
        show_console()

def open_settings():
    """
    Open the settings file in the default text editor.
    This function opens the SupplySync.ini file located in the current working directory using the os.startfile() method.
    This method will open the file with the default text editor associated with the file type.
    
    
    :pram: None
    :return: None
    """
    # Open the settings file in the default text editor.
    os.startfile(f'{os.getcwd()}\\SupplySync\\SupplySync.ini')

def open_about():
    """
    Open the about window of SupplySync.
    This function creates a new Tkinter window with the title "About SupplySync", it sets the favicon of the window to the file favicon.ico. It creates a non-resizable window.
    It then creates a PhotoImage object of the file "SupplySync_logo.png" and displays it on the window.
    It creates a Label object that displays the version number of SupplySync and Copyright information.
    It creates a button that closes the window when clicked.
    
    :pram: None
    :return: None
    """
    about_window = tkinter.Tk()
    about_window.title("About SupplySync")
    about_window.wm_iconbitmap("SupplySync\\favicon.ico")
    about_window.resizable(False, False)

    logo = tkinter.PhotoImage(file=f'SupplySync\\SupplySync_logo.png')
    logo_label = tkinter.Label(about_window, image=logo)
    logo_label.pack()
    
    label = tkinter.Label(about_window, text=f'SupplySync version {version}\n\nCopyright © 2021 Brandon Henness\nAll rights reserved.\n\nSupplySync is a program that facilitates the integration of ARRAY and MEDITECH\nsystems, enabling seamless synchronization of inventory. The program utilizes the\nsupply usage batch download from ARRAY and converts it into a Handheld\nTerminal (HHT) transmission file, adhering to the MEDITECH Materials\nManagement Interface (MM) Specifications. This allows for the efficient\nimportation of data provided by the ARRAY supply usage batch into MEDITECH.')
    label.pack(padx=20, pady=20)

    close_button = tkinter.Button(about_window, text="Close", command=about_window.destroy)
    close_button.pack(padx=20, pady=20)

    about_window.mainloop()

def exit():
    """
    Exit the program.
    This function exits the program by calling os._exit(0), it's important to note that this method may not be the best way to end the program, it may leave resources open and it may not call cleanup functions.
    
    :pram: None
    :return: None
    """
    #TODO: clean up before exiting.
    os._exit(0)

def create_tray_menu():
    """
    Create a tray menu.
    This function creates a pystray.Menu object with the following options:
    - About SupplySync: Open the about window of SupplySync.
    - Show/Hide Console: Toggles the visibility of the console window.
    - Settings: Open the settings file in the default text editor.
    - Exit: Exit the program.
    It returns the created menu.
    
    :pram: None
    :return: None
    """
    menu = pystray.Menu(
        pystray.MenuItem('About SupplySync', open_about),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Show/Hide Console', toggle_console),
        pystray.MenuItem('Settings', open_settings),
        pystray.MenuItem('Exit', exit)
    )
    return menu

def create_tray_icon():
    """
    Create a tray icon.
    This function creates a pystray.Icon object named 'SupplySync' with the icon 'SupplySync_icon.png' and the menu returned by the create_tray_menu function.
    It runs the icon, making it visible in the system tray.
    
    :pram: None
    :return: None
    """
    tray = pystray.Icon('SupplySync', icon=Image.open(f'SupplySync\\SupplySync_icon.png'), menu=create_tray_menu())
    tray.run()

def main():
    """
    Main function.
    This function is the main function of the program, it is called when the program is started.
    """
    # Start logging.
    logging.basicConfig(
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%SZ',
        level=logging.INFO,
        handlers=[
            logging.FileHandler('SupplySync\\SupplySync.log'),
            logging.StreamHandler()
        ]
    )

    print('Program: SupplySync')
    print(f'Version: {version}')
    print('Date:    10/6/2022')
    print('Author:  Brandon Henness')
    print('')
    print('This program will watch a directory for new batch files from ARRAY.')
    print('When a new batch file is found, it will be parsed and an HHT file will be created.')
    # print('The HHT file will then be uploaded to MEDITECH.')
    print('')
    print('Press Ctrl+C to exit.')
    print('')
    # Load config file.
    os.chdir(os.path.realpath(os.path.dirname(__file__)))
    global config
    config = createConfig()


    # Create directories if they do not exist.
    if not os.path.exists(config.processedDir):
        logging.info('PROCESSED DIRECTORY CREATED')
        os.makedirs(config.processedDir)
    if not os.path.exists(config.downloadDir):
        logging.info('DOWNLOAD DIRECTORY CREATED')
        os.makedirs(config.downloadDir)
    if not os.path.exists(config.uploadDir):
        logging.info('UPLOAD DIRECTORY CREATED')
        os.makedirs(config.uploadDir)

    # Create an upload file for all files in the upload directory.
    if exists(config.hhtFile):
        os.remove(config.hhtFile)
        logging.info(f'FILE | {config.hhtFile} | DELETED')
    proccess.createFile(proccess.parseAllFiles(config.downloadDir), config.hhtFile)

    # Hide console.
    hide_console()

    # Create an interface thread.
    interface_thread = threading.Thread(target=create_tray_icon)
    interface_thread.start()

    # Create an observer object and Startup file monitoring of the watched directory.
    watcher = watchDirectory()
    watcher.run()
  
if __name__ == '__main__':
    main()
