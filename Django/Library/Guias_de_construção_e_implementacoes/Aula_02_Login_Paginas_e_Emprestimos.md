# Aula 2 — Login, páginas e empréstimos

Sistema de Biblioteca com Django · Aula 2 de 6 · [Roteiro do curso](README.md)

## Objetivos da aula

- Entender o caminho **URL → View → Template**.
- Criar as primeiras páginas: **login**, **acervo** e **meus empréstimos**.
- Usar **herança de templates** para ter um layout único (menu, cores, tema claro e escuro).
- Permitir que o leitor **empreste** e **devolva** livros com segurança.
- Entender **GET e POST**, **CSRF**, **mensagens** e o padrão **Post/Redirect/Get**.

Ao final da aula, um leitor entra no sistema, vê o acervo com as capas, pega um livro emprestado e devolve.

| Aula 1 | Aula 2 | Aula 3 | Aula 4 | Aula 5 | Aula 6 |
|:---:|:---:|:---:|:---:|:---:|:---:|
| Concluída | **Aula atual** | Equipe, busca e testes | Categorias e exportação | Contas e avaliações | Relatórios e banco |

## Antes de começar

- [ ] Abra a pasta `biblioteca` no VS Code e ative o ambiente virtual (`.\.venv\Scripts\Activate.ps1`).
- [ ] `python manage.py check` não mostra erros.
- [ ] Existem pelo menos três livros e o usuário `maria` cadastrados pelo Admin. Se não lembrar a senha da `maria`, troque-a no Admin: **Usuários → maria → formulário de alteração de senha**.

---

## Parte 1 — Conceitos

### 1.1 O caminho de um pedido

Quando o navegador pede `http://127.0.0.1:8000/emprestimos/`:

```
1. library/urls.py   "Quem cuida de 'emprestimos/'?"   →  repassa para catalog/urls.py
2. catalog/urls.py   "'emprestimos/' é a view my_loans"  →  chama views.my_loans(request)
3. views.py          my_loans busca os empréstimos no banco (Model)
                     e chama render(request, "catalog/my_loans.html", {"loans": ...})
4. template          o HTML é montado com os dados e volta para o navegador
```

- Uma **view** é uma função Python que **recebe** um `request` (o pedido: quem está logado, os dados enviados etc.) e **devolve** uma resposta (uma página HTML, um redirecionamento, um arquivo).
- Um **template** é um HTML com lacunas que o Django preenche. `{{ variavel }}` mostra um valor e `{% tag %}` executa uma lógica (`{% if %}`, `{% for %}`, `{% url %}`).

### 1.2 GET e POST

| | GET | POST |
|---|---|---|
| Serve para | consultar (abrir uma página, buscar) | alterar algo (emprestar, devolver, sair) |
| Onde vão os dados | na URL (`?q=python`) | no corpo do pedido |
| Pode ser repetido sem problema? | sim | não (emprestaria duas vezes) |
| No HTML | um link `<a href>` | `<form method="post">` |

**Regra:** tudo o que altera o banco usa POST. Um link comum nunca deve emprestar ou apagar nada, porque navegadores, antivírus e buscadores às vezes abrem links sozinhos para adiantar o carregamento.

### 1.3 CSRF

Imagine um site malicioso com um formulário escondido que envia um POST para `sua-biblioteca/livros/1/emprestar/`. Se você estiver logado na biblioteca, o navegador enviaria o pedido em seu nome. Esse ataque se chama **CSRF**.

O Django bloqueia isso exigindo um código secreto em todo formulário POST, gerado pela tag **`{% csrf_token %}`**. Sem ela, a resposta é **403 Forbidden**.

### 1.4 Post/Redirect/Get

Depois de processar um POST com sucesso, a view não mostra uma página diretamente. Ela **redireciona** para outra, que o navegador carrega com GET:

```
POST /livros/1/emprestar/  →  cria o empréstimo  →  redirect para /emprestimos/  →  GET /emprestimos/
```

Assim, se a pessoa apertar F5, ela só recarrega a lista, sem emprestar de novo. Para informar o resultado, usamos as **mensagens** do Django (`messages.success(...)`), que aparecem uma única vez na página seguinte.

---

## Parte 2 — Configuração e URLs

### Passo 1 — Pasta de templates e redirecionamentos de login

**Arquivo:** `library/settings.py` · **Ação:** alterar dois trechos

**1.1)** Em `TEMPLATES`, troque a linha `'DIRS': [],` por:

```python
        'DIRS': [BASE_DIR / 'templates'],  # pasta de templates do projeto (ao lado do manage.py)
```

**1.2)** No final do arquivo, depois das linhas `MEDIA_...`, adicione:

```python
# Autenticação (os valores são NOMES de rotas, não endereços)
LOGIN_URL = 'login'  # para onde vai quem tenta abrir uma página protegida sem estar logado
LOGIN_REDIRECT_URL = 'catalog:book_list'  # para onde vai depois de entrar
LOGOUT_REDIRECT_URL = 'login'  # para onde vai depois de sair
```

As rotas `login` e `catalog:book_list` serão criadas nos próximos passos.

### Passo 2 — URLs do projeto

**Arquivo:** `library/urls.py` · **Ação:** substituir todo o conteúdo

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Lista de endereços do projeto. O Django testa de cima para baixo e usa o primeiro que combinar.
urlpatterns = [
    # Painel administrativo: /admin/
    path("admin/", admin.site.urls),
    # Login, logout e recuperação de senha prontos do Django: /contas/login/, /contas/logout/ ...
    path("contas/", include("django.contrib.auth.urls")),
    # Todos os outros endereços são resolvidos pelo arquivo catalog/urls.py
    path("", include("catalog.urls")),
]

# Só em desenvolvimento (DEBUG=True): o próprio Django entrega as imagens enviadas (capas).
# Em um servidor de verdade, quem faz isso é o servidor web (Nginx, Apache...).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

#### Entendendo o código

O `include("django.contrib.auth.urls")` acrescenta ao projeto as rotas de autenticação que já vêm prontas no Django:

| Endereço | Nome da rota | Uso |
|---|---|---|
| `/contas/login/` | `login` | entrar |
| `/contas/logout/` | `logout` | sair (só aceita POST) |
| `/contas/password_reset/` | `password_reset` | recuperar a senha (Aula 5) |
| `/contas/password_change/` | `password_change` | trocar a senha |

A view de login pronta procura o template `registration/login.html`, que vamos criar no Passo 7.

### Passo 3 — URLs do app

**Arquivo:** `catalog/urls.py` · **Ação:** criar (o arquivo ainda não existe)

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
]
```

#### Entendendo o código

- **`app_name`** cria um "sobrenome" para as rotas. Escrevemos `catalog:book_list`, e não há confusão se outro app também tiver uma rota `book_list`.
- **`<int:book_id>`** é uma parte variável da URL. Em `/livros/7/emprestar/`, o Django chama `borrow_book(request, book_id=7)`. O `int:` só deixa passar números.
- **`name=...`** é o nome da rota. Nos templates, use sempre `{% url 'catalog:my_loans' %}` em vez de escrever o endereço à mão: se o endereço mudar um dia, basta mudar aqui.

---

## Parte 3 — As views

### Passo 4 — Escrever as views

**Arquivo:** `catalog/views.py` · **Ação:** substituir todo o conteúdo

```python
from datetime import timedelta  # representa um intervalo de tempo (ex.: 14 dias)

from django.contrib import messages  # mensagens de retorno ("Empréstimo feito!")
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Book, Loan

LOAN_DAYS = 14  # prazo padrão de empréstimo, em dias


@login_required  # só usuários logados; os outros são mandados para o login
def book_list(request):
    """Mostra todos os livros do acervo."""
    books = Book.objects.all()
    # render junta o template com os dados; cada chave do dicionário vira uma variável no template
    return render(request, "catalog/book_list.html", {"books": books})


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
```

#### Entendendo o código

**Decorators nas views.** Funcionam como uma catraca na entrada da função:

| Decorator | Se a regra não for cumprida... |
|---|---|
| `@login_required` | quem não está logado vai para o login e, depois de entrar, volta à página que queria |
| `@require_POST` | um pedido GET recebe **405 Method Not Allowed** |

**Atalhos do Django** (`django.shortcuts`):

- `render(request, "template.html", {"chave": valor})` monta o HTML. O dicionário é o **contexto**: cada chave vira uma variável no template.
- `redirect("catalog:my_loans")` responde "vá para outra página" (código 302).
- `get_object_or_404(Book, pk=book_id)` busca o livro e, se ele não existir, responde 404 em vez de gerar um erro no servidor.

**Segurança no `return_book`.** O filtro `user=request.user` é essencial. Sem ele, qualquer pessoa logada poderia devolver o empréstimo de outra apenas trocando o número na URL. Com ele, o empréstimo de outra pessoa "não existe" para quem pede, e a resposta é 404.

**`select_related("book")`.** O template vai mostrar `loan.book.title` em cada linha. Sem o `select_related`, o Django faria uma consulta extra para cada empréstimo. Com ele, o livro vem junto na mesma consulta (um `JOIN` no SQL).

**`LOAN_DAYS`** é uma constante: um nome em maiúsculas para um valor fixo. Se o prazo mudar, a alteração é feita num lugar só.

---

## Parte 4 — Os templates

### Passo 5 — Criar as pastas

Na pasta `biblioteca`, ao lado do `manage.py`, crie esta estrutura:

```
biblioteca/
└── templates/
    ├── base.html                ← layout comum (Passo 6)
    ├── registration/
    │   └── login.html           ← Passo 7
    └── catalog/
        ├── book_list.html       ← Passo 8
        └── my_loans.html        ← Passo 9
```

Pelo terminal:

```powershell
mkdir templates\registration, templates\catalog
```

### Passo 6 — O template base

Todas as páginas têm o mesmo cabeçalho, menu, cores e área de mensagens. Em vez de repetir isso em cada arquivo, criamos um **template base** com lacunas, os `{% block %}`. As outras páginas **herdam** dele e preenchem só essas lacunas, como na herança de classes.

**Arquivo:** `templates/base.html` · **Ação:** criar

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  {# Cada página pode trocar o título preenchendo este bloco #}
  <title>{% block title %}Biblioteca{% endblock %}</title>
  <style>
    /* 1) Cores do tema claro, guardadas em variáveis CSS */
    :root {
      --bg: #f6f7f9;       /* fundo da página */
      --card: #ffffff;     /* fundo de cartões, tabelas e campos */
      --text: #1f2328;     /* texto principal */
      --muted: #6b7280;    /* texto secundário */
      --border: #d9dde3;   /* bordas */
      --primary: #2f5bd3;  /* links e botões principais */
      --header: #1e293b;   /* barra do menu */
      --danger: #b42318;   /* erros e atrasos */
      --success: #067647;  /* confirmações */
      --warning: #b54708;  /* avisos */
    }
    /* 2) Tema escuro: só trocamos o valor das variáveis */
    .theme-dark {
      --bg: #0f141a;
      --card: #18202a;
      --text: #e6e9ee;
      --muted: #9aa4b2;
      --border: #2c3643;
      --primary: #7aa2ff;
      --header: #0b1016;
      --danger: #ff7a70;
      --success: #4ad295;
      --warning: #ffb86b;
    }

    /* 3) Estilos gerais: todos usam as variáveis acima */
    * { box-sizing: border-box; }
    body { margin: 0; font-family: system-ui, Arial, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }
    a { color: var(--primary); }

    /* Menu superior */
    header { background: var(--header); padding: 12px 16px; }
    nav { max-width: 1000px; margin: 0 auto; display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; }
    nav a { color: #fff; text-decoration: none; }
    nav a:hover { text-decoration: underline; }
    .spacer { flex: 1; } /* ocupa o espaço livre e empurra o que vem depois para a direita */
    nav .user { color: #cbd5e1; }

    /* Área de conteúdo */
    main { max-width: 1000px; margin: 0 auto; padding: 16px; }

    /* Classes utilitárias usadas nas páginas */
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin-bottom: 16px; }
    .muted { color: var(--muted); }
    .danger { color: var(--danger); }
    .success { color: var(--success); }

    /* Botões (servem para <button> e para links <a class="btn">) */
    .btn { display: inline-block; padding: 6px 12px; border: 1px solid var(--border); border-radius: 6px;
           background: var(--card); color: var(--text); cursor: pointer; font: inherit; text-decoration: none; }
    .btn:hover { border-color: var(--primary); }
    .btn-primary { background: var(--primary); border-color: var(--primary); color: #fff; }
    .btn[disabled] { opacity: .5; cursor: not-allowed; }
    form.inline { display: inline; } /* formulário na mesma linha do texto */

    /* Tabelas */
    table { width: 100%; border-collapse: collapse; background: var(--card); }
    th, td { padding: 8px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: middle; }
    .table-wrap { overflow-x: auto; } /* em telas pequenas a tabela rola para o lado */

    /* Miniatura da capa (ou o quadro "sem capa") */
    .cover { width: 48px; height: 72px; object-fit: cover; border-radius: 4px; background: var(--border);
             display: flex; align-items: center; justify-content: center; font-size: 10px; color: var(--muted); text-align: center; }

    /* Mensagens do Django: a classe vem de message.tags (success, error, warning, info) */
    .message { padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; border: 1px solid var(--border); background: var(--card); }
    .message.success { border-color: var(--success); color: var(--success); }
    .message.error   { border-color: var(--danger);  color: var(--danger); }
    .message.warning { border-color: var(--warning); color: var(--warning); }

    /* Formulários */
    input, select, textarea { font: inherit; padding: 6px 8px; border: 1px solid var(--border); border-radius: 6px;
                              background: var(--card); color: var(--text); }
    .form-grid { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
    .form-grid label { display: block; font-weight: 600; margin-bottom: 4px; }
    .form-grid input, .form-grid select { width: 100%; }
    .actions { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 12px; }
  </style>
</head>
<body>
  <header>
    <nav>
      <a href="{% url 'catalog:book_list' %}"><strong>Biblioteca</strong></a>
      {# "user" está disponível em todos os templates: é o usuário da requisição #}
      {% if user.is_authenticated %}
        <a href="{% url 'catalog:my_loans' %}">Meus empréstimos</a>
        {# Links que só a equipe (is_staff) enxerga #}
        {% if user.is_staff %}
          <a href="{% url 'admin:index' %}">Admin</a>
        {% endif %}
      {% endif %}
      <span class="spacer"></span>
      <button id="theme-toggle" class="btn" type="button">Tema escuro</button>
      {% if user.is_authenticated %}
        <span class="user">Olá, {{ user.username }}</span>
        {# Sair altera a sessão, por isso é um formulário POST (e não um link) #}
        <form class="inline" method="post" action="{% url 'logout' %}">
          {% csrf_token %}
          <button class="btn" type="submit">Sair</button>
        </form>
      {% else %}
        <a href="{% url 'login' %}">Entrar</a>
      {% endif %}
    </nav>
  </header>

  <main>
    {# Mensagens criadas nas views com messages.success(), messages.error()... Aparecem uma única vez. #}
    {% for message in messages %}
      <div class="message {{ message.tags }}">{{ message }}</div>
    {% endfor %}

    {# Aqui entra o conteúdo de cada página #}
    {% block content %}{% endblock %}
  </main>

  <script>
    // Tema claro/escuro: a escolha fica guardada no navegador (localStorage)
    (function () {
      const root = document.documentElement; // a tag <html>
      const button = document.getElementById("theme-toggle");

      // Liga ou desliga a classe .theme-dark e ajusta o texto do botão
      function apply(theme) {
        root.classList.toggle("theme-dark", theme === "dark");
        button.textContent = theme === "dark" ? "Tema claro" : "Tema escuro";
      }

      // Na primeira visita, segue a preferência do sistema operacional
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      apply(localStorage.getItem("theme") || (prefersDark ? "dark" : "light"));

      // A cada clique, inverte o tema e guarda a escolha
      button.addEventListener("click", function () {
        const next = root.classList.contains("theme-dark") ? "light" : "dark";
        localStorage.setItem("theme", next);
        apply(next);
      });
    })();
  </script>
</body>
</html>
```

#### Entendendo o código

- **Blocos.** `{% block title %}` e `{% block content %}` são as lacunas que as páginas filhas preenchem. O texto entre as tags é o valor padrão.
- **`{{ user }}`** está disponível em qualquer template: é o usuário logado. `user.is_authenticated` diz se há alguém logado e `user.is_staff` diz se a pessoa faz parte da equipe.
- **Comentários de template.** O que fica entre `{#` e `#}` não aparece no HTML enviado ao navegador.
- **Sair** é um formulário POST. Desde o Django 5, o logout não aceita GET.
- **Mensagens.** O `{% for message in messages %}` mostra as mensagens criadas nas views. `message.tags` vira a classe CSS (`success`, `error`, `warning`), que define a cor.
- **Tema claro e escuro.** As cores ficam em variáveis CSS (`--bg`, `--text`...) e todo o CSS usa `var(--bg)`, nunca uma cor fixa. A classe `.theme-dark` redefine as variáveis, então basta colocá-la na tag `<html>` para trocar todas as cores de uma vez. O JavaScript faz essa troca no clique e guarda a escolha no `localStorage` do navegador.

### Passo 7 — Página de login

**Arquivo:** `templates/registration/login.html` · **Ação:** criar

```html
{% extends "base.html" %}
{# extends precisa ser a primeira linha: esta página herda o layout do base.html #}
{% block title %}Entrar · Biblioteca{% endblock %}
{% block content %}
  <div class="card" style="max-width: 420px; margin: 40px auto;">
    <h1>Entrar</h1>

    {# form é enviado pela view de login do Django; form.errors existe quando a senha está errada #}
    {% if form.errors %}
      <div class="message error">Usuário ou senha incorretos. Tente novamente.</div>
    {% endif %}

    <form method="post">
      {% csrf_token %}
      {# Desenha os campos usuário e senha, um por parágrafo #}
      {{ form.as_p }}
      {# Página que a pessoa tentava abrir antes do login; o Django volta para ela depois #}
      <input type="hidden" name="next" value="{{ next }}">
      <button class="btn btn-primary" type="submit">Entrar</button>
    </form>
  </div>
{% endblock %}
```

Repare que não escrevemos nenhuma view de login: ela veio pronta com o `django.contrib.auth.urls`. Nós só fornecemos o template.

### Passo 8 — Página do acervo

**Arquivo:** `templates/catalog/book_list.html` · **Ação:** criar

```html
{% extends "base.html" %}
{% block title %}Livros · Biblioteca{% endblock %}
{% block content %}
  <h1>Acervo</h1>

  {# books foi enviado pela view no dicionário de contexto #}
  {% if books %}
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
          {# Uma linha da tabela para cada livro #}
          {% for book in books %}
            <tr>
              <td>
                {# book.image.url monta o endereço /media/book_covers/... #}
                {% if book.image %}
                  <img class="cover" src="{{ book.image.url }}" alt="Capa de {{ book.title }}">
                {% else %}
                  <div class="cover">sem capa</div>
                {% endif %}
              </td>
              <td>{{ book.title }}</td>
              <td>{{ book.author }}</td>
              {# copies_available é a @property do model Book #}
              <td>{{ book.copies_available }} de {{ book.copies_total }}</td>
              <td>
                {% if book.copies_available > 0 %}
                  {# Emprestar altera dados: formulário POST com o token de segurança CSRF #}
                  <form class="inline" method="post" action="{% url 'catalog:borrow_book' book.id %}">
                    {% csrf_token %}
                    <button class="btn btn-primary" type="submit">Emprestar</button>
                  </form>
                {% else %}
                  <button class="btn" disabled>Indisponível</button>
                {% endif %}
              </td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  {% else %}
    <p class="muted">Nenhum livro cadastrado ainda. Cadastre pelo Admin.</p>
  {% endif %}
{% endblock %}
```

O botão **Indisponível** é só visual. Quem realmente impede o empréstimo sem cópias é a view, que confere de novo antes de gravar. Alguém pode ter levado a última cópia entre o carregamento da página e o clique. Em resumo: **o que está na tela é só uma sugestão; as regras de verdade ficam no servidor.**

### Passo 9 — Página "Meus empréstimos"

**Arquivo:** `templates/catalog/my_loans.html` · **Ação:** criar

```html
{% extends "base.html" %}
{% block title %}Meus empréstimos · Biblioteca{% endblock %}
{% block content %}
  <h1>Meus empréstimos</h1>

  {% if loans %}
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Livro</th>
            <th>Emprestado em</th>
            <th>Devolver até</th>
            <th>Situação</th>
            <th>Ação</th>
          </tr>
        </thead>
        <tbody>
          {% for loan in loans %}
            <tr>
              {# loan.book segue a ForeignKey até o livro #}
              <td>{{ loan.book.title }}</td>
              {# O filtro date formata a data: dia/mês/ano hora:minuto #}
              <td>{{ loan.borrowed_at|date:"d/m/Y H:i" }}</td>
              <td>{{ loan.due_date|date:"d/m/Y" }}</td>
              <td>
                {# A ordem importa: primeiro devolvido, depois atrasado, senão em dia #}
                {% if loan.returned_at %}
                  <span class="muted">Devolvido em {{ loan.returned_at|date:"d/m/Y" }}</span>
                {% elif loan.is_overdue %}
                  <strong class="danger">Atrasado</strong>
                {% else %}
                  <span class="success">Em dia</span>
                {% endif %}
              </td>
              <td>
                {# O botão só aparece enquanto o empréstimo está ativo #}
                {% if loan.is_active %}
                  <form class="inline" method="post" action="{% url 'catalog:return_book' loan.id %}">
                    {% csrf_token %}
                    <button class="btn" type="submit">Devolver</button>
                  </form>
                {% endif %}
              </td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  {% else %}
    <p class="muted">Você ainda não pegou nenhum livro emprestado.</p>
  {% endif %}
{% endblock %}
```

O `|date:"d/m/Y"` é um **filtro**: ele transforma o valor antes de mostrar. As propriedades `is_overdue` e `is_active` são as mesmas que criamos no model na Aula 1. O template aproveita as regras do model em vez de repeti-las.

---

## Parte 5 — Testando

### Passo 10 — Usar o sistema

```powershell
python manage.py runserver
```

1. Acesse <http://127.0.0.1:8000/>. Sem login, você é levado para `/contas/login/?next=/`.
2. Entre com a `maria` e veja o acervo com as capas.
3. Clique em **Emprestar**. Você vai para **Meus empréstimos**, com a mensagem de confirmação.
4. Volte ao acervo: as cópias disponíveis diminuíram.
5. Tente emprestar o mesmo livro de novo: aparece o aviso "Você já está com...".
6. Em **Meus empréstimos**, clique em **Devolver**.
7. Clique em **Tema escuro** e recarregue a página: a escolha é mantida.
8. Clique em **Sair** e entre com o superusuário: o link **Admin** aparece no menu.

### Passo 11 — Verificar a segurança

Com a `maria` logada, digite no navegador <http://127.0.0.1:8000/livros/1/emprestar/>. A resposta é **405 Method Not Allowed**, porque abrir um endereço é um pedido GET e a view só aceita POST.

Crie pelo Admin um empréstimo para outro usuário. Logada como `maria`, não existe botão para devolvê-lo, e mesmo que alguém forjasse o pedido, o filtro `user=request.user` responderia 404. Na Aula 3 vamos confirmar isso com um teste automatizado.

---

## Checkpoint

- [ ] Sem login, qualquer página leva à tela de **Entrar**.
- [ ] Um login com senha errada mostra a mensagem de erro.
- [ ] O acervo mostra as capas cadastradas.
- [ ] Emprestar e devolver funcionam e mostram as mensagens coloridas.
- [ ] Não é possível emprestar o mesmo livro duas vezes nem emprestar sem cópias.
- [ ] **Sair** funciona, e o tema escolhido é lembrado.
- [ ] O link **Admin** só aparece para a equipe.

---

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `TemplateDoesNotExist: catalog/book_list.html` | Pasta `templates` no lugar errado ou `DIRS` sem ajuste | A pasta `templates/` fica ao lado do `manage.py`. Confira o Passo 1.1 |
| `NoReverseMatch: 'catalog' is not a registered namespace` | Falta `app_name = "catalog"` | Confira o Passo 3 |
| `NoReverseMatch ... 'borrow_book' with arguments ('',)` | `{% url %}` sem o id | A rota exige o id: `{% url 'catalog:borrow_book' book.id %}` |
| **403 — CSRF verification failed** | Falta `{% csrf_token %}` no formulário | Coloque-o logo depois de `<form method="post">` |
| **405** ao clicar em Sair | Logout feito com um link `<a>` | Use o formulário POST do `base.html` |
| Capas não aparecem | Falta o `static(...)` no `library/urls.py` | Confira o Passo 2 |
| Página sem estilo nem menu | Falta `{% extends "base.html" %}` na primeira linha | Corrija o template |

---

## Resumo

O sistema ganhou páginas de verdade: login, acervo com capas, empréstimo, devolução, histórico, mensagens e tema claro e escuro.

O que ficou de ideia principal:

- **URLs** ligam endereços a views. Nos templates usamos nomes de rotas (`{% url %}`), nunca endereços escritos à mão.
- **Views** recebem o `request`, aplicam as regras e respondem com `render` (uma página) ou `redirect` (outro endereço).
- **Templates** herdam de `base.html` (`{% extends %}` + `{% block %}`) e usam `{{ }}`, `{% if %}`, `{% for %}` e filtros como `|date`.
- **Decorators** como `@login_required` e `@require_POST` controlam o acesso às views.
- **Ações que alteram dados** usam POST, CSRF e redirect (Post/Redirect/Get), com mensagens de retorno.
- **Segurança:** `user=request.user` impede mexer nos dados de outra pessoa.

---

## Exercícios

1. Mude o prazo de empréstimo para 21 dias. Quantos lugares do código precisaram ser alterados?
2. Em `my_loans.html`, mostre a capa do livro numa nova primeira coluna. Dica: use a lógica da `book_list.html` com `loan.book.image`.
3. No acervo, acrescente uma coluna com o ISBN, usando a classe `muted`.
4. (Desafio) No menu, ao lado de "Meus empréstimos", mostre quantos livros a pessoa tem com ela no momento. Dá para fazer só no template? Por que seria melhor calcular na view?

---

## Perguntas para revisar

<details>
<summary>1. Descreva o caminho de um pedido a <code>/emprestimos/</code> até a página aparecer.</summary>

`library/urls.py` repassa para `catalog/urls.py`, que encontra a rota `emprestimos/` e chama a view `my_loans`. A view consulta os empréstimos do usuário pelo model e chama `render` com o template `my_loans.html`. O HTML montado volta para o navegador.
</details>

<details>
<summary>2. Por que emprestar e devolver usam POST?</summary>

Porque alteram dados. Pedidos GET podem ser repetidos ou disparados automaticamente (pré-carregamento, F5, robôs de busca). Além disso, o POST exige o token CSRF, que protege contra sites maliciosos.
</details>

<details>
<summary>3. O que aconteceria se o <code>return_book</code> usasse só <code>get_object_or_404(Loan, pk=loan_id)</code>?</summary>

Qualquer usuário logado poderia devolver empréstimos de outras pessoas trocando o número na URL.
</details>

<details>
<summary>4. Para que serve o padrão Post/Redirect/Get?</summary>

Para evitar que o formulário seja reenviado quando a pessoa atualiza a página. Depois do POST, o navegador vai para uma página carregada com GET, e o F5 só recarrega essa página.
</details>

<details>
<summary>5. Qual a vantagem de ter um <code>base.html</code>?</summary>

O layout (menu, estilos, mensagens, tema) fica num lugar só. Todas as páginas herdam dele, e uma mudança no menu vale para o site inteiro.
</details>

---

Próxima aula: [Aula 3 — Equipe, busca, paginação e testes](Aula_03_Equipe_Busca_Paginacao_e_Testes.md).
