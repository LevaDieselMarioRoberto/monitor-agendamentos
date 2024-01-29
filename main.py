import json
import logging
from datetime import datetime, timedelta, time
from config import ARQUIVO_JSON_PEDIDOS
from scraper_ipr import ScraperIpiranga
from telegram import Telegram
from logger import Logger

def main():
    logger = Logger()
    telegram = Telegram()
    scraper = ScraperIpiranga()

    now = datetime.now()
    weekday = now.weekday()
    current_time = now.time()

    # Verificação de internet/energia em sábados ou domingos às 10h e 18h
    if weekday >= 5 and (time(9, 55) < current_time < time(10, 7) or time(16, 55) < current_time < time(18, 7)):
        telegram.enviar_mensagem('Verificação de internet/energia ✅')

    # Verificação de horário para execução do script
    if time(1, 30) <= current_time <= time(23, 30):
        logger.log(f"   --- Iniciando verificação... ---")
        pedidos_com_erro = scraper.verifica_agendamentos(maximizado=False)

        try: 
            with open(ARQUIVO_JSON_PEDIDOS, 'r') as f: pedidos_json = json.load(f)
        except FileNotFoundError:
            pedidos_json = {'hoje': [], 'amanha': [], 'erro_na_coleta': []}
            with open(ARQUIVO_JSON_PEDIDOS, 'w') as f: json.dump(pedidos_json, f)

        # Verifica se houve erro na coleta e se é diferente do último erro
        if pedidos_com_erro['erro_na_coleta'] != [] and pedidos_com_erro['erro_na_coleta'] != pedidos_json['erro_na_coleta']:
            mensagem = f'⚠️ Erro no script: {pedidos_com_erro["erro_na_coleta"]}'
            telegram.enviar_mensagem(mensagem)
            logging.error(mensagem)
            pedidos_json['erro_na_coleta'] = pedidos_com_erro['erro_na_coleta']

        else:
            # Verifica se havia erro na coleta e agora não há mais
            if pedidos_com_erro['erro_na_coleta'] == [] and pedidos_json['erro_na_coleta'] != []:
                mensagem = '✅ Script funcionando normalmente!'
                telegram.enviar_mensagem(mensagem)
                logger.log(mensagem)
                pedidos_json['erro_na_coleta'] = []

            # Análise de erro nos pedidos de hoje e amanhã
            for dia in ['hoje', 'amanha']:
                if dia == 'hoje': data = datetime.now().strftime("%d/%m/%Y")
                else: data = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
                mensagem = f'⛽ Agendamentos {data}:'

                # Verifica se existem erros nos agendamentos e se é diferente do último erro
                if pedidos_com_erro[dia] != [] and pedidos_com_erro[dia] != pedidos_json[dia]:
                    for pedido in pedidos_com_erro[dia]: mensagem += f'\n{pedido}'
                    telegram.enviar_mensagem(mensagem)
                    logger.log(f'Alteração nos pedidos de {data}:')
                    logger.log(f'Novo: {pedidos_com_erro[dia]}')
                    logger.log(f'Anterior: {pedidos_json[dia]}')
                    pedidos_json[dia] = pedidos_com_erro[dia]

                # Verifica se havia erro nos agendamentos e agora não há mais
                elif pedidos_com_erro[dia] == [] and pedidos_json[dia] != []:
                    mensagem += f'\n✅ Nenhuma restrição'
                    telegram.enviar_mensagem(mensagem)
                    logger.log(f'Nenhuma restrição')
                    pedidos_json[dia] = pedidos_com_erro[dia]

                # Se não houve alteração nos pedidos
                else: logger.log(f'Sem alteração nos pedidos de {data}')

        with open(ARQUIVO_JSON_PEDIDOS, 'w') as f: json.dump(pedidos_json, f)
        logger.log(f'Script finalizado com sucesso!')


if __name__ == '__main__':
    main()
