# Atenção: execute os comandos abaixo no terminal para instalar a biblioteca requests
# pip install requests
# python -m pip install requests
# python -m venv .venv
# .venv\Scripts\activate
# python -m pip install requests

# importa a biblioteca requests, usada para fazer requisições HTTP
import requests

# ----- Consulta ViaCEP (cep -> endereço) -----
try:
    # faz uma requisição HTTP GET para a API ViaCEP para o CEP 01001-000
    # timeout=10 -> se não houver resposta em 10 segundos, a requisição levanta timeout
    resp = requests.get("https://viacep.com.br/ws/01001-000/json/", timeout=10)

    # raise_for_status() verifica o código HTTP da resposta:
    # se for 400 ou maior (erros do cliente/servidor) lança requests.exceptions.HTTPError
    resp.raise_for_status()                # levanta erro se status >= 400

    # converte o corpo da resposta (assumindo JSON) para um dicionário Python
    data = resp.json()

    # imprime o valor do campo "logradouro" e do campo "bairro" do JSON.
    # data.get("chave") retorna None se a chave não existir (evita KeyError)
    print(data.get("logradouro"), "-", data.get("bairro"))

# captura qualquer exceção relacionada a requisições da biblioteca requests
except requests.exceptions.RequestException as e:
    # RequestException é a classe base para erros como ConnectionError, Timeout, HTTPError etc.
    print("Erro ao consultar ViaCEP:", e)

# ----- Consulta NASA APOD (imagem/descrição do dia) -----
try:
    # URL base da API APOD (Astronomy Picture of the Day)
    url = "https://api.nasa.gov/planetary/apod"

    # parâmetros da requisição: chave de API.
    # "DEMO_KEY" é uma chave pública para testes com limites de uso.
    params = {"api_key": "DEMO_KEY"}      # DEMO_KEY funciona mas tem limites

    # faz a requisição GET para a URL com os parâmetros fornecidos
    # requests monta a query string automaticamente a partir de params
    r = requests.get(url, params=params, timeout=10)

    # levanta HTTPError se o status da resposta indicar erro (>=400)
    r.raise_for_status()

    # imprime o código HTTP retornado e o Content-Type do cabeçalho da resposta
    print(r.status_code, r.headers.get("Content-Type"))

    # converte o corpo JSON para dicionário e pega o campo "title"
    # se o JSON não tiver "title", .get retorna None
    print(r.json().get("title"))

# captura exceções relacionadas a requisições (inclui Timeout, HTTPError etc.)
except requests.exceptions.RequestException as e:
    print("Erro ao consultar NASA APOD:", e)