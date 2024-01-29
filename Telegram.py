import requests
from config import TELEGRAM_CONFIG
from logger import Logger

class Telegram:

    def __init__(self):
        self.token = TELEGRAM_CONFIG['TOKEN']
        self.chat_id = TELEGRAM_CONFIG['IDCHAT']
    
    def enviar_mensagem(self, msg):
        try:
            data = {"chat_id": self.chat_id, "text": msg}
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            requests.post(url, data)
        except Exception as e:
            logger = Logger()
            logger.log_error("Telegram - Erro no sendMessage:", e)
