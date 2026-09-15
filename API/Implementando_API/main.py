from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

# ============================================================
# CRIAÇÃO DA APLICAÇÃO
# ============================================================

app = FastAPI(
    title="API de Livros",
    description="API REST desenvolvida com FastAPI para fins didáticos.",
    version="1.0.0"
)


# ============================================================
# MODELO DE DADOS
# ============================================================

class Livro(BaseModel):
    titulo: str
    autor: str


# ============================================================
# DADOS INICIAIS
# ============================================================

livros = [
    {
        "id": 1,
        "titulo": "Dom Casmurro",
        "autor": "Machado de Assis"
    },
    {
        "id": 2,
        "titulo": "O Cortiço",
        "autor": "Aluísio Azevedo"
    },
    {
        "id": 3,
        "titulo": "Vidas Secas",
        "autor": "Graciliano Ramos"
    }
]


# ============================================================
# ROTA INICIAL
# ============================================================

@app.get("/")
def inicio():
    return {
        "mensagem": "Bem-vindo à API de Livros",
        "documentacao": "/docs"
    }


# ============================================================
# GET - LISTAR TODOS OS LIVROS
# ============================================================

@app.get("/livros")
def listar_livros():
    return livros


# ============================================================
# GET - BUSCAR UM LIVRO PELO ID
# ============================================================

@app.get("/livros/{livro_id}")
def buscar_livro(livro_id: int):

    for livro in livros:
        if livro["id"] == livro_id:
            return livro

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Livro não encontrado"
    )


# ============================================================
# POST - CADASTRAR UM NOVO LIVRO
# ============================================================

@app.post(
    "/livros",
    status_code=status.HTTP_201_CREATED
)
def cadastrar_livro(livro: Livro):

    novo_id = 1

    if livros:
        novo_id = max(item["id"] for item in livros) + 1

    novo_livro = {
        "id": novo_id,
        "titulo": livro.titulo,
        "autor": livro.autor
    }

    livros.append(novo_livro)

    return novo_livro


# ============================================================
# PUT - ATUALIZAR UM LIVRO COMPLETAMENTE
# ============================================================

@app.put("/livros/{livro_id}")
def atualizar_livro(
    livro_id: int,
    livro_atualizado: Livro
):

    for livro in livros:

        if livro["id"] == livro_id:

            livro["titulo"] = livro_atualizado.titulo
            livro["autor"] = livro_atualizado.autor

            return livro

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Livro não encontrado"
    )


# ============================================================
# DELETE - EXCLUIR UM LIVRO
# ============================================================

@app.delete("/livros/{livro_id}")
def excluir_livro(livro_id: int):

    for livro in livros:

        if livro["id"] == livro_id:

            livros.remove(livro)

            return {
                "mensagem": "Livro excluído com sucesso"
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Livro não encontrado"
    )