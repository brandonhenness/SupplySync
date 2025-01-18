import os
import time
import logging
from watchdog.events import PatternMatchingEventHandler
from app.processing import proccess

class Handler(PatternMatchingEventHandler):
    """
    Handles file creation events in the watched directory.
    """

    def __init__(self, config):
        """
        Initializes the handler with patterns for `.txt` files.
        :param config: The configuration object from `createConfig`.
        """
        self.config = config
        super().__init__(patterns=['*.txt'], ignore_directories=True, case_sensitive=False)

    def on_created(self, event):
        """
        Triggered when a new file is created in the monitored directory.
        :param event: The event object containing file path information.
        """
        logging.info(f'FILE CREATED: {event.src_path}')
        try:
            parsed_files = []
            parsed_files.append(proccess.parseFile(event.src_path, self.config))
            proccess.createFile(parsed_files, self.config.hhtFile)
        except Exception as e:
            logging.error(f'Error processing file {event.src_path}: {e}')
