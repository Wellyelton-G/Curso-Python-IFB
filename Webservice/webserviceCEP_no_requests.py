# Exemplo funcional sem instalar dependências externas.

import json                # Para converter texto JSON em estruturas Python (dict/list) e vice‑versa
import socket              # Usado para detectar timeout de conexão de baixo nível
from urllib import request, parse, error
# - request: permite abrir URLs (fazer requisições HTTP)
# - parse: ajuda a montar query strings (ex.: transformar dict em "a=1&b=2")
# - error: contém tipos de exceção específicos para erros de URL/HTTP

def fetch_json(url, timeout=15):
    """
    Faz uma requisição HTTP GET para 'url' e retorna um dict Python com os dados JSON.
    timeout: tempo máximo (segundos) que o Python espera pela resposta.
    Esta função centraliza tratamento de erros para deixar o restante do código mais limpo.
    """
    try:
        # request.urlopen abre a URL e retorna um objeto parecido com um arquivo.
        # usamos 'with' para garantir que a conexão seja fechada automaticamente.
        with request.urlopen(url, timeout=timeout) as resp:
            raw = resp.read()                       # Lê todos os bytes retornados pelo servidor
            text = raw.decode("utf-8")              # Converte bytes para string (UTF-8)
            return json.loads(text)                 # Converte texto JSON em dict Python

    except error.HTTPError as e:
        # HTTPError ocorre quando o servidor responde com código HTTP de erro (ex.: 404, 500).
        # Aqui transformamos a exceção em RuntimeError com mensagem legível.
        raise RuntimeError(f"HTTP error {e.code}: {e.reason}")

    except error.URLError as e:
        # URLError cobre problemas de rede como DNS, conexão recusada, proxy mal configurado, etc.
        # e.reason costuma conter uma descrição (ex.: 'timed out', 'Name or service not known').
        raise RuntimeError(f"Network error: {e.reason}")

    except socket.timeout:
        # Caso o timeout da camada de socket seja atingido.
        raise RuntimeError("Timeout ao conectar")

    except json.JSONDecodeError:
        # O servidor respondeu mas o conteúdo não é JSON válido (ou está truncado).
        raise RuntimeError("Resposta não é JSON válido")


def main():
    # ---------- Exemplo 1: ViaCEP (consulta de endereço por CEP) ----------
    try:
        # URL pública que retorna JSON com dados de endereço para o CEP informado.
        url_cep = "https://viacep.com.br/ws/01001-000/json/"

        # Chama a função que faz a requisição e recebe um dict Python como resposta.
        data = fetch_json(url_cep, timeout=15)

        # Acessa campos do dict com .get para evitar KeyError caso não exista o campo.
        # Imprime logradouro, bairro e estado (uf).
        print("ViaCEP ->", data.get("logradouro"), "-", data.get("bairro"), "| uf:", data.get("uf"))

    except Exception as e:
        # Captura qualquer erro lançado por fetch_json e mostra uma mensagem amigável.
        print("Erro ao consultar ViaCEP:", e)


    # ---------- Exemplo 2: NASA APOD (imagem do dia) ----------
    try:
        # Endpoint público da NASA que retorna dados sobre a imagem do dia.
        base = "https://api.nasa.gov/planetary/apod"

        # Parâmetros da API: aqui usamos a DEMO_KEY (chave pública com limites de uso).
        params = {"api_key": "DEMO_KEY"}

        # Monta a URL com os parâmetros (ex.: "base?api_key=DEMO_KEY")
        url_nasa = base + "?" + parse.urlencode(params)

        # Faz a requisição com timeout maior (algumas APIs podem demorar um pouco)
        data2 = fetch_json(url_nasa, timeout=20)

        # Mostra o título do registro retornado
        print("NASA APOD ->", data2.get("title"))

        # Se a resposta contiver a chave "url" (link da imagem), imprime também.
        if "url" in data2:
            print("  url:", data2.get("url"))

    except Exception as e:
        # Mensagem amigável em caso de falha na consulta à API da NASA
        print("Erro ao consultar NASA APOD:", e)


# Este bloco garante que main() só rode quando este arquivo for executado diretamente.
# Se outro arquivo fizer 'import webserviceCEP_no_requests', main() não será executada automaticamente.
if __name__ == "__main__":
    main()