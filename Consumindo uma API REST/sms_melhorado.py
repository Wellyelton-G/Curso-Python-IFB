
# from twilio.rest import Client
# account_sid = 'AC132fb1dc43156a064e6aa5de63f16520'
# auth_token = '2998992abef279e314d2f9dc696d1da2'
# client = Client(account_sid, auth_token)
# message = client.messages.create(
#   from_='+15076877374',
#   body='Oi Wellyelton',
#   to='+5561999972615'
# )
# print(message.sid)

from twilio.rest import Client
from dotenv import load_dotenv
from pathlib import Path
import os

# Garante que o .env da PASTA DO SCRIPT seja carregado
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR / ".env"
if not ENV_PATH.exists():
    raise FileNotFoundError(f"Arquivo .env não encontrado em: {ENV_PATH}")

load_dotenv(dotenv_path=ENV_PATH, override=True)

# Lê as variáveis
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token  = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_FROM")
to_number   = os.getenv("TO_NUMBER")

# Código didático para enviar um SMS com Twilio. Comentários explicam linha a linha.

from twilio.rest import Client          # Biblioteca oficial da Twilio para enviar mensagens
from dotenv import load_dotenv          # Usada para carregar variáveis de ambiente de um arquivo .env
from pathlib import Path                # Facilita trabalhar com caminhos de arquivo
import os                               # Permite acessar variáveis de ambiente do sistema

# ----- Localiza e carrega o arquivo .env -----
# Garante que o .env que será lido fica na mesma pasta deste script
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR / ".env"

# Se não existir .env na mesma pasta, avisamos e interrompemos o programa
if not ENV_PATH.exists():
    raise FileNotFoundError(f"Arquivo .env não encontrado em: {ENV_PATH}")

# Carrega as variáveis do .env para as variáveis de ambiente do processo
# override=True garante que valores já definidos no ambiente sejam sobrescritos pelo .env (útil durante testes)
load_dotenv(dotenv_path=ENV_PATH, override=True)

# ----- Lê as variáveis necessárias do ambiente -----
# Essas variáveis devem estar definidas no arquivo .env (ou no ambiente do sistema).
# Não coloque chaves/segredos diretamente no código — por isso usamos o .env.
account_sid = os.getenv("TWILIO_ACCOUNT_SID")   # Identificador da conta Twilio (parecido com um "usuário")
auth_token  = os.getenv("TWILIO_AUTH_TOKEN")    # Token secreto usado para autenticar (nunca compartilhar)
from_number = os.getenv("TWILIO_FROM")          # Número Twilio que enviará a mensagem (formato internacional: +55...)
to_number   = os.getenv("TO_NUMBER")            # Número destino que receberá a mensagem

# ----- Validação amigável -----
# Cria uma lista com os nomes das variáveis que estão faltando ou vazias.
missing = [n for n, v in {
    "TWILIO_ACCOUNT_SID": account_sid,
    "TWILIO_AUTH_TOKEN": auth_token,
    "TWILIO_FROM": from_number,
    "TO_NUMBER": to_number,
}.items() if not v]

# Se houver variáveis faltando, interrompe com uma mensagem clara para o usuário.
if missing:
    # join transforma a lista ["A","B"] em "A, B"
    raise RuntimeError("Variáveis ausentes no .env: " + ", ".join(missing))

# ----- Cria o cliente da Twilio -----
# Client faz a comunicação com a API da Twilio usando as credenciais lidas.
client = Client(account_sid, auth_token)

# ----- Envia a mensagem -----
# client.messages.create aciona o envio de SMS.
# Parâmetros principais:
#   from_ : número que envia (número Twilio)
#   to     : número que recebe (destino)
#   body   : texto da mensagem
message = client.messages.create(
    from_=from_number,      # ex.: "+15076877374"    (número fornecido pela Twilio)
    to=to_number,           # ex.: "+55619999...."  (número do destinatário)
    body="Olá estudante do IFB, é uma satisfação ter você aqui, aproveite a jornada."    # Texto da mensagem que será enviada
)

# ----- Resultado -----
# message.sid é um identificador único da mensagem criado pela Twilio.
# Exibir esse valor ajuda a confirmar que o envio foi solicitado com sucesso.
print(message.sid)