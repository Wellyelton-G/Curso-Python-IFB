"""Cliente de linha de comando que consome a API da biblioteca (Aula 8).

Mostra o outro lado da API: um programa Python que não sabe nada de Django,
só envia pedidos HTTP e lê as respostas em JSON.

Uso:
    python cliente_api.py                       -> usa http://127.0.0.1:8000/api
    python cliente_api.py https://seunome.pythonanywhere.com/api
"""

import sys
from getpass import getpass  # lê a senha sem mostrá-la na tela

import requests  # biblioteca para fazer pedidos HTTP (pip install requests)

# Endereço base da API: o primeiro argumento da linha de comando ou o servidor local
BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8000/api"


def listar_livros(busca=""):
    """GET /livros/ : lista a primeira página do acervo (não precisa de login)."""
    resposta = requests.get(f"{BASE_URL}/livros/", params={"q": busca}, timeout=10)
    resposta.raise_for_status()  # levanta um erro se o status não for 2xx
    dados = resposta.json()  # o texto JSON vira um dicionário Python
    print(f"\n{dados['count']} livro(s) encontrado(s):")
    for livro in dados["results"]:
        print(f"  [{livro['id']:>3}] {livro['title']} — {livro['author']} ({livro['available']} disponível(is))")


def obter_token(usuario, senha):
    """POST /token/ : troca usuário e senha por um token de acesso."""
    resposta = requests.post(f"{BASE_URL}/token/", data={"username": usuario, "password": senha}, timeout=10)
    if resposta.status_code != 200:
        print("Usuário ou senha incorretos.")
        return None
    return resposta.json()["token"]


def emprestar(token, livro_id):
    """POST /livros/{id}/emprestar/ : empresta um livro para o dono do token."""
    cabecalhos = {"Authorization": f"Token {token}"}  # é assim que a API sabe quem está pedindo
    resposta = requests.post(f"{BASE_URL}/livros/{livro_id}/emprestar/", headers=cabecalhos, timeout=10)
    if resposta.status_code == 201:
        emprestimo = resposta.json()
        print(f"Empréstimo feito: “{emprestimo['book_title']}”, devolver até {emprestimo['due_date']}.")
    elif resposta.status_code == 404:
        print(f"Não existe livro com o id {livro_id}.")
    else:
        # 409 (regra de negócio, como "sem cópias"): a API explica o motivo em "detail"
        print(f"Não foi possível emprestar ({resposta.status_code}): {resposta.json()['detail']}")


def meus_emprestimos(token):
    """GET /emprestimos/ : lista os empréstimos do dono do token."""
    cabecalhos = {"Authorization": f"Token {token}"}
    resposta = requests.get(f"{BASE_URL}/emprestimos/", headers=cabecalhos, timeout=10)
    resposta.raise_for_status()
    print("\nSeus empréstimos:")
    for emprestimo in resposta.json()["results"]:
        situacao = "devolvido" if emprestimo["returned_at"] else "com você"
        print(f"  {emprestimo['book_title']} — até {emprestimo['due_date']} ({situacao})")


def main():
    print(f"API: {BASE_URL}")
    listar_livros(input("Buscar livros (Enter para ver todos): ").strip())

    usuario = input("\nUsuário (Enter para sair): ").strip()
    if not usuario:
        return
    token = obter_token(usuario, getpass("Senha: "))
    if not token:
        return

    livro_id = input("Id do livro para emprestar (Enter para pular): ").strip()
    if livro_id.isdigit():
        emprestar(token, livro_id)
    meus_emprestimos(token)


if __name__ == "__main__":
    main()
