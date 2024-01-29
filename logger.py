import logging
from config import ARQUIVO_LOG

class Logger:

    def __init__(self):
        self.log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(filename=ARQUIVO_LOG, level=logging.INFO, format=self.log_format, encoding='utf-8')

    def log(self, msg):
        logging.info(msg)
    
    def log_error(self, msg):
        logging.error(msg)
