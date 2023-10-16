from AgendamentoIprScraper import AgendamentoIprScraper
from Telegram import Telegram
from datetime import datetime, timedelta
import json
import logging
from logging.handlers import TimedRotatingFileHandler


log = "C:/Users/titrr/Documents/Projetos/monitor_agendamentos/dist/monitora_agendamentos/script.log"
arquivo_json = "C:/Users/titrr/Documents/Projetos/monitor_agendamentos/dist/monitora_agendamentos/pedidos.json"


def monitora_agendamentos():

    handler = TimedRotatingFileHandler(log, when="D", interval=1, backupCount=2, encoding='utf-8')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[handler])

    # Ajuste as configurações do handler
    handler.suffix = "%Y%m%d.log"  # Adiciona a data no nome do arquivo
    handler.extMatch = r"^\d{8}\.log$"

    logging.info('') # Linha em branco
    info = f"Iniciando o script..."
    print(info)
    logging.info(info)


    scraper_ipr = AgendamentoIprScraper()
    telegram = Telegram()

    pedidos = scraper_ipr.scrap_data()
    # pedidos = scraper_ipr.scrap_data(maximized=True)

    try:
        with open(arquivo_json, 'r') as infile:
            pedidos_json = json.load(infile)
    except FileNotFoundError:
        with open(arquivo_json, 'w') as outfile:
            arquivo_novo = {'hoje': [], 'amanha': [], 'erros': []}
            json.dump(arquivo_novo, outfile)
        with open(arquivo_json, 'r') as infile:
            pedidos_json = json.load(infile)


    if pedidos['erros'] == [] and pedidos_json['erros'] != []:
        mensagem = '✅ Script funcionando normalmente!'
        telegram.enviarMensagem(mensagem)
        logging.info(mensagem)

        pedidos_json['erros'] = []
        with open(arquivo_json, 'w') as outfile:
            json.dump(pedidos_json, outfile)


    if pedidos['erros'] != [] and pedidos['erros'] != pedidos_json['erros']:
        mensagem = '⚠️ Erro no script: \n'
        mensagem += pedidos['erros'][0]
        telegram.enviarMensagem(mensagem)
        logging.error(f'{pedidos["erros"][0]}')

        pedidos_json['erros'] = pedidos['erros']
        with open(arquivo_json, 'w') as outfile:
            json.dump(pedidos_json, outfile)

    else:
        if pedidos['hoje'] != [] and pedidos['hoje'] != pedidos_json['hoje']:
            hoje = datetime.now().strftime("%d/%m/%Y")
            mensagem = f'⛽ Pedidos {hoje}: \n'

            for pedido in pedidos['hoje']:
                mensagem += f'\n{pedido}'

            telegram.enviarMensagem(mensagem)
            logging.info(f'Alteração nos pedidos de hoje:')
            logging.info(f'Novo: {pedidos["hoje"]}')
            logging.info(f'Antigo: {pedidos_json["hoje"]}')
            pedidos_json['hoje'] = pedidos['hoje']
        else:
            logging.info(f'Sem alteração nos pedidos de hoje')


        if pedidos['amanha'] != [] and pedidos['amanha'] != pedidos_json['amanha']:
            amanha = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
            mensagem = f'⛽ Pedidos {amanha}: \n'

            for pedido in pedidos['amanha']:
                mensagem += f'\n{pedido}'

            telegram.enviarMensagem(mensagem)
            logging.info(f'Alteração nos pedidos de amanhã:')
            logging.info(f'Novo: {pedidos["amanha"]}')
            logging.info(f'Antigo: {pedidos_json["amanha"]}')
            pedidos_json['amanha'] = pedidos['amanha']
        else:
            logging.info(f'Sem alteração nos pedidos de amanhã')

        with open(arquivo_json, 'w') as outfile:
            json.dump(pedidos_json, outfile)

        logging.info(f'Script finalizado com sucesso!')


if __name__ == '__main__':
    monitora_agendamentos()
