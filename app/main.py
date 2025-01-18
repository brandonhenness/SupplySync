import os
import logging
import threading
from app.config import createConfig
from app.watcher import watchDirectory
from app.tray import create_tray_icon

# Version information
VERSION = "3.1.2"


def setup_logging(config):
    """
    Sets up logging for the application.
    :param config: The configuration object from `createConfig`.
    """
    log_dir = os.path.join(config.mainDir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "SupplySync.log")
    logging.basicConfig(
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        level=logging.INFO,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ],
    )
    logging.info("Logging initialized")


def setup_directories(config):
    """
    Ensures required directories exist.
    :param config: The configuration object from `createConfig`.
    """
    for directory in [config.downloadDir, config.processedDir, config.uploadDir]:
        os.makedirs(directory, exist_ok=True)
        logging.info(f"Directory ensured: {directory}")


def main():
    """
    The main entry point of the application.
    """
    # Load configuration
    config = createConfig()

    # Set up logging
    setup_logging(config)

    # Ensure necessary directories exist
    setup_directories(config)

    logging.info(f"SupplySync v{VERSION} started")

    # Start the tray icon in a separate thread
    tray_thread = threading.Thread(target=create_tray_icon, args=(config, VERSION), daemon=True)
    tray_thread.start()

    # Start the directory watcher
    try:
        watcher = watchDirectory(config)
        watcher.run()
    except KeyboardInterrupt:
        logging.info("Application interrupted")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
