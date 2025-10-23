# Atenção: execute os comandos abaixo no terminal para instalar a biblioteca requests
# pip install requests
# python -m pip install requests
# python -m venv .venv
# .venv\Scripts\activate
# python -m pip install requests

import requests

# ----- Consulta ViaCEP (cep -> endereço) -----
try:
    resp = requests.get("https://viacep.com.br/ws/01001-000/json/", timeout=10)
    resp.raise_for_status()                # levanta erro se status >= 400
    data = resp.json()
    print(data.get("logradouro"), "-", data.get("bairro"))
except requests.exceptions.RequestException as e:
    print("Erro ao consultar ViaCEP:", e)

# ----- Consulta NASA APOD (imagem/descrição do dia) -----
try:
    url = "https://api.nasa.gov/planetary/apod"
    params = {"api_key": "DEMO_KEY"}      # DEMO_KEY funciona mas tem limites
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    print(r.status_code, r.headers.get("Content-Type"))
    print(r.json().get("title"))
except requests.exceptions.RequestException as e:
    print("Erro ao consultar NASA APOD:", e)