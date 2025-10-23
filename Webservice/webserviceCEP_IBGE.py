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

# Função auxiliar para obter a lista completa de estados do IBGE.
# Colocamos em função para poder reutilizar fácil em outros pontos do código.
def fetch_ibge_states(timeout=10):
    """
    Retorna a lista completa de estados do IBGE (lista de dicts).
    Lança requests.exceptions.RequestException em caso de erro de rede/HTTP,
    ou ValueError/JSONDecodeError se a resposta não for JSON válido.
    """
    # endpoint público do IBGE que lista estados
    url_ibge = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    # faz a requisição e retorna a lista decodificada (requests.json() já lança se inválido)
    r = requests.get(url_ibge, timeout=timeout)
    r.raise_for_status()
    return r.json()

# ----- Consulta NASA APOD (imagem/descrição do dia) -----
# Substituição/ajuste: a DEMO_KEY da NASA frequentemente retorna 429 (Too Many Requests)
# em ambientes de ensino onde várias pessoas ou execuções usam a mesma chave.
# Aqui implementamos:
# 1) tentativa da API NASA com DEMO_KEY;
# 2) se receber 429 (ou outro erro HTTP específico), registramos e tentamos um "fallback"
#    para uma API pública alternativa do governo brasileiro (IBGE) que não exige chave e
#    retorna JSON. Isso mantém o exemplo funcional em sala de aula sem exigir chave.
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
except requests.exceptions.HTTPError as e:
    # Se o erro HTTP for 429 (Too Many Requests), é muito provável que a DEMO_KEY tenha atingido limite.
    status = None
    if e.response is not None:
        status = e.response.status_code
    # Mensagem breve sobre a causa mais comum do 429
    if status == 429:
        print("Erro ao consultar NASA APOD: 429 Too Many Requests — DEMO_KEY atingiu limite.")
        print("Tentando fallback para uma API pública alternativa do governo brasileiro (IBGE)...")

        # Fallback: usamos a função fetch_ibge_states() para obter a lista completa de estados.
        try:
            # obtém lista completa de estados do IBGE (cada item é um dict com 'id','sigla','nome','regiao',...)
            states = fetch_ibge_states(timeout=10)

            # Mostra quantos estados foram retornados (esperado: 27)
            print("Fallback (IBGE) -> estados retornados:", len(states))

            # Exibe a lista completa de estados em formato "SIGLA - Nome" (ordenada por sigla para consistência)
            # Comentário: ordenamos por 'sigla' para saída previsível independentemente da ordem do IBGE.
            states_sorted = sorted(states, key=lambda s: s.get("sigla") or "")
            for s in states_sorted:
                # uso de .get para evitar KeyError caso alguma chave esteja ausente
                print(f"  {s.get('sigla')} - {s.get('nome')}")

            # Se quiser usar programaticamente, criamos um dicionário mapeando sigla -> nome
            sigla_para_nome = {s.get("sigla"): s.get("nome") for s in states_sorted if s.get("sigla")}

            # Exemplo de uso do dicionário: buscar o nome do estado pela sigla
            exemplo_sigla = "SP"
            print(f"Exemplo de lookup: {exemplo_sigla} ->", sigla_para_nome.get(exemplo_sigla, "não encontrado"))

            # Agora 'states' e 'sigla_para_nome' podem ser usados nas próximas etapas do programa,
            # por exemplo para preencher menus, validar entradas de usuário, etc.

        except requests.exceptions.HTTPError as e2:
            # Erro HTTP do IBGE (pou provável, mas tratado)
            print("Fallback IBGE falhou com HTTPError:", e2)
        except requests.exceptions.RequestException as e2:
            # Erros de rede/timeout ao acessar IBGE
            print("Fallback IBGE falhou (erro de requisição):", e2)
        except ValueError:
            # json() pode lançar ValueError/JSONDecodeError se o corpo não for JSON válido
            print("Fallback IBGE retornou JSON inválido")
    else:
        # Para outros HTTPError, mostramos a mensagem original.
        print("Erro ao consultar NASA APOD:", e)

except requests.exceptions.RequestException as e:
    # Captura outros erros de requisição (Timeout, ConnectionError etc.)
    print("Erro ao consultar NASA APOD:", e)