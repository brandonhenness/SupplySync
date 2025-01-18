import time
import logging
from watchdog.observers import Observer
from app.handlers import Handler


class watchDirectory:
    """
    Monitors a specified directory for changes and triggers the appropriate event handlers.
    """

    def __init__(self, config):
        """
        Initializes the directory watcher with the given configuration.
        :param config: The configuration object from `createConfig`.
        """
        self.config = config
        self.observer = Observer()

    def run(self):
        """
        Starts the observer to monitor the specified directory.
        """
        logging.info("STARTING DIRECTORY WATCHER")
        event_handler = Handler(self.config)
        self.observer.schedule(event_handler, self.config.downloadDir, recursive=True)
        self.observer.start()

        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logging.error(f"Error in directory watcher: {e}")
            self.stop()

    def stop(self):
        """
        Stops the observer.
        """
        self.observer.stop()
        logging.info("DIRECTORY WATCHER STOPPED")
        self.observer.join()
