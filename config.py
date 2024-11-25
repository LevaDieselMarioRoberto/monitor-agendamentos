import os
from getpass import getuser
from dotenv import load_dotenv

user = getuser()

BASE_DIR = f"C:/Users/{user}/Documents/Projetos/monitor_agendamentos/"

ARQUIVO_JSON_PEDIDOS = BASE_DIR + "dist/pedidos.json"
ARQUIVO_LOG = BASE_DIR + "dist/monitor.log"
ARQUIVO_ENV = BASE_DIR + ".env" # Necessário ser explícito para execução de tarefa automática do Windows

load_dotenv(ARQUIVO_ENV)

TELEGRAM_CONFIG = {
    'TOKEN': os.getenv('TOKEN'),
    'IDCHAT': os.getenv('IDCHAT'),
}

VAR = {
    'link': os.getenv("LINK_IPR"),
    'login': os.getenv("LOGIN_IPR"),
    'senha': os.getenv("SENHA_IPR"),
    'link_filial_rp': os.getenv("LINK_FILIAL_RIBEIRAO"),
    'id_input_login': os.getenv("ID_INPUT_LOGIN_IPR"),
    'id_input_senha': os.getenv("ID_INPUT_SENHA_IPR"),
    'xpath_button_entrar': os.getenv("XPATH_BUTTON_ENTRAR_IPR"),
    'xpath_button_ribpreto': os.getenv("XPATH_BUTTON_RIBPRETO_IPR"),
    'xpath_button_calendario': os.getenv("XPATH_BUTTON_CALENDARIO_IPR"),
    'xpath_status': os.getenv("XPATH_STATUS_IPR"),
    'xpath_table_agendamentos': os.getenv("XPATH_TABLE_AGENDAMENTOS_IPR"),
    'xpath_button_calendario_nextmonth': os.getenv("XPATH_BUTTON_CALENDARIO_NEXTMONTH"),
    'xpath_input_calendario': os.getenv("XPATH_BUTTON_CALENDARIO"),
    'xpath_calendario': os.getenv("XPATH_CALENDARIO")
}
