import os
import configparser
import logging
from genericpath import exists

class createConfig:
    """
    Handles the creation and loading of the SupplySync configuration file.
    """
    def __init__(self):
        config_dir = os.path.join(os.getcwd(), "data")
        config_file = os.path.join(config_dir, "SupplySync.ini")
        
        # Ensure the data directory exists
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # Create the config file with default settings if it does not exist
        if not exists(config_file):
            self.config = configparser.ConfigParser()
            self.config['DEFAULT'] = {
                'mainDir': os.getcwd(),
                'userCode': 'ARRAY.INTM',
                'departmentCode': '01.7020',
                'downloadDir': os.path.join(config_dir, "BATCH"),
                'processedDir': os.path.join(config_dir, "PROCESSED"),
                'uploadDir': os.path.join(config_dir, "HHT"),
                'hhtFile': os.path.join(config_dir, "HHT", "SupplySync.hht"),
            }
            with open(config_file, 'w') as cFile:
                self.config.write(cFile)
            logging.info('CONFIG FILE CREATED')
        
        # Read the existing config file
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.mainDir = self.config['DEFAULT']['mainDir']
        self.userCode = self.config['DEFAULT']['userCode']
        self.departmentCode = self.config['DEFAULT']['departmentCode']
        self.downloadDir = self.config['DEFAULT']['downloadDir']
        self.processedDir = self.config['DEFAULT']['processedDir']
        self.uploadDir = self.config['DEFAULT']['uploadDir']
        self.hhtFile = self.config['DEFAULT']['hhtFile']
        logging.info('CONFIG FILE LOADED')
