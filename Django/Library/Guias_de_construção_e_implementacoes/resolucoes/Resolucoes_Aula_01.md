# Resoluções — Aula 1

[Voltar à lista de resoluções](README.md) · [Guia da Aula 1](../Aula_01_Fundamentos_Modelos_e_Admin.md)

Ponto de partida: projeto ao final da Aula 1 (`gabarito/aula_01`).

---

## Exercício 1 — Filtro por autor no Admin

> Acrescente a linha `list_filter = ("author",)` ao `BookAdmin`. O que muda na tela?

**Arquivo:** `catalog/admin.py` · **Ação:** acrescentar uma linha ao `BookAdmin`

```python
    search_fields = ("title", "author", "isbn")
    # Exercício 1: filtro lateral com a lista de autores cadastrados
    list_filter = ("author",)
```

**O que muda:** aparece, à direita da lista de livros, o painel **Filtro** com a opção **Por Autor(a)** e um link para cada autor cadastrado. Clicar num autor mostra só os livros dele; a URL ganha algo como `?author=Machado+de+Assis`.

Observação para a discussão em sala: a vírgula em `("author",)` é obrigatória. Sem ela, `("author")` é só um texto entre parênteses, não uma tupla, e o Django reclama que `list_filter` precisa ser uma lista ou tupla.

---

## Exercício 2 — Livros com mais de uma cópia

> No shell, liste só os livros com mais de uma cópia.

```python
from catalog.models import Book

# __gt significa "maior que" (greater than)
Book.objects.filter(copies_total__gt=1)
```

Variações que valem a pena mostrar: `__gte` (maior ou igual), `__lt` (menor que) e `__lte` (menor ou igual).

---

## Exercício 3 — Empréstimos ativos

> No shell, descubra quantos empréstimos ativos existem no sistema.

```python
from catalog.models import Loan

# Ativo = ainda não devolvido = returned_at vazio (NULL)
Loan.objects.filter(returned_at__isnull=True).count()
```

O `.count()` faz a contagem **no banco** (`SELECT COUNT(*)`), sem trazer os empréstimos para o Python. É bem mais eficiente do que `len(Loan.objects.filter(...))`.

---

## Exercício 4 (desafio) — Campo `pages`

> Adicione ao `Book` o campo opcional `pages` (número de páginas).

**Arquivo:** `catalog/models.py` · **Ação:** acrescentar o campo na classe `Book`, logo abaixo de `created_at`

```python
    created_at = models.DateTimeField("Cadastrado em", auto_now_add=True)  # preenchido sozinho na criação
    # Exercício 4: opcional (null/blank) para não exigir valor dos livros já cadastrados
    pages = models.PositiveIntegerField("Páginas", null=True, blank=True)
```

Depois:

```powershell
python manage.py makemigrations
python manage.py migrate
```

O `makemigrations` mostra `+ Add field pages to book`. No Admin, o formulário do livro ganha o campo **Páginas**, que pode ficar em branco.

**Ponto de atenção:** se o campo fosse obrigatório (sem `null=True`), o `makemigrations` perguntaria que valor dar aos livros já cadastrados. Esse assunto é aprofundado na Aula 4.
