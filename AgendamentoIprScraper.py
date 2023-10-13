from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from time import sleep, time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import pandas as pd
from io import StringIO
import logging
from logging.handlers import TimedRotatingFileHandler


class AgendamentoIprScraper:

    # working_directory = os.getcwd()
    # working_directory = os.path.dirname(os.path.abspath(__file__))
    # log = os.path.join(working_directory, 'scraper.log')
    # env = os.path.join(working_directory, '.env')

    log = 'C:/Users/titrr/Documents/Projetos/monitor_agendamentos/dist/monitora_agendamentos/scraper.log'
    env = 'C:/Users/titrr/Documents/Projetos/monitor_agendamentos/.env'

    def data(self):
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')


    def inicializa_logger(self):
        handler = TimedRotatingFileHandler(self.log, when="D", interval=1, backupCount=2, encoding='utf-8')
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[handler])

        # Ajuste as configurações do handler
        handler.suffix = "%Y%m%d.log"  # Adiciona a data no nome do arquivo
        handler.extMatch = r"^\d{8}\.log$"

        logging.info('') # Linha em branco
        info = f"{self.data()} Iniciando o scraper..."
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
            self.tempo_espera = 30

            # Verifica se as variáveis não são nulas
            if not self.LINK_IPR or not self.LOGIN_IPR or not self.SENHA_IPR or not self.ID_INPUT_LOGIN_IPR or not self.ID_INPUT_SENHA_IPR or not self.XPATH_BUTTON_ENTRAR_IPR or not self.XPATH_BUTTON_RIBPRETO_IPR or not self.XPATH_STATUS_IPR or not self.XPATH_TABLE_AGENDAMENTOS_IPR:
                erro = f"Alguma variável não foi definida"
                raise Exception(erro)

            info = f"{self.data()} Variáveis de ambiente carregadas com sucesso"
            logging.info(info)
            print(info)
            return []
        except Exception as e:
            erro = f"{self.data()} Erro ao carregar as variáveis de ambiente: {e}"
            logging.error(erro)
            print(erro)
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

            info = f"{self.data()} Navegador configurado com sucesso"
            logging.info(info)
            print(info)
            return []
        except Exception as e:
            erro = f"{self.data()} Erro ao configurar o navegador: {e}"
            logging.error(erro)
            print(erro)
            return [erro]


    def login(self):
            try:
                self.navegador.get(self.LINK_IPR)
                WebDriverWait(self.navegador, self.tempo_espera).until(EC.presence_of_element_located((By.ID, self.ID_INPUT_LOGIN_IPR))).send_keys(self.LOGIN_IPR)
                WebDriverWait(self.navegador, self.tempo_espera).until(EC.presence_of_element_located((By.ID, self.ID_INPUT_SENHA_IPR))).send_keys(self.SENHA_IPR)
                WebDriverWait(self.navegador, self.tempo_espera).until(EC.presence_of_element_located((By.XPATH, self.XPATH_BUTTON_ENTRAR_IPR))).click()
                WebDriverWait(self.navegador, self.tempo_espera).until(EC.presence_of_element_located((By.XPATH, self.XPATH_BUTTON_RIBPRETO_IPR))).click()

                info = f"{self.data()} Acesso ao portal da Ipiranga realizado com sucesso"
                logging.info(info)
                print(info)
                return []
            except Exception as e:
                erro = f"{self.data()} Erro ao acessar o portal da Ipiranga: {e}"
                logging.error(erro)
                print(erro)
                return [erro]


    def scrap(self, dia):

        pedidos = []
        erros = []

        if dia == 'amanhã':
            dia_seguinte_msg = f"{self.data()} Coletando agendamentos para amanhã..."
            print(dia_seguinte_msg)
            logging.info(dia_seguinte_msg)

            amanha = datetime.now() + timedelta(days=1)
            WebDriverWait(self.navegador, self.tempo_espera).until(EC.presence_of_element_located((By.XPATH, self.XPATH_BUTTON_CALENDARIO_IPR))).click()
            WebDriverWait(self.navegador, self.tempo_espera).until(EC.presence_of_element_located((By.XPATH, f'//td[text()="{amanha.day}"]'))).click()
            sleep(2)

        try:
            sleep(2)
            elements = self.navegador.find_elements(By.XPATH, self.XPATH_STATUS_IPR)

            info = f"{self.data()} Quantidade de elementos de atualização de status: {len(elements)}"
            logging.info(info)
            print(info)
        except Exception as e:
            erro = f"{self.data()} Erro ao encontrar os elementos de atualização de status: {e}"
            logging.error(erro)
            print(erro)
            erros.append(erro)
            return pedidos, erros

        if elements == []:
            print(f"{self.data()} Não há agendamentos disponíveis para {dia}")
        else:
            try:
                contador = 0
                for element in elements:
                    element.click()
                    contador += 1
                    sleep(2)

                info = f"{self.data()} Elementos de atualização de status clicados com sucesso. Quantidade: {contador}"
                logging.info(info)
                print(info)
            except Exception as e:
                erro = f"{self.data()} Erro ao clicar nos elementos de atualização de status: {e}"
                logging.error(erro)
                print(erro)
                erros.append(erro)
                return pedidos, erros

            try:
                table = self.navegador.find_element(By.XPATH, self.XPATH_TABLE_AGENDAMENTOS_IPR)
                html_string = table.get_attribute('outerHTML')
                html_io = StringIO(html_string)

                info = f"{self.data()} Dados da tabela de agendamentos coletados com sucesso"
                logging.info(info)
                print(info)
            except Exception as e:
                erro = f"{self.data()} Erro ao coletar os dados da tabela de agendamentos: {e}"
                logging.error(erro)
                print(erro)
                erros.append(erro)
                return pedidos, erros

            try:
                df = pd.read_html(html_io)[0]
                df.drop([('Agendamentos', 'Unnamed: 0_level_1'), ('Agendamentos', 'Confirmado')], axis=1, inplace=True)

                size_df_original = len(df)
                df = df[df['Agendamentos', 'Placa'] != 'EZU0899']
                size_df = len(df)

                info = f"{self.data()} Dados da tabela de agendamentos convertidos para DataFrame com sucesso"
                logging.info(info)
                print(info)

                if size_df_original != size_df:
                    info = f"{self.data()} Linhas removidas do DataFrame (Placa EZU0899): {size_df_original - size_df}"
                    logging.info(info)
                    print(info)
            except Exception as e:
                erro = f"{self.data()} Erro ao converter os dados da tabela de agendamentos para DataFrame: {e}"
                logging.error(erro)
                print(erro)
                erros.append(erro)
                return pedidos, erros

            try:
                for index, row in df.iterrows():
                    id = row['Agendamentos', 'ID']
                    horario = row['Agendamentos', 'Horário']
                    status = row['Agendamentos', 'Status']

                    pedido = f"🆔: {id}, ⏱️: {horario}, 📝: {status}"
                    pedidos.append(pedido)
                    print(pedido)
                    logging.info(pedido)
            except Exception as e:
                erro = f"{self.data()} Erro ao percorrer o DataFrame: {e}"
                logging.error(erro)
                print(erro)
                erros.append(erro)
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

                tempo_execucao = f"{self.data()} Tempo de execução da coleta: {round(time() - inicio, 2)} segundos"
                print(tempo_execucao)
                logging.info(tempo_execucao)
            except Exception as e:
                erro = f"{self.data()} Erro ao executar a coleta: {e}"
                logging.error(erro)
                print(erro)
                result['erros'].append(erro)

        return result



if __name__ == "__main__":

    scraper = AgendamentoIprScraper()
    scraper.inicializa_logger()
    scraper.scrap_data(maximized=True)
