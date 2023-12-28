from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from time import sleep, time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import pandas as pd
from io import StringIO
import logging
from logging.handlers import TimedRotatingFileHandler
from bs4 import BeautifulSoup


class AgendamentoIprScraper:


    def __init__(self):

        self.log = 'C:/Users/titrr/Documents/Projetos/monitor_agendamentos/dist/monitora_agendamentos/script.log'
        self.env = 'C:/Users/titrr/Documents/Projetos/monitor_agendamentos/.env'

        # Configurações de Log
        handler = TimedRotatingFileHandler(self.log, when="D", interval=1, backupCount=2, encoding='utf-8')
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[handler])

        # Ajuste as configurações do handler
        handler.suffix = "%Y%m%d.log"  # Adiciona a data no nome do arquivo
        handler.extMatch = r"^\d{8}\.log$"

        info = f"Iniciando o scraper..."
        print(info)
        logging.info(info)


    def carrega_variaveis(self):
        try:
            load_dotenv(dotenv_path=self.env)
            self.LINK_IPR = os.getenv("LINK_IPR")
            self.LOGIN_IPR = os.getenv("LOGIN_IPR")
            self.SENHA_IPR = os.getenv("SENHA_IPR")
            self.ID_INPUT_LOGIN_IPR = os.getenv("ID_INPUT_LOGIN_IPR")
            self.ID_INPUT_SENHA_IPR = os.getenv("ID_INPUT_SENHA_IPR")
            self.XPATH_BUTTON_ENTRAR_IPR = os.getenv("XPATH_BUTTON_ENTRAR_IPR")
            self.XPATH_BUTTON_RIBPRETO_IPR = os.getenv("XPATH_BUTTON_RIBPRETO_IPR")
            self.XPATH_BUTTON_CALENDARIO_IPR = os.getenv("XPATH_BUTTON_CALENDARIO_IPR")
            self.XPATH_STATUS_IPR = os.getenv("XPATH_STATUS_IPR")
            self.XPATH_TABLE_AGENDAMENTOS_IPR = os.getenv("XPATH_TABLE_AGENDAMENTOS_IPR")
            self.XPATH_BUTTON_CALENDARIO_NEXTMONTH = os.getenv("XPATH_BUTTON_CALENDARIO_NEXTMONTH")
            self.XPATH_CALENDARIO = os.getenv("XPATH_CALENDARIO")
            self.tempo_espera = 30

            # Verifica se as variáveis não são nulas
            if not self.LINK_IPR or not self.LOGIN_IPR or not self.SENHA_IPR or not self.ID_INPUT_LOGIN_IPR or not self.ID_INPUT_SENHA_IPR or not self.XPATH_BUTTON_ENTRAR_IPR or not self.XPATH_BUTTON_RIBPRETO_IPR or not self.XPATH_STATUS_IPR or not self.XPATH_TABLE_AGENDAMENTOS_IPR:
                erro = f"Alguma variável não foi definida"
                raise Exception(erro)

            info = f"Variáveis de ambiente carregadas com sucesso"
            logging.info(info)
            print(info)
            return []
        except Exception as e:
            erro = f"Erro ao carregar as variáveis de ambiente"
            logging.error(f"{erro}: {e}")
            print(f"{erro}: {e}")
            return [erro]


    def inicializa_navegador(self, maximized=False):
        try:
            self.options = webdriver.EdgeOptions()
            self.options.add_argument("--log-level=1")  # Define o nível de log para WARNING, ERROR e SEVERE

            if maximized:
                self.options.add_argument("--start-maximized")
                self.options.add_argument("--force-device-scale-factor=0.8")
            else:
                self.options.add_argument("--headless")
                self.options.add_argument("--disable-gpu")
                self.options.add_argument("--window-size=1920x1080")

            svc = EdgeService(EdgeChromiumDriverManager().install())
            self.navegador = webdriver.Edge(service=svc, options=self.options)

            info = f"Navegador configurado com sucesso"
            logging.info(info)
            print(info)
            return []
        except Exception as e:
            erro = f"Erro ao configurar o navegador"
            logging.error(f"{erro}: {e}")
            print(f"{erro}: {e}")
            return [erro]


    def login(self):
            try:
                self.navegador.get(self.LINK_IPR)
                WebDriverWait(self.navegador, self.tempo_espera).until(EC.presence_of_element_located((By.ID, self.ID_INPUT_LOGIN_IPR))).send_keys(self.LOGIN_IPR)
                WebDriverWait(self.navegador, self.tempo_espera).until(EC.presence_of_element_located((By.ID, self.ID_INPUT_SENHA_IPR))).send_keys(self.SENHA_IPR)
                WebDriverWait(self.navegador, self.tempo_espera).until(EC.presence_of_element_located((By.XPATH, self.XPATH_BUTTON_ENTRAR_IPR))).click()
                WebDriverWait(self.navegador, self.tempo_espera).until(EC.presence_of_element_located((By.XPATH, self.XPATH_BUTTON_RIBPRETO_IPR))).click()

                info = f"Acesso ao portal da Ipiranga realizado com sucesso"
                logging.info(info)
                print(info)
                return []
            except Exception as e:
                erro = f"Erro ao acessar o portal da Ipiranga"
                logging.error(f"{erro}: {e}")
                print(f"{erro}: {e}")
                return [erro]


    def scrap(self, dia):

        pedidos = []
        erros = []

        if dia == 'amanhã':
            dia_seguinte_msg = f"Coletando agendamentos para amanhã..."
            print(dia_seguinte_msg)
            logging.info(dia_seguinte_msg)

            # Encontrar o input de data e abrir o modal
            self.navegador.find_element(By.ID, "data").click()
            sleep(2)

            amanha = str((datetime.now() + timedelta(days=1)).day)
            print(f"Definiu a data para o dia {amanha} no input")
            if amanha == '1':
                WebDriverWait(self.navegador, self.tempo_espera).until(EC.presence_of_element_located((By.XPATH, self.XPATH_BUTTON_CALENDARIO_NEXTMONTH))).click()
                sleep(2)

            html_calendario = self.navegador.find_element(By.XPATH, self.XPATH_CALENDARIO).get_attribute('outerHTML')
            soup = BeautifulSoup(html_calendario, 'html.parser')    # Analisa o HTML

            elemento_amanha = soup.find('td', string=str(amanha))

            # Verifica se o elemento tem a classe "dp_not_in_month"
            while elemento_amanha and 'dp_not_in_month' in elemento_amanha.get('class', []):
                elemento_amanha = elemento_amanha.find_next('td', string=str(amanha))   # Procura pelo próximo elemento

            # Obtém a posição do elemento do dia seguinte
            tds_anteriores = elemento_amanha.find_all_previous('td')
            posicao_td = (len(tds_anteriores) % 7) + 1
            posicao_tr = (len(tds_anteriores) // 7) + 2

            # Clica no dia seguinte
            xpath_dia_seguinte = f'/html/body/div[8]/table[2]/tbody/tr[{posicao_tr}]/td[{posicao_td}]'
            WebDriverWait(self.navegador, self.tempo_espera).until(EC.presence_of_element_located((By.XPATH, xpath_dia_seguinte))).click()
            sleep(2)

        try:
            sleep(2)
            elements = self.navegador.find_elements(By.XPATH, self.XPATH_STATUS_IPR)

            info = f"Quantidade de elementos de atualização de status: {len(elements)}"
            logging.info(info)
            print(info)
        except Exception as e:
            erro = f"Erro ao encontrar os elementos de atualização de status"
            erros.append(erro)
            erro += f": {e}"
            logging.error(erro)
            print(erro)
            return pedidos, erros

        if elements == []:
            print(f"Não há agendamentos disponíveis para {dia}")
        else:
            try:
                contador = 0
                for element in elements:
                    element.click()
                    contador += 1
                    sleep(4)

                info = f"Elementos de atualização de status clicados com sucesso. Quantidade: {contador}"
                logging.info(info)
                print(info)
            except Exception as e:
                erro = f"Erro ao clicar nos elementos de atualização de status"
                erros.append(erro)
                erro += f": {e}"
                logging.error(erro)
                print(erro)
                return pedidos, erros

            try:
                table = self.navegador.find_element(By.XPATH, self.XPATH_TABLE_AGENDAMENTOS_IPR)
                html_string = table.get_attribute('outerHTML')
                html_io = StringIO(html_string)

                info = f"Dados da tabela de agendamentos coletados com sucesso"
                logging.info(info)
                print(info)
            except Exception as e:
                erro = f"Erro ao coletar os dados da tabela de agendamentos"
                erros.append(erro)
                erro += f": {e}"
                logging.error(erro)
                print(erro)
                return pedidos, erros

            try:
                df = pd.read_html(html_io)[0]
                df.drop([('Agendamentos', 'Unnamed: 0_level_1'), ('Agendamentos', 'Confirmado')], axis=1, inplace=True)

                size_df_original = len(df)
                df = df[~df['Agendamentos', 'Modelo C.  Placa'].str.contains('EZU0899')]
                size_df = len(df)

                info = f"Dados da tabela de agendamentos convertidos para DataFrame com sucesso"
                logging.info(info)
                print(info)

                if size_df_original != size_df:
                    info = f"Linhas removidas do DataFrame (Placa EZU0899): {size_df_original - size_df}"
                    logging.info(info)
                    print(info)
            except Exception as e:
                erro = f"Erro ao converter os dados da tabela de agendamentos para DataFrame"
                erros.append(erro)
                erro += f": {e}"
                logging.error(erro)
                print(erro)
                return pedidos, erros

            try:
                for index, row in df.iterrows():
                    id = row['Agendamentos', 'ID']
                    horario = row['Agendamentos', 'Horário']
                    status = row['Agendamentos', 'Status']
                    pedido = f"🆔: {id}, ⏱️: {horario}, 📝: {status}"

                    status_ok = ['Faturado/Carregado', 'Agendamento Liberado']
                    if status not in status_ok: pedidos.append(pedido)

                    print(pedido)
                    logging.info(pedido)
            except Exception as e:
                erro = f"Erro ao percorrer o DataFrame"
                erros.append(erro)
                erro += f": {e}"
                logging.error(erro)
                print(erro)
                return pedidos, erros

        return pedidos, erros


    def scrap_data(self, maximized=False):

        result = {'hoje': [], 'amanha': [], 'erros': []}

        result['erros'] = self.carrega_variaveis()
        if result['erros'] != []: return result

        result['erros'] = self.inicializa_navegador(maximized)
        if result['erros'] != []: return result

        with self.navegador:

            inicio = time()

            try:
                result['erros'] = self.login()
                if result['erros'] != []: return result

                result['hoje'], result['erros'] = self.scrap('hoje')
                if result['erros'] != []: return result

                result['amanha'], result['erros'] = self.scrap('amanhã')
                if result['erros'] != []: return result

                tempo_execucao = f"Tempo de execução da coleta: {round(time() - inicio, 2)} segundos"
                print(tempo_execucao)
                logging.info(tempo_execucao)
            except Exception as e:
                erro = f"Erro ao executar a coleta"
                result['erros'].append(erro)
                erro += f": {e}"
                logging.error(erro)
                print(erro)

        return result



if __name__ == "__main__":

    hora = datetime.now().time()
    hora_inicio = datetime.strptime('01:30', '%H:%M').time()
    hora_fim = datetime.strptime('23:30', '%H:%M').time()

    if hora >= hora_inicio and hora <= hora_fim:
        scraper = AgendamentoIprScraper()
        scraper.scrap_data(maximized=True)
