import os
import time
import logging
import datetime
from datetime import date


class proccess:
    """
    Handles file parsing, HHT file creation, and related operations.
    """

    @staticmethod
    def parseFile(file, config):
        """
        Parses a batch file and returns the parsed data.
        :param file: The path to the batch file.
        :param config: The configuration object for paths.
        :return: Parsed batch data as a dictionary.
        """
        for _ in range(100):  # Ensure the file is fully written before reading.
            with open(file) as f:
                if any(line.strip() == 'END OF FILE' for line in f):
                    break
                time.sleep(0.1)

        parsed_batch = {}
        with open(file) as f:
            for index, line in enumerate(f):
                data = line.strip().split(',')
                if data[0] == 'END OF FILE':
                    batch_date = datetime.datetime.strptime(
                        f.readline().split(' ')[3], '%m/%d/%y'
                    ).strftime('%Y%m%d')
                    logging.info(f'FILE PARSED: {file}')
                    os.replace(file, os.path.join(config.processedDir, os.path.basename(file)))
                    logging.info(f'FILE MOVED TO: {config.processedDir}')
                    return [parsed_batch, index, batch_date]

                if data[0] not in parsed_batch:
                    parsed_batch[data[0]] = {}
                parsed_batch[data[0]][data[1]] = data[2]

    @staticmethod
    def createFile(batches, file_string, config):
        """
        Creates an HHT file using parsed batch data.
        :param batches: Parsed batch data as a list of dictionaries.
        :param file_string: Path to save the HHT file.
        :param config: The configuration object for dynamic values.
        """
        if not batches:
            return

        if os.path.exists(file_string):
            os.remove(file_string)
            logging.info(f'FILE DELETED: {file_string}')

        with open(file_string, "a") as file:
            transmission_date = date.today().strftime("%Y%m%d")
            total_transactions = 0
            total_batches = 0

            file.write(f'001 {transmission_date}{config.userCode: <20}\n')
            for batch in batches:
                transmission_date = batch[2]
                for inventory, transactions in batch[0].items():
                    total_batches += 1
                    file.write(f'050 {inventory: <10}{transmission_date}{config.departmentCode: <25}{config.userCode: <10}\n')
                    for stock_number, transaction_qty in transactions.items():
                        file.write(f'051 {stock_number: <20}{transaction_qty:0>10}{" " * 15}\n')
                    file.write(f'990 {len(transactions):0>6}\n')
                    total_transactions += len(transactions)

            file.write(f'999 {total_batches:0>6}{total_transactions:0>6}\n')
            logging.info(f'HHT FILE CREATED: {file_string}')

    @staticmethod
    def findAllFiles(directory):
        """
        Finds all .txt files in a directory.
        :param directory: The directory to search.
        :return: List of file paths.
        """
        logging.info(f'SCANNING DIRECTORY: {directory}')
        return [
            os.path.join(directory, file) for file in os.listdir(directory)
            if file.lower().endswith('.txt')
        ]

    @staticmethod
    def parseAllFiles(directory, config):
        """
        Parses all .txt files in the specified directory.
        :param directory: The directory to scan for files.
        :param config: The configuration object.
        :return: List of parsed file data.
        """
        parsed_files = []
        files = proccess.findAllFiles(directory)
        for file in files:
            parsed_files.append(proccess.parseFile(file, config))
        return parsed_files
