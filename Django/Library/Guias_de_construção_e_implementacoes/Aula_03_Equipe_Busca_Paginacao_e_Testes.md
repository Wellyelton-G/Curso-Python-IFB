# Aula 3 — Área da equipe, busca, paginação e testes

Sistema de Biblioteca com Django · Aula 3 de 10 · [Roteiro do curso](README.md)

## Objetivos da aula

- Diferenciar **autenticação** (quem é você?) de **autorização** (o que você pode fazer?).
- Criar a **área da equipe**: empréstimos atrasados, "com quem está este livro?" e registro de devolução.
- Escrever um **decorator** próprio, o `staff_required`.
- Acrescentar ao acervo **busca**, filtro **"somente disponíveis"** e **paginação**.
- Deixar as consultas mais eficientes com **`annotate`**.
- Escrever **testes automatizados**, que conferem o sistema em segundos.

Ao final da aula, a equipe tem páginas próprias, o acervo tem busca e paginação, e o comando `python manage.py test` verifica 14 comportamentos do sistema.

| Aula 1 | Aula 2 | Aula 3 | Aula 4 | Aula 5 | Aula 6 | Aula 7 | Aula 8 | Aula 9 | Aula 10 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Concluída | Concluída | **Aula atual** | Categorias e exportação | Contas e avaliações | Relatórios e banco | Publicação | API REST | Qualidade de código | Git em equipe |

## Antes de começar

- [ ] Ambiente virtual ativo e `python manage.py check` sem erros.
- [ ] Login, acervo, emprestar e devolver (Aula 2) funcionando.

---

## Parte 1 — Conceitos

### 1.1 Autenticação e autorização

| | Pergunta | No Django |
|---|---|---|
| **Autenticação** | Quem é você? | login e senha; na view, `@login_required` |
| **Autorização** | O que você pode fazer? | por exemplo, `user.is_staff` (faz parte da equipe?) |

Quem **não está logado** é mandado para o login. Quem **está logado mas não tem permissão** recebe **403 Forbidden**. Mandar essa pessoa para o login não faria sentido, porque ela já entrou.

### 1.2 O problema das N+1 consultas

Na Aula 2, o acervo mostra `book.copies_available` para cada livro, e essa `@property` faz uma consulta ao banco **por livro**. Com 20 livros na tela são 21 consultas; com 1000 livros, 1001.

A solução é pedir ao banco que calcule tudo de uma vez, com `annotate`:

```python
# Cada livro já vem do banco com o campo extra "available", numa única consulta
Book.objects.annotate(
    available=F("copies_total") - Count("loans", filter=Q(loans__returned_at__isnull=True))
)
```

| Peça | Significado |
|---|---|
| `annotate(nome=...)` | acrescenta a cada resultado um campo calculado chamado `nome` |
| `Count("loans", filter=...)` | conta os empréstimos do livro que atendem ao filtro |
| `Q(...)` | uma condição que pode ser combinada: `Q(a) \| Q(b)` é OU, `Q(a) & Q(b)` é E |
| `F("copies_total")` | o valor da coluna `copies_total` da própria linha, usado dentro do banco |

### 1.3 Paginação

Ninguém quer rolar mil livros numa página só. O **`Paginator`** divide a lista em páginas, e a página atual vem pela URL: `/?page=2`.

O cuidado é **não perder os filtros ao trocar de página**: `/?q=machado&page=2` precisa manter o `q=machado`. O template tag `{% querystring page=2 %}` (Django 5.1 ou mais novo) resolve isso: copia os parâmetros atuais da URL e troca só o `page`.

### 1.4 Por que testes automatizados

A cada aula o sistema cresce, e conferir tudo clicando fica inviável. Um **teste automatizado** é um trecho de código que usa o sistema e verifica o resultado. Todo teste segue o roteiro prepara → age → verifica:

```python
def test_nao_empresta_sem_copias(self):
    ...  # prepara: um livro com 1 cópia, já emprestada para outra pessoa
    ...  # age: a Maria tenta emprestar
    ...  # verifica: nenhum empréstimo novo foi criado para a Maria
```

O Django cria um **banco de testes separado e vazio** a cada execução, então os dados reais nunca são tocados. Se uma mudança futura quebrar uma regra antiga, o teste avisa na hora.

---

## Parte 2 — Área da equipe e busca

### Passo 1 — As views

Nesta aula vamos criar o decorator `staff_required`, reescrever a `book_list` (busca, filtro e paginação) e adicionar três views da equipe. As views `borrow_book`, `my_loans` e `return_book` continuam iguais.

**Arquivo:** `catalog/views.py` · **Ação:** substituir todo o conteúdo

```python
from datetime import timedelta  # representa um intervalo de tempo (ex.: 14 dias)
from functools import wraps  # ajuda a escrever decorators

from django.contrib import messages  # mensagens de retorno ("Empréstimo feito!")
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied  # gera a resposta 403 (proibido)
from django.core.paginator import Paginator  # divide listas em páginas
from django.db.models import Count, F, Q  # ferramentas para montar consultas
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Book, Loan

LOAN_DAYS = 14  # prazo padrão de empréstimo, em dias
BOOKS_PER_PAGE = 10  # quantos livros aparecem por página


def staff_required(view):
    """Decorator: só deixa passar quem está logado E faz parte da equipe."""

    @wraps(view)  # mantém o nome e a documentação da view original
    @login_required  # primeiro exige login
    def wrapper(request, *args, **kwargs):
        # Logado, mas não é da equipe: resposta 403 ("proibido")
        if not request.user.is_staff:
            raise PermissionDenied
        # Tudo certo: executa a view original com os mesmos argumentos
        return view(request, *args, **kwargs)

    return wrapper  # a função "embrulhada" passa a ocupar o lugar da view


@login_required
def book_list(request):
    """Lista o acervo com busca, filtro de disponibilidade e paginação."""
    # 1) Consulta base: cada livro já vem com o campo calculado "available" (cópias disponíveis).
    #    Count conta os empréstimos ainda não devolvidos; F("copies_total") é o valor da coluna.
    books = Book.objects.annotate(
        available=F("copies_total") - Count("loans", filter=Q(loans__returned_at__isnull=True))
    ).order_by("title")

    # 2) Busca por texto: /?q=machado
    q = request.GET.get("q", "").strip()  # "" se o parâmetro não vier; strip tira espaços das pontas
    if q:
        # Q permite combinar condições com | (OU): título OU autor OU ISBN contém o texto
        books = books.filter(
            Q(title__icontains=q) | Q(author__icontains=q) | Q(isbn__icontains=q)
        )

    # 3) Somente disponíveis: /?disponivel=1
    only_available = request.GET.get("disponivel") == "1"
    if only_available:
        books = books.filter(available__gt=0)  # __gt significa "maior que"

    # 4) Paginação: /?page=2
    paginator = Paginator(books, BOOKS_PER_PAGE)
    # get_page aceita número inválido sem erro (vai para a primeira ou para a última página)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,  # só os livros da página atual
        "q": q,  # para o campo de busca mostrar o que foi digitado
        "only_available": only_available,  # para a caixa de seleção continuar marcada
    }
    return render(request, "catalog/book_list.html", context)


@login_required
@require_POST  # recusa pedidos GET com erro 405: emprestar só por formulário
def borrow_book(request, book_id):
    """Cria um empréstimo do livro para o usuário logado."""
    # Busca o livro pelo id; se não existir, responde 404 (página não encontrada)
    book = get_object_or_404(Book, pk=book_id)

    # Regra 1: precisa haver cópia disponível
    if book.copies_available == 0:
        messages.error(request, f"Não há cópias disponíveis de “{book.title}”.")
        return redirect("catalog:book_list")

    # Regra 2: a pessoa não pode estar com este mesmo livro ainda sem devolver
    already_has = book.loans.filter(user=request.user, returned_at__isnull=True).exists()
    if already_has:
        messages.warning(request, f"Você já está com “{book.title}”.")
        return redirect("catalog:book_list")

    # Tudo certo: calcula o prazo e cria o empréstimo
    due_date = timezone.localdate() + timedelta(days=LOAN_DAYS)
    Loan.objects.create(book=book, user=request.user, due_date=due_date)
    messages.success(request, f"Empréstimo feito! Devolva “{book.title}” até {due_date:%d/%m/%Y}.")
    # Depois de um POST, sempre redirecionamos (padrão Post/Redirect/Get)
    return redirect("catalog:my_loans")


@login_required
def my_loans(request):
    """Lista os empréstimos do usuário logado (ativos e devolvidos)."""
    # select_related("book") traz o livro na mesma consulta, evitando uma consulta extra por empréstimo
    loans = Loan.objects.filter(user=request.user).select_related("book")
    return render(request, "catalog/my_loans.html", {"loans": loans})


@login_required
@require_POST
def return_book(request, loan_id):
    """Registra a devolução de um empréstimo do próprio usuário."""
    # user=request.user impede devolver o empréstimo de outra pessoa trocando o número na URL
    loan = get_object_or_404(Loan, pk=loan_id, user=request.user)

    if loan.returned_at:
        messages.info(request, "Este livro já tinha sido devolvido.")
    else:
        loan.mark_returned()  # regra de negócio que fica no model
        messages.success(request, f"“{loan.book.title}” devolvido. Obrigado!")
    return redirect("catalog:my_loans")


# ---------- Área da equipe (staff) ----------


@staff_required
def overdue_loans(request):
    """Empréstimos ativos cujo prazo já venceu, do mais antigo para o mais novo."""
    # Duas condições separadas por vírgula valem juntas (E):
    # ainda não devolvido E prazo menor que hoje (__lt significa "menor que")
    loans = (
        Loan.objects.filter(returned_at__isnull=True, due_date__lt=timezone.localdate())
        .select_related("book", "user")  # traz livro e usuário na mesma consulta
        .order_by("due_date")
    )
    return render(request, "catalog/overdue_loans.html", {"loans": loans})


@staff_required
def book_borrowers(request, book_id):
    """Quem está com um determinado livro neste momento."""
    book = get_object_or_404(Book, pk=book_id)
    loans = book.loans.filter(returned_at__isnull=True).select_related("user")
    return render(request, "catalog/book_borrowers.html", {"book": book, "loans": loans})


@staff_required
@require_POST
def staff_mark_returned(request, loan_id):
    """A equipe registra a devolução de qualquer empréstimo."""
    # Aqui não filtramos por usuário: a equipe pode devolver o empréstimo de qualquer leitor
    loan = get_object_or_404(Loan, pk=loan_id)
    if loan.is_active:
        loan.mark_returned()
        messages.success(request, f"Devolução de “{loan.book.title}” ({loan.user}) registrada.")
    return redirect("catalog:overdue_loans")
```

#### Entendendo o código: o decorator `staff_required`

Um decorator é uma função que recebe uma função e devolve outra, que "embrulha" a original. Escrever:

```python
@staff_required
def overdue_loans(request):
    ...
```

é o mesmo que escrever `overdue_loans = staff_required(overdue_loans)`. O nosso decorator:

1. recebe a view original (`view`);
2. cria a função `wrapper`, que exige login (por causa do `@login_required` aplicado a ela), confere `is_staff` e, se a pessoa não for da equipe, levanta `PermissionDenied` (o Django responde 403);
3. se estiver tudo certo, chama a view original repassando todos os argumentos com `*args, **kwargs` (por exemplo, o `book_id`).

O `@wraps(view)` copia o nome e a docstring da view original para o `wrapper`, o que deixa as mensagens de erro mais claras.

A regra "só a equipe" foi escrita uma vez e aplicada a três views. Se ela mudar, a alteração é feita num lugar só.

#### Entendendo o código: a nova `book_list`

A consulta é montada em etapas, e cada filtro só entra se tiver sido pedido. Como os QuerySets são preguiçosos, nada vai ao banco até o fim, e o Django junta tudo numa consulta só.

| Etapa | Código | Explicação |
|---|---|---|
| Ler da URL | `request.GET.get("q", "")` | `request.GET` funciona como um dicionário com os parâmetros da URL |
| Limpar | `.strip()` | `"  machado "` vira `"machado"` |
| Buscar | `title__icontains=q` | "o título contém `q`", sem diferenciar maiúsculas |
| Combinar | `Q(...) \| Q(...) \| Q(...)` | título OU autor OU ISBN |
| Filtrar pelo cálculo | `available__gt=0` | dá para filtrar pelo campo criado no `annotate` |
| Paginar | `paginator.get_page(...)` | `?page=abc` vai para a página 1 e `?page=999` vai para a última |

A view agora envia ao template um `page_obj`, que contém só os livros da página atual e sabe informar `has_next`, `number`, `paginator.num_pages` etc.

#### Entendendo o código: as views da equipe

- **`overdue_loans`** combina duas condições no mesmo `filter`: ainda não devolvido **e** prazo anterior a hoje.
- **`staff_mark_returned`**, ao contrário do `return_book` do leitor, não filtra por `user=request.user`: a equipe pode registrar a devolução de qualquer empréstimo. Autorização é exatamente isso, definir quem pode fazer o quê.

### Passo 2 — URLs

**Arquivo:** `catalog/urls.py` · **Ação:** substituir todo o conteúdo

```python
from django.urls import path

from . import views

# Namespace do app: nos templates escrevemos {% url 'catalog:book_list' %}
app_name = "catalog"

urlpatterns = [
    # Página inicial: lista de livros
    path("", views.book_list, name="book_list"),
    # <int:book_id> captura um número da URL e entrega para a view como book_id
    path("livros/<int:book_id>/emprestar/", views.borrow_book, name="borrow_book"),
    path("emprestimos/", views.my_loans, name="my_loans"),
    path("emprestimos/<int:loan_id>/devolver/", views.return_book, name="return_book"),
    # Área da equipe (prefixo "equipe/" para não colidir com o "admin/" do Django)
    path("equipe/atrasados/", views.overdue_loans, name="overdue_loans"),
    path("equipe/livros/<int:book_id>/leitores/", views.book_borrowers, name="book_borrowers"),
    path("equipe/emprestimos/<int:loan_id>/devolver/", views.staff_mark_returned, name="staff_mark_returned"),
]
```

### Passo 3 — Link "Atrasados" no menu

**Arquivo:** `templates/base.html` · **Ação:** alterar um trecho

Localize:

```html
        {% if user.is_staff %}
          <a href="{% url 'admin:index' %}">Admin</a>
        {% endif %}
```

E troque por:

```html
        {% if user.is_staff %}
          <a href="{% url 'catalog:overdue_loans' %}">Atrasados</a>
          <a href="{% url 'admin:index' %}">Admin</a>
        {% endif %}
```

Esconder o link não protege a página, porque qualquer um pode digitar `/equipe/atrasados/` no navegador. Quem protege é o `@staff_required` na view. O `{% if %}` do menu apenas evita mostrar um link inútil.

### Passo 4 — O acervo com busca e paginação

**Arquivo:** `templates/catalog/book_list.html` · **Ação:** substituir todo o conteúdo

```html
{% extends "base.html" %}
{% block title %}Livros · Biblioteca{% endblock %}
{% block content %}
  <h1>Acervo</h1>

  {# Formulário de busca. É GET: os filtros vão para a URL e não precisam de csrf_token. #}
  <form class="card" method="get">
    <div class="form-grid">
      <div>
        <label for="q">Buscar por título, autor ou ISBN</label>
        {# name="q" precisa ser igual ao nome lido na view: request.GET.get("q") #}
        {# value="{{ q }}" faz o campo continuar mostrando o que foi pesquisado #}
        <input id="q" type="text" name="q" value="{{ q }}" placeholder="Ex.: Machado">
      </div>
    </div>
    <div class="actions">
      <label>
        <input type="checkbox" name="disponivel" value="1" {% if only_available %}checked{% endif %}>
        Somente com cópias disponíveis
      </label>
      <button class="btn btn-primary" type="submit">Filtrar</button>
      {# Limpar é só um link para a página sem nenhum parâmetro #}
      <a class="btn" href="{% url 'catalog:book_list' %}">Limpar</a>
    </div>
  </form>

  {# paginator.count é o total de livros encontrados (em todas as páginas) #}
  <p class="muted">{{ page_obj.paginator.count }} livro(s) encontrado(s).</p>

  {# Tabela com os livros da página atual #}
  {% if page_obj %}
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Capa</th>
            <th>Título</th>
            <th>Autor(a)</th>
            <th>Disponíveis</th>
            <th>Ação</th>
          </tr>
        </thead>
        <tbody>
          {% for book in page_obj %}
            <tr>
              <td>
                {% if book.image %}
                  <img class="cover" src="{{ book.image.url }}" alt="Capa de {{ book.title }}">
                {% else %}
                  <div class="cover">sem capa</div>
                {% endif %}
              </td>
              <td>{{ book.title }}</td>
              <td>{{ book.author }}</td>
              {# book.available vem do annotate da view: não faz consulta extra #}
              <td>{{ book.available }} de {{ book.copies_total }}</td>
              <td>
                {% if book.available > 0 %}
                  <form class="inline" method="post" action="{% url 'catalog:borrow_book' book.id %}">
                    {% csrf_token %}
                    <button class="btn btn-primary" type="submit">Emprestar</button>
                  </form>
                {% else %}
                  <button class="btn" disabled>Indisponível</button>
                {% endif %}
                {# Atalho visível apenas para a equipe #}
                {% if user.is_staff %}
                  <a class="btn" href="{% url 'catalog:book_borrowers' book.id %}">Com quem está?</a>
                {% endif %}
              </td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>

    {# Navegação entre páginas (só aparece se houver mais de uma) #}
    {% if page_obj.paginator.num_pages > 1 %}
      <div class="actions">
        {# querystring copia os parâmetros atuais da URL (q, disponivel) e troca só o page #}
        {% if page_obj.has_previous %}
          <a class="btn" href="{% querystring page=page_obj.previous_page_number %}">« Anterior</a>
        {% endif %}
        <span>Página {{ page_obj.number }} de {{ page_obj.paginator.num_pages }}</span>
        {% if page_obj.has_next %}
          <a class="btn" href="{% querystring page=page_obj.next_page_number %}">Próxima »</a>
        {% endif %}
      </div>
    {% endif %}
  {% else %}
    <p class="muted">Nenhum livro encontrado.</p>
  {% endif %}
{% endblock %}
```

#### Entendendo o código

- O formulário de busca usa **GET**, porque buscar não altera nada. Por isso não precisa de `{% csrf_token %}`, e o resultado é uma URL que pode ser salva ou compartilhada: `/?q=machado&disponivel=1`.
- O `name` de cada campo vira o nome do parâmetro na URL. **O `name` do HTML precisa ser igual ao nome lido na view.**
- `value="{{ q }}"` e o `checked` fazem o formulário lembrar o que foi pesquisado.
- A tabela percorre o `page_obj` e usa `book.available`, o campo calculado no `annotate`. Resultado: uma consulta para a página inteira.

### Passo 5 — Página "Empréstimos atrasados"

**Arquivo:** `templates/catalog/overdue_loans.html` · **Ação:** criar

```html
{% extends "base.html" %}
{% block title %}Atrasados · Biblioteca{% endblock %}
{% block content %}
  <h1>Empréstimos atrasados</h1>

  {% if loans %}
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Livro</th>
            <th>Leitor(a)</th>
            <th>Devolver até</th>
            <th>Tempo de atraso</th>
            <th>Ação</th>
          </tr>
        </thead>
        <tbody>
          {% for loan in loans %}
            <tr>
              <td>{{ loan.book.title }}</td>
              <td>{{ loan.user.username }}</td>
              <td class="danger">{{ loan.due_date|date:"d/m/Y" }}</td>
              {# timesince calcula quanto tempo passou desde o prazo ("3 dias", "1 semana") #}
              <td>{{ loan.due_date|timesince }}</td>
              <td>
                {# Ação da equipe: devolve o empréstimo de qualquer leitor #}
                <form class="inline" method="post" action="{% url 'catalog:staff_mark_returned' loan.id %}">
                  {% csrf_token %}
                  <button class="btn" type="submit">Registrar devolução</button>
                </form>
              </td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  {% else %}
    <p class="success">Nenhum empréstimo atrasado.</p>
  {% endif %}
{% endblock %}
```

### Passo 6 — Página "Com quem está?"

**Arquivo:** `templates/catalog/book_borrowers.html` · **Ação:** criar

```html
{% extends "base.html" %}
{% block title %}Com quem está · Biblioteca{% endblock %}
{% block content %}
  <h1>Com quem está “{{ book.title }}”?</h1>
  <p class="muted">{{ book.author }} · {{ book.copies_available }} de {{ book.copies_total }} cópia(s) na estante</p>

  {# loans contém só os empréstimos ativos deste livro (filtrados na view) #}
  {% if loans %}
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Leitor(a)</th>
            <th>Desde</th>
            <th>Devolver até</th>
            <th>Situação</th>
          </tr>
        </thead>
        <tbody>
          {% for loan in loans %}
            <tr>
              <td>{{ loan.user.username }}</td>
              <td>{{ loan.borrowed_at|date:"d/m/Y" }}</td>
              <td>{{ loan.due_date|date:"d/m/Y" }}</td>
              <td>
                {% if loan.is_overdue %}
                  <strong class="danger">Atrasado</strong>
                {% else %}
                  <span class="success">Em dia</span>
                {% endif %}
              </td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  {% else %}
    <p class="muted">Todas as cópias estão na estante.</p>
  {% endif %}

  <p><a class="btn" href="{% url 'catalog:book_list' %}">« Voltar ao acervo</a></p>
{% endblock %}
```

### Passo 7 — Livros suficientes para ver a paginação

Com poucos livros não há o que paginar. Crie 25 livros de teste pelo shell:

```powershell
python manage.py shell
```

```python
from catalog.models import Book

# Cria 25 livros de teste com títulos e ISBNs diferentes
for i in range(1, 26):
    Book.objects.create(title=f"Livro de teste {i:02d}", author="Autor Exemplo",
                        isbn=f"{9780000000000 + i}", copies_total=2)

Book.objects.count()  # confere o total
exit()
```

`{i:02d}` escreve o número com dois dígitos (`01`, `02`...) para a ordem alfabética ficar certa, e `9780000000000 + i` gera ISBNs diferentes. Esses nomes genéricos serão trocados por um acervo de verdade na Aula 4.

### Passo 8 — Testando no navegador

Rode `python manage.py runserver` e confira:

1. **Busca:** digite `machado` e clique em Filtrar. A URL vira `/?q=machado`.
2. **Filtro:** marque **Somente com cópias disponíveis**.
3. **Paginação:** limpe os filtros. Aparecem 10 livros e o texto **Página 1 de N**. Clique em **Próxima »**.
4. **Filtros mantidos:** busque `teste` e vá para a página 2. A URL fica `/?q=teste&page=2`.
5. **Equipe:** crie no Admin um empréstimo com prazo no passado. Entre como superusuário, abra **Atrasados** e clique em **Registrar devolução**.
6. **Com quem está?:** no acervo, logado como superusuário, clique no botão de um livro emprestado.
7. **Autorização:** entre como `maria` e digite `http://127.0.0.1:8000/equipe/atrasados/`. A resposta é **403 Forbidden**.

---

## Parte 3 — Testes automatizados

### Passo 9 — Escrever os testes

**Arquivo:** `catalog/tests.py` · **Ação:** substituir todo o conteúdo

```python
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse  # gera o endereço a partir do nome da rota (como o {% url %})
from django.utils import timezone

from .models import Book, Loan


def make_loan(book, user, days=14):
    """Atalho para criar empréstimos nos testes (days negativo = prazo já vencido)."""
    return Loan.objects.create(book=book, user=user, due_date=timezone.localdate() + timedelta(days=days))


class LoanModelTests(TestCase):
    """Testes das regras que ficam nos models."""

    def setUp(self):
        # setUp roda antes de CADA teste; o banco de testes começa vazio
        self.user = User.objects.create_user("maria", password="senha-forte-123")
        self.book = Book.objects.create(title="Dom Casmurro", author="Machado de Assis",
                                        isbn="9788535910663", copies_total=2)

    def test_copies_available_desconta_emprestimos_ativos(self):
        self.assertEqual(self.book.copies_available, 2)
        make_loan(self.book, self.user)
        self.assertEqual(self.book.copies_available, 1)  # uma cópia saiu

    def test_emprestimo_com_prazo_vencido_esta_atrasado(self):
        loan = make_loan(self.book, self.user, days=-1)  # prazo era ontem
        self.assertTrue(loan.is_overdue)

    def test_mark_returned_encerra_o_emprestimo(self):
        loan = make_loan(self.book, self.user)
        loan.mark_returned()
        self.assertFalse(loan.is_active)
        self.assertFalse(loan.is_overdue)
        self.assertEqual(self.book.copies_available, 2)  # a cópia voltou para a estante


class BookListViewTests(TestCase):
    """Testes da página do acervo."""

    def setUp(self):
        self.user = User.objects.create_user("maria", password="senha-forte-123")
        self.client.force_login(self.user)  # entra no sistema sem precisar digitar a senha
        Book.objects.create(title="Dom Casmurro", author="Machado de Assis", isbn="1111111111111")
        Book.objects.create(title="Capitães da Areia", author="Jorge Amado", isbn="2222222222222")

    def test_exige_login(self):
        self.client.logout()
        response = self.client.get(reverse("catalog:book_list"))
        self.assertEqual(response.status_code, 302)  # 302 = redirecionou para o login

    def test_busca_por_autor(self):
        # O segundo argumento do get vira a parte ?q=machado da URL
        response = self.client.get(reverse("catalog:book_list"), {"q": "machado"})
        self.assertContains(response, "Dom Casmurro")
        self.assertNotContains(response, "Capitães da Areia")

    def test_filtro_somente_disponiveis(self):
        livro = Book.objects.get(isbn="2222222222222")
        make_loan(livro, self.user)  # a única cópia saiu
        response = self.client.get(reverse("catalog:book_list"), {"disponivel": "1"})
        self.assertContains(response, "Dom Casmurro")
        self.assertNotContains(response, "Capitães da Areia")

    def test_paginacao_mostra_10_por_pagina(self):
        # Mais 15 livros: com os 2 do setUp, são 17 livros, ou seja, 2 páginas
        for i in range(15):
            Book.objects.create(title=f"Livro {i:02d}", author="Autor", isbn=f"99900000000{i:02d}")
        response = self.client.get(reverse("catalog:book_list"))
        # response.context guarda as variáveis que a view enviou para o template
        self.assertEqual(len(response.context["page_obj"]), 10)
        self.assertContains(response, "Página 1 de 2")


class LoanViewsTests(TestCase):
    """Testes de emprestar e devolver pelas páginas."""

    def setUp(self):
        self.maria = User.objects.create_user("maria", password="senha-forte-123")
        self.joao = User.objects.create_user("joao", password="senha-forte-123")
        self.book = Book.objects.create(title="Dom Casmurro", author="Machado de Assis",
                                        isbn="9788535910663", copies_total=1)

    def test_emprestar_cria_emprestimo(self):
        self.client.force_login(self.maria)
        # args preenche o <int:book_id> da rota
        self.client.post(reverse("catalog:borrow_book", args=[self.book.id]))
        self.assertEqual(Loan.objects.filter(user=self.maria, book=self.book).count(), 1)

    def test_emprestar_exige_post(self):
        self.client.force_login(self.maria)
        response = self.client.get(reverse("catalog:borrow_book", args=[self.book.id]))
        self.assertEqual(response.status_code, 405)  # 405 = método não permitido
        self.assertEqual(Loan.objects.count(), 0)  # nada foi criado

    def test_nao_empresta_sem_copias(self):
        make_loan(self.book, self.joao)  # João pegou a única cópia
        self.client.force_login(self.maria)
        self.client.post(reverse("catalog:borrow_book", args=[self.book.id]))
        self.assertFalse(Loan.objects.filter(user=self.maria).exists())

    def test_nao_devolve_emprestimo_de_outra_pessoa(self):
        loan = make_loan(self.book, self.joao)
        self.client.force_login(self.maria)  # Maria tenta devolver o livro do João
        response = self.client.post(reverse("catalog:return_book", args=[loan.id]))
        self.assertEqual(response.status_code, 404)
        loan.refresh_from_db()  # relê o empréstimo do banco
        self.assertTrue(loan.is_active)  # continua ativo


class StaffViewsTests(TestCase):
    """Testes da área da equipe."""

    def setUp(self):
        self.leitor = User.objects.create_user("maria", password="senha-forte-123")
        self.equipe = User.objects.create_user("bibliotecaria", password="senha-forte-123", is_staff=True)
        self.book = Book.objects.create(title="Dom Casmurro", author="Machado de Assis", isbn="9788535910663")

    def test_leitor_comum_recebe_403(self):
        self.client.force_login(self.leitor)
        response = self.client.get(reverse("catalog:overdue_loans"))
        self.assertEqual(response.status_code, 403)  # 403 = proibido

    def test_equipe_ve_atrasados(self):
        make_loan(self.book, self.leitor, days=-3)
        self.client.force_login(self.equipe)
        response = self.client.get(reverse("catalog:overdue_loans"))
        self.assertContains(response, "Dom Casmurro")

    def test_equipe_registra_devolucao(self):
        loan = make_loan(self.book, self.leitor, days=-3)
        self.client.force_login(self.equipe)
        self.client.post(reverse("catalog:staff_mark_returned", args=[loan.id]))
        loan.refresh_from_db()
        self.assertFalse(loan.is_active)
```

#### Entendendo o código

- Cada **classe** herda de `TestCase` e agrupa testes de um assunto.
- **`setUp`** roda antes de cada teste. Cada teste começa com o banco vazio mais o que o `setUp` criou.
- Todo método cujo nome começa com **`test_`** é um teste. Nomes descritivos ajudam: quando um teste falha, o nome já diz o que quebrou.
- **`self.client`** é um navegador simulado: `.get()` e `.post()` fazem pedidos de verdade ao sistema, e `.force_login()` entra sem digitar senha.
- **`reverse("catalog:book_list")`** faz em Python o mesmo que o `{% url %}` faz no template.

| Verificação | Confere que... |
|---|---|
| `assertEqual(a, b)` | `a == b` |
| `assertTrue(x)` / `assertFalse(x)` | `x` é verdadeiro / falso |
| `assertContains(response, "texto")` | a página respondeu 200 e contém o texto |
| `assertNotContains(response, "texto")` | a página não contém o texto |

Repare que as regras de segurança explicadas na Aula 2 agora estão comprovadas por testes: `test_emprestar_exige_post`, `test_nao_devolve_emprestimo_de_outra_pessoa` e `test_leitor_comum_recebe_403`.

### Passo 10 — Rodar os testes

```powershell
python manage.py test
```

Resultado esperado (o tempo varia de máquina para máquina):

```text
Found 14 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..............
----------------------------------------------------------------------
Ran 14 tests in 3.521s

OK
Destroying test database for alias 'default'...
```

Cada ponto é um teste que passou. Uma letra **F** indica falha (a verificação deu diferente do esperado) e uma letra **E** indica erro (o código quebrou durante o teste).

**Experimente quebrar de propósito:** na view `return_book`, apague o trecho `, user=request.user` e rode os testes. O `test_nao_devolve_emprestimo_de_outra_pessoa` falha e aponta a falha de segurança. Depois desfaça a mudança e rode de novo.

---

## Checkpoint

- [ ] A busca por título, autor e ISBN funciona, e o campo mantém o texto pesquisado.
- [ ] O filtro "Somente com cópias disponíveis" funciona.
- [ ] A paginação mostra 10 livros por página e mantém a busca ao trocar de página.
- [ ] O superusuário vê **Atrasados** e **Com quem está?** e consegue registrar uma devolução.
- [ ] Um leitor comum recebe 403 em `/equipe/atrasados/`.
- [ ] `python manage.py test` mostra 14 testes OK.

---

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `Invalid block tag ... 'querystring'` | Django anterior à versão 5.1 | `pip install "Django>=5.2,<6.0"` |
| A busca não filtra nada | `name` do campo diferente do nome lido na view | O HTML usa `name="q"` e a view usa `request.GET.get("q")` |
| Na página 2 a busca some | Link escrito como `href="?page=2"` | Use `{% querystring page=... %}` |
| `NameError: name 'Q' is not defined` | Falta o import | `from django.db.models import Count, F, Q` |
| `Cannot resolve keyword 'available'` | Filtro por `available` antes do `annotate` | O `annotate` precisa vir antes na cadeia |
| `UNIQUE constraint failed` no Passo 7 | O laço já foi executado antes | Os livros já existem; pode seguir |
| Teste falha com `302 != 200` | A página redirecionou (por exemplo, para o login) | Confira se o teste chamou `force_login` |

---

## Resumo

Criamos a área da equipe (atrasados, com quem está, registro de devolução), acrescentamos busca, filtro e paginação ao acervo e escrevemos 14 testes automatizados.

O que ficou de ideia principal:

- **Autorização** com um decorator próprio (`staff_required`) que responde 403.
- **Filtros** montados em etapas a partir de `request.GET`, com `Q` para o OU e lookups como `__icontains`, `__lt` e `__gt`.
- **`annotate` com `Count`, `F` e `Q`** calcula a disponibilidade no banco, numa consulta só.
- **`Paginator`** divide a lista em páginas, e `{% querystring %}` mantém os filtros ao trocar de página.
- **Testes** com `TestCase` usam banco separado, `setUp`, `self.client` e asserts.

---

## Exercícios

1. Troque `BOOKS_PER_PAGE` para 5 e observe a paginação. Algum teste quebrou? Por quê? Depois volte para 10.
2. Na página de atrasados, mostre também o e-mail do leitor (`loan.user.email`).
3. Escreva o teste `test_busca_por_isbn` seguindo o modelo do `test_busca_por_autor`.
4. (Desafio) Crie no model `Loan` uma `@property` chamada `days_overdue`, que devolve o número de dias de atraso (0 se não houver atraso). Use-a na página de atrasados e escreva um teste para ela.

---

## Perguntas para revisar

<details>
<summary>1. Qual a diferença entre responder 302 (ir para o login) e 403?</summary>

O 302 para o login é para quem não está autenticado: "entre primeiro". O 403 é para quem está autenticado mas não tem autorização: "você não pode ver isto".
</details>

<details>
<summary>2. Por que usar <code>annotate</code> em vez da <code>@property copies_available</code> na listagem?</summary>

A `@property` faz uma consulta por livro. O `annotate` calcula a disponibilidade de todos os livros numa consulta só. Além disso, o valor do `annotate` pode ser usado em `filter` e `order_by`.
</details>

<details>
<summary>3. Por que o formulário de busca usa GET e não precisa de <code>{% csrf_token %}</code>?</summary>

Porque buscar não altera dados. Com GET os filtros ficam na URL, que pode ser salva e compartilhada. O CSRF protege ações que alteram dados, e essas usam POST.
</details>

<details>
<summary>4. Esconder o link "Atrasados" do menu protege a página?</summary>

Não. Qualquer pessoa pode digitar o endereço. A proteção real é o `@staff_required` na view.
</details>

<details>
<summary>5. Os testes alteram os dados cadastrados?</summary>

Não. O Django cria um banco de testes separado e vazio a cada execução e o apaga no final.
</details>

---

Próxima aula: [Aula 4 — Categorias, busca avançada e exportação](Aula_04_Categorias_Busca_Avancada_e_Exportacao.md).
