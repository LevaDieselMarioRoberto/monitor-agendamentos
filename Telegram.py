import requests

class Telegram:

    token = '6549384225:AAEBaKjBcOcY8jL_g6A81L9wIprhQuSZJNY'
    chat_id = -1002086817983
    
    def enviarMensagem(self, msg):
        try:
            data = {"chat_id": self.chat_id, "text": msg}
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            requests.post(url, data)
        except Exception as e:
            print("Erro no sendMessage:", e)
