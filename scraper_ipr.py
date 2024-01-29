import pandas as pd
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from io import StringIO
from scraper import Scraper
from logger import Logger
from config import VAR
from time import time, sleep
from datetime import datetime, timedelta


class ScraperIpiranga(Scraper):

    def __init__(self):
        super().__init__()
        self.logger = Logger()

    def verifica_agendamentos(self, maximizado=False):

        pedidos_com_erro = {'hoje': [], 'amanha': [], 'erro_na_coleta': []}
        tentativa = 1
        max_tentativas = 3

        while True:
            try:
                self.logger.log(f"Iniciando verificação de agendamentos (tentativa {tentativa}/{max_tentativas})")
                self.navegador = self.inicializa_navegador(maximizado)
                self.inicio = time()

                self.navegador.get(VAR['link']) # Login na página principal
                self.preenche_input(VAR['id_input_login'], VAR['login'], xpath_ou_id='id')
                self.preenche_input(VAR['id_input_senha'], VAR['senha'], xpath_ou_id='id')
                self.clica_botao(VAR['xpath_button_entrar'])
                self.clica_botao(VAR['xpath_button_ribpreto'])
                self.logger.log(f"Login realizado com sucesso")
    
                dia_atual = datetime.now().day
                pedidos_com_erro['hoje'] = self.__coleta_pedidos(dia_atual)
                if pedidos_com_erro['hoje'] != []: self.logger.log(f"Pedidos com erro do dia {dia_atual}: {pedidos_com_erro['hoje']}")

                self.logger.log(f"Coletando agendamentos do próximo dia...")
                dia_seguinte = (datetime.now() + timedelta(days=1)).day

                self.__troca_dia_no_calendario(dia_seguinte)

                pedidos_com_erro['amanha'] = self.__coleta_pedidos(dia_seguinte)
                if pedidos_com_erro['amanha'] != []: self.logger.log(f"Pedidos com erro do dia {dia_seguinte}: {pedidos_com_erro['amanha']}")

                self.fechar_navegador()
                self.tempo_execucao = round(time() - self.inicio, 2)
                self.logger.log(f"Tempo de execução: {self.tempo_execucao}s")
                break

            except Exception as e:
                tentativa += 1
                self.fechar_navegador()

                if tentativa <= max_tentativas:
                    self.logger.log(f"Erro na verificação de agendamentos, nova tentativa em 30 segundos...")
                    sleep(30)
                    continue
                else:
                    self.logger.log(f"Verificação de agendamentos não realizada! Erro: {e}")
                    pedidos_com_erro['erro_na_coleta'] = str(e)
                    break

        return pedidos_com_erro

    def __coleta_pedidos(self, dia):

        sleep(2)
        elements = self.navegador.find_elements(By.XPATH, VAR['xpath_status'])
        self.logger.log(f"Quantidade de elementos de atualização de status: {len(elements)}")
        pedidos_com_erro = []

        if elements == []: self.logger.log(f"Ainda não há agendamentos para o dia {dia}")
        else:
            for element in elements:
                element.click()
                sleep(4)

            table = self.navegador.find_element(By.XPATH, VAR['xpath_table_agendamentos'])
            html_string = table.get_attribute('outerHTML')
            html_io = StringIO(html_string)
            self.logger.log(f"Dados da tabela de agendamentos coletados com sucesso")

            df = pd.read_html(html_io)[0]
            df.drop([('Agendamentos', 'Unnamed: 0_level_1'), ('Agendamentos', 'Confirmado')], axis=1, inplace=True)

            size_df_original = len(df)
            df = df[~df['Agendamentos', 'Modelo C.  Placa'].str.contains('EZU0899')]
            size_df = len(df)
            self.logger.log(f"Dados da tabela de agendamentos convertidos para DataFrame com sucesso")
            if size_df_original != size_df: self.logger.log(f"Linhas removidas do DataFrame (Placa EZU0899): {size_df_original - size_df}")

            for index, row in df.iterrows():
                id = row['Agendamentos', 'ID']
                horario = row['Agendamentos', 'Horário']
                status = row['Agendamentos', 'Status']
                pedido = f"🆔: {id}, ⏱️: {horario}, 📝: {status}"
                self.logger.log(pedido)
                status_ok = ['Faturado/Carregado', 'Agendamento Liberado']
                if status not in status_ok: pedidos_com_erro.append(pedido)

        return pedidos_com_erro
    
    def __troca_dia_no_calendario(self, dia):
            
        self.navegador.find_element(By.ID, "data").click()  # Encontrar o input de data e abrir o modal
        sleep(2)

        if dia == 1:
            self.clica_botao(VAR['xpath_button_calendario_nextmonth'])
            sleep(2)
        
        html_calendario = self.navegador.find_element(By.XPATH, VAR['xpath_calendario']).get_attribute('outerHTML')
        soup = BeautifulSoup(html_calendario, 'html.parser')    # Analisa o HTML

        elemento_dia = soup.find('td', string=str(dia))

        # Verifica se o elemento tem a classe "dp_not_in_month"
        while elemento_dia and 'dp_not_in_month' in elemento_dia.get('class', []):
            elemento_dia = elemento_dia.find_next('td', string=str(dia))   # Procura pelo próximo elemento

        # Obtém a posição do elemento do dia seguinte
        tds_anteriores = elemento_dia.find_all_previous('td')
        posicao_td = (len(tds_anteriores) % 7) + 1
        posicao_tr = (len(tds_anteriores) // 7) + 2

        xpath_dia_seguinte = f'/html/body/div[8]/table[2]/tbody/tr[{posicao_tr}]/td[{posicao_td}]'
        self.clica_botao(xpath_dia_seguinte)
        sleep(2)


if __name__ == "__main__":
    scraper = ScraperIpiranga()
    pedidos_com_erro = scraper.verifica_agendamentos(maximizado=True)
    print(f"Resultado: {pedidos_com_erro}")
