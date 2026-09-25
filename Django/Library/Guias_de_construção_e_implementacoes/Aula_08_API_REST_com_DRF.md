# Aula 8 — API REST da biblioteca com Django REST Framework

Sistema de Biblioteca com Django · Aula 8 de 10 · [Roteiro do curso](README.md)

## Objetivos da aula

- Retomar os conceitos de API REST vistos no [guia prático de FastAPI](../../../API/Guia_FastAPI_Bolsa_Futuro_Digital.pdf) e aplicá-los ao sistema de biblioteca.
- Conhecer o **Django REST Framework (DRF)**: serializers, viewsets, routers, permissões e autenticação por token.
- Criar uma API com os **dados reais** do banco, protegida por **login** e que respeita as **mesmas regras** das páginas.
- Gerar a **documentação interativa** da API (Swagger), como o `/docs` do FastAPI.
- Escrever **testes automatizados** da API.
- Escrever um **programa cliente** em Python que consome a API.
- Publicar a API no PythonAnywhere.
- Comparar **FastAPI, DRF e Django Ninja** e saber quando usar cada um.

Ao final da aula, qualquer programa (um aplicativo de celular, um script Python, outro sistema) poderá consultar o acervo e fazer empréstimos pela internet.

| Aula 1 | Aula 2 | Aula 3 | Aula 4 | Aula 5 | Aula 6 | Aula 7 | Aula 8 | Aula 9 | Aula 10 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Concluída | Concluída | Concluída | Concluída | Concluída | Concluída | Concluída | **Aula atual** | Qualidade de código | Git em equipe |

## Antes de começar

- [ ] Ambiente virtual ativo e `python manage.py test` com 39 testes OK (Aula 7).
- [ ] O sistema publicado no PythonAnywhere (Aula 7).
- [ ] O guia prático de FastAPI à mão, para comparar.

---

## Parte 1 — Conceitos

### 1.1 Do guia de FastAPI à API da biblioteca

No guia de FastAPI, construímos uma API de livros com `GET`, `POST`, `PUT` e `DELETE`. O próprio guia termina apontando o que faltava:

| API do guia de FastAPI | API desta aula |
|---|---|
| Livros numa lista Python: somem quando o servidor reinicia | Livros no banco de dados, com os models que já temos |
| Qualquer pessoa cadastra, altera e apaga | Leitura aberta; alterações só para a equipe; empréstimo só com login |
| `id` calculado com `len(livros) + 1` (repete ids depois de uma exclusão) | `id` gerado pelo banco |
| Regras só na API | As **mesmas** regras das páginas (cópias disponíveis, "você já está com este livro") |
| Sem testes | Testes automatizados |
| Só no computador | Publicada no PythonAnywhere |

### 1.2 Recapitulando REST

Uma API REST organiza o sistema em **recursos** (livros, categorias, empréstimos), cada um com um endereço, e usa os **métodos HTTP** para dizer o que fazer:

| Método | Endereço | O que faz |
|---|---|---|
| `GET` | `/api/livros/` | lista os livros |
| `GET` | `/api/livros/7/` | consulta o livro 7 |
| `POST` | `/api/livros/` | cadastra um livro |
| `PUT` / `PATCH` | `/api/livros/7/` | altera o livro 7 (inteiro / só alguns campos) |
| `DELETE` | `/api/livros/7/` | apaga o livro 7 |
| `POST` | `/api/livros/7/emprestar/` | empresta o livro 7 para quem fez o pedido |

A resposta traz os dados em **JSON** e um **código de status** que resume o resultado. Nesta aula usaremos:

| Código | Significado | Quando aparece na nossa API |
|---|---|---|
| 200 | OK | consultas e alterações bem-sucedidas |
| 201 | Created | livro cadastrado, empréstimo feito |
| 204 | No Content | livro apagado (a resposta não tem corpo) |
| 400 | Bad Request | dados inválidos (ex.: ISBN repetido, campo obrigatório vazio) |
| 401 | Unauthorized | o pedido não informou **quem** está pedindo |
| 403 | Forbidden | sabemos quem é, mas a pessoa **não tem permissão** |
| 404 | Not Found | o recurso não existe (ou não é seu) |
| 409 | Conflict | o pedido é válido, mas uma regra impede (ex.: sem cópias disponíveis) |

### 1.3 As peças do Django REST Framework

O DRF é uma extensão do Django para construir APIs. Ele tem cinco peças principais, e quase todas têm um equivalente no que vimos com FastAPI:

| Peça do DRF | Para quê | No FastAPI |
|---|---|---|
| **Serializer** | converte objetos do banco em JSON e valida o JSON recebido | `BaseModel` do Pydantic |
| **ViewSet** | reúne numa classe as operações sobre um recurso (listar, consultar, criar...) | as funções com `@app.get`, `@app.post`... |
| **Router** | cria os endereços dos ViewSets automaticamente | os endereços escritos em cada decorator |
| **Permission** | decide quem pode fazer cada operação | (não havia) |
| **Authentication** | descobre quem está fazendo o pedido | (não havia) |

O DRF é o padrão de mercado para APIs em projetos Django. A principal vantagem aqui é que ele usa tudo o que o projeto já tem: models, banco, usuários, permissões e testes.

### 1.4 Autenticação por token

Nas páginas do site, o Django sabe quem é você pela **sessão**: um cookie que o navegador guarda depois do login. Programas que consomem uma API (um aplicativo, um script) normalmente não trabalham com cookies. Eles usam um **token**:

1. O programa envia usuário e senha para `POST /api/token/` e recebe um código, por exemplo `9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`.
2. Nos pedidos seguintes, o programa envia esse código no cabeçalho `Authorization: Token 9944b0...`.
3. A API identifica o usuário pelo token, sem precisar da senha de novo.

A nossa API aceita **os dois jeitos**: token (para programas) e sessão (para testar no navegador, logado no site).

### 1.5 Uma regra, duas portas de entrada

Hoje, a regra "só empresta se houver cópia" está dentro da view `borrow_book`, que responde com mensagens e redirecionamentos, coisas de página HTML. A API precisa da **mesma regra**, mas respondendo em JSON. Se copiarmos a regra, um dia as duas versões vão ficar diferentes.

A solução é tirar a regra da view e colocá-la num módulo próprio, `services.py`. A view das páginas e a view da API passam a chamar a mesma função:

```
página (views.py) ─┐
                   ├──▶ services.borrow_book(livro, usuário) ──▶ banco
API (api_views.py) ┘
```

---

## Parte 2 — Preparação

### Passo 1 — Instalar o DRF

```powershell
pip install djangorestframework drf-spectacular requests
```

- **djangorestframework**: o DRF.
- **drf-spectacular**: gera a documentação interativa da API (a página `/api/docs/`).
- **requests**: biblioteca para fazer pedidos HTTP; será usada pelo programa cliente da Parte 6.

O `requirements.txt` fica assim:

```text
Django>=5.2,<6.0
Pillow
openpyxl
reportlab
python-dotenv
djangorestframework
drf-spectacular
requests
```

### Passo 2 — Configurar o projeto

**Arquivo:** `library/settings.py` · **Ação:** duas alterações

**2.1)** Acrescente três apps ao final do `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'catalog',  # o nosso app: sem esta linha o Django ignora models, templates e migrações dele
    'rest_framework',  # Django REST Framework: a API (Aula 8)
    'rest_framework.authtoken',  # tokens de acesso à API
    'drf_spectacular',  # documentação automática da API (/api/docs/)
]
```

**2.2)** No final do arquivo, acrescente a configuração da API:

```python
# ---------- API REST (Aula 8) ----------
REST_FRAMEWORK = {
    # Como a API descobre quem está fazendo o pedido:
    # 1) pelo token enviado no cabeçalho "Authorization: Token ..." (programas, aplicativos)
    # 2) pela sessão de login do site (útil para testar a API no navegador)
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    # Seguro por padrão: todo endpoint exige login, a não ser que a view libere
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    # Listas longas voltam em páginas de 10 itens: /api/livros/?page=2
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    # Quem gera a descrição da API para a documentação automática
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "API da Biblioteca",
    "DESCRIPTION": "API REST do sistema de biblioteca: acervo, categorias e empréstimos.",
    "VERSION": "1.0.0",
}
```

- **Seguro por padrão.** Com `IsAuthenticated` como padrão, se alguém esquecer de definir a permissão de uma view nova, ela exige login em vez de ficar aberta. As views que devem ser públicas dizem isso explicitamente.
- **Paginação.** A resposta das listas passa a ter o formato `{"count": 27, "next": "...?page=2", "previous": null, "results": [...]}`.

O app de tokens cria uma tabela nova, então rode:

```powershell
python manage.py migrate
```

---

## Parte 3 — As regras de empréstimo num lugar só

### Passo 3 — O módulo `services.py`

**Arquivo:** `catalog/services.py` · **Ação:** criar

```python
"""Regras de negócio dos empréstimos.

Ficam aqui, fora das views, porque são usadas em dois lugares:
pelas páginas do site (views.py) e pela API (api_views.py).
Assim a regra é escrita uma vez só, e as duas portas de entrada se comportam igual.
"""

from datetime import timedelta  # representa um intervalo de tempo (ex.: 14 dias)

from django.utils import timezone

from .models import Loan

LOAN_DAYS = 14  # prazo padrão de empréstimo, em dias


class LoanError(Exception):
    """Uma regra de empréstimo impediu a ação. A mensagem explica o motivo ao usuário."""


def borrow_book(book, user):
    """Cria um empréstimo do livro para o usuário e devolve o Loan criado.

    Levanta LoanError se alguma regra não for cumprida.
    """
    # Regra 1: precisa haver cópia disponível
    if book.copies_available == 0:
        raise LoanError(f"Não há cópias disponíveis de “{book.title}”.")

    # Regra 2: a pessoa não pode estar com este mesmo livro ainda sem devolver
    if book.loans.filter(user=user, returned_at__isnull=True).exists():
        raise LoanError(f"Você já está com “{book.title}”.")

    # Tudo certo: calcula o prazo e cria o empréstimo
    due_date = timezone.localdate() + timedelta(days=LOAN_DAYS)
    return Loan.objects.create(book=book, user=user, due_date=due_date)
```

#### Entendendo o código

- **`class LoanError(Exception)`** cria um tipo de erro próprio. Herdar de `Exception` é tudo o que é preciso: a classe fica vazia, e a mensagem é passada na hora de levantar o erro.
- **`raise LoanError("...")`** interrompe a função e avisa quem chamou que a regra não foi cumprida. A função não sabe se quem chamou é uma página ou a API, e nem precisa saber: cada um decide como mostrar o erro.

### Passo 4 — A view das páginas passa a usar o `services.py`

**Arquivo:** `catalog/views.py` · **Ação:** quatro alterações

**4.1)** No topo, apague a linha `from datetime import timedelta ...`. Ela passou para o `services.py`.

**4.2)** Logo abaixo da linha `from .reports import REPORTS ...`, acrescente:

```python
from . import services  # regras de empréstimo, compartilhadas com a API (Aula 8)
```

**4.3)** Apague a linha `LOAN_DAYS = 14 ...`, que também passou para o `services.py`.

**4.4)** Na view `borrow_book`, substitua tudo o que vem depois do `get_object_or_404` até a mensagem de sucesso, de modo que a view fique assim:

```python
def borrow_book(request, book_id):
    """Cria um empréstimo do livro para o usuário logado."""
    # Busca o livro pelo id; se não existir, responde 404 (página não encontrada)
    book = get_object_or_404(Book, pk=book_id)

    # As regras ficam em services.py (Aula 8): a API usa exatamente as mesmas
    try:
        loan = services.borrow_book(book, request.user)
    except services.LoanError as error:
        messages.error(request, str(error))  # a mensagem da regra que impediu o empréstimo
        return redirect("catalog:book_list")

    messages.success(request, f"Empréstimo feito! Devolva “{book.title}” até {loan.due_date:%d/%m/%Y}.")
    # Depois de um POST, sempre redirecionamos (padrão Post/Redirect/Get)
    return redirect("catalog:my_loans")
```

Os decorators `@login_required` e `@require_POST` acima da view continuam iguais.

- **`try` / `except`**: a view tenta fazer o empréstimo. Se o `services.py` levantar um `LoanError`, a view transforma o erro numa mensagem vermelha e volta para o acervo.
- **`str(error)`** é o texto passado ao `LoanError`, por exemplo "Não há cópias disponíveis de...".

Rode `python manage.py test`: os 39 testes devem continuar passando. É a prova de que a mudança de lugar não alterou o comportamento das páginas.

---

## Parte 4 — A API

### Passo 5 — Serializers

**Arquivo:** `catalog/serializers.py` · **Ação:** criar

```python
"""Serializers: convertem objetos do banco em JSON (e JSON recebido em objetos).

Cumprem na API o papel que o BaseModel do Pydantic cumpria no FastAPI:
descrevem os campos, validam os dados recebidos e montam as respostas.
"""

from rest_framework import serializers

from .models import Book, Category, Loan


class CategorySerializer(serializers.ModelSerializer):
    """Categoria em JSON: {"id": 1, "name": "Romance", "description": "..."}."""

    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class BookSerializer(serializers.ModelSerializer):
    """Livro em JSON. Os campos e as validações (ex.: ISBN único) vêm do model."""

    # Campo só de leitura: o nome da categoria, além do id que já vem no campo "category"
    category_name = serializers.CharField(source="category.name", read_only=True)
    # Campo calculado, também só de leitura: quantas cópias podem ser emprestadas agora
    available = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id", "title", "author", "isbn", "category", "category_name",
            "language", "publisher", "edition_year", "copies_total", "available",
        ]

    def get_available(self, obj) -> int:
        """Valor do campo "available" (o "-> int" ajuda a documentação a mostrar o tipo)."""
        # Na listagem, o valor já vem calculado do banco pelo annotate da filter_books.
        # Num livro recém-criado pela API ele não existe, então usamos a @property do model.
        if hasattr(obj, "available"):
            return obj.available
        return obj.copies_available


class LoanSerializer(serializers.ModelSerializer):
    """Empréstimo em JSON. Todos os campos são só de leitura: quem cria é a regra de negócio."""

    book_title = serializers.CharField(source="book.title", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)  # a @property do model Loan

    class Meta:
        model = Loan
        fields = ["id", "book", "book_title", "borrowed_at", "due_date", "returned_at", "is_overdue"]
        read_only_fields = ["book", "borrowed_at", "due_date", "returned_at"]
```

#### Entendendo o código

- **`ModelSerializer`** funciona como o `ModelForm` da Aula 5: lê os campos do model, com tipos e validações. O ISBN único, por exemplo, é validado sozinho: um ISBN repetido gera resposta 400 dizendo qual campo está errado.
- **`fields`** lista o que entra no JSON. O campo `image` ficou de fora de propósito: enviar arquivos por API é um assunto à parte.
- **`source="category.name"`** busca o valor seguindo a `ForeignKey`, como `book.category.name`. Se o livro não tiver categoria, o valor é `null`.
- **`read_only=True`**: o campo aparece nas respostas, mas é ignorado quando o cliente envia dados.
- **`SerializerMethodField`** calcula o valor chamando o método `get_<nome_do_campo>`, aqui `get_available`.
- **`read_only_fields`** no `LoanSerializer`: pela API ninguém escolhe prazo nem data de devolução. Quem define isso são as regras de negócio.

### Passo 6 — Permissão "leitura para todos, escrita para a equipe"

**Arquivo:** `catalog/permissions.py` · **Ação:** criar

```python
from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """Consultar (GET) é liberado para todos; criar, alterar e apagar só para a equipe.

    É o equivalente, na API, do nosso decorator staff_required das páginas.
    """

    def has_permission(self, request, view):
        # SAFE_METHODS são os métodos que só leem dados: GET, HEAD e OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
```

O DRF chama `has_permission` antes de cada operação. Se a resposta for `False`, ele responde **401** quando o pedido não identificou ninguém e **403** quando identificou alguém sem permissão.

**Uma decisão de projeto:** no site, o acervo só aparece para quem está logado. Na API, decidimos deixar a **consulta** do acervo aberta, como fazem muitas bibliotecas com catálogo público. Empréstimos e alterações continuam protegidos.

### Passo 7 — ViewSets

**Arquivo:** `catalog/api_views.py` · **Ação:** criar

```python
"""Views da API REST (Django REST Framework).

Cada ViewSet agrupa, numa classe só, as operações sobre um recurso
(listar, consultar, criar, alterar, apagar). O router, em api_urls.py,
transforma essas operações em endereços e métodos HTTP.
"""

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import services  # as mesmas regras de empréstimo usadas pelas páginas
from .models import Category, Loan
from .permissions import IsStaffOrReadOnly
from .serializers import BookSerializer, CategorySerializer, LoanSerializer
from .views import filter_books  # a mesma busca e os mesmos filtros do acervo


class BookViewSet(viewsets.ModelViewSet):
    """Livros do acervo.

    Um ModelViewSet já oferece as cinco operações do CRUD:
    GET /livros/, GET /livros/{id}/, POST /livros/, PUT e PATCH /livros/{id}/ e DELETE /livros/{id}/.
    """

    serializer_class = BookSerializer
    permission_classes = [IsStaffOrReadOnly]  # ler: todos; escrever: só a equipe

    def get_queryset(self):
        # Reaproveita a busca da Aula 4: /api/livros/?q=machado&disponivel=1&ordenar=author
        return filter_books(self.request.query_params)

    def destroy(self, request, *args, **kwargs):
        """DELETE /livros/{id}/: não apaga livros que já têm histórico de empréstimos."""
        book = self.get_object()
        if book.loans.exists():
            # 409 Conflict: o pedido é válido, mas entra em conflito com o estado atual dos dados
            return Response(
                {"detail": "Este livro tem histórico de empréstimos e não pode ser apagado."},
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)  # o comportamento padrão: apaga e responde 204

    @extend_schema(request=None, responses={201: LoanSerializer})
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def emprestar(self, request, pk=None):
        """POST /livros/{id}/emprestar/: empresta o livro para o usuário autenticado."""
        book = self.get_object()  # 404 se o livro não existir
        try:
            loan = services.borrow_book(book, request.user)
        except services.LoanError as error:
            return Response({"detail": str(error)}, status=status.HTTP_409_CONFLICT)
        return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Categorias (somente leitura): GET /categorias/ e GET /categorias/{id}/."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]  # qualquer pessoa pode consultar


class LoanViewSet(viewsets.ReadOnlyModelViewSet):
    """Os empréstimos do usuário autenticado: GET /emprestimos/ e GET /emprestimos/{id}/."""

    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ao gerar a documentação (/api/docs/) não há usuário logado: devolvemos uma consulta vazia
        if getattr(self, "swagger_fake_view", False):
            return Loan.objects.none()
        # Só os empréstimos de quem fez o pedido: o de outra pessoa responde 404
        return Loan.objects.filter(user=self.request.user).select_related("book")

    @extend_schema(request=None, responses={200: LoanSerializer})
    @action(detail=True, methods=["post"])
    def devolver(self, request, pk=None):
        """POST /emprestimos/{id}/devolver/: registra a devolução."""
        loan = self.get_object()
        if not loan.is_active:
            return Response({"detail": "Este livro já tinha sido devolvido."}, status=status.HTTP_409_CONFLICT)
        loan.mark_returned()  # a mesma regra usada pelas páginas e pelo Admin
        return Response(LoanSerializer(loan).data)
```

#### Entendendo o código: os tipos de ViewSet

| Classe | Operações | Usado em |
|---|---|---|
| `ModelViewSet` | listar, consultar, criar, alterar e apagar | livros |
| `ReadOnlyModelViewSet` | só listar e consultar | categorias e empréstimos |

**O que cada ViewSet precisa informar:**

- `serializer_class`: como converter para JSON;
- `get_queryset()` ou `queryset`: de onde vêm os dados;
- `permission_classes`: quem pode usar.

**O que foi reaproveitado das aulas anteriores:**

- `filter_books` (Aula 4): `/api/livros/?q=machado&categoria=2&ordenar=author` funciona igual à página do acervo;
- `services.borrow_book` (Passo 3): as regras de empréstimo;
- `mark_returned` (Aula 1): a devolução.

**Personalizações feitas nesta aula:**

- **`destroy`** foi sobrescrito para impedir que um livro com histórico seja apagado. Pelo `on_delete=CASCADE` da Aula 1, apagar o livro apagaria também os empréstimos dele. O `super().destroy(...)` chama o comportamento original quando o livro não tem histórico.
- **`@action(detail=True, methods=["post"])`** cria operações além do CRUD, com endereço próprio. `detail=True` significa "sobre um item específico", e por isso o endereço é `livros/{id}/emprestar/`. A própria action pode ter permissão diferente da do ViewSet: para emprestar basta estar logado.
- **`get_queryset` do `LoanViewSet`** filtra por `user=self.request.user`. É a mesma proteção da Aula 2: o empréstimo de outra pessoa "não existe" para quem pede, e a resposta é 404.
- **`@extend_schema(...)`** não muda o funcionamento. Ele só ajuda o drf-spectacular a descrever a operação na documentação: `request=None` indica que a operação não recebe corpo, e `responses` indica o que ela devolve.
- **`swagger_fake_view`** é um detalhe da documentação: quando o drf-spectacular gera a página `/api/docs/`, não há usuário logado, então devolvemos uma consulta vazia.

### Passo 8 — Rotas da API

**Arquivo:** `catalog/api_urls.py` · **Ação:** criar

```python
"""Endereços da API. Todos começam com /api/ (veja library/urls.py)."""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import permissions
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import APIRootView, DefaultRouter

from . import api_views

app_name = "api"


class PublicAPIRootView(APIRootView):
    """Página inicial da API (/api/), com os links dos recursos. Aberta a todos."""

    permission_classes = [permissions.AllowAny]


# O router cria as rotas de cada ViewSet automaticamente:
# livros/ e livros/{id}/, e também as @action, como livros/{id}/emprestar/
router = DefaultRouter()
router.APIRootView = PublicAPIRootView  # sem isto, a página inicial exigiria login
router.register("livros", api_views.BookViewSet, basename="livro")
router.register("categorias", api_views.CategoryViewSet, basename="categoria")
router.register("emprestimos", api_views.LoanViewSet, basename="emprestimo")

urlpatterns = [
    path("", include(router.urls)),
    # POST com usuário e senha devolve um token: {"token": "..."}
    path("token/", obtain_auth_token, name="token"),
    # Descrição da API no padrão OpenAPI e a página de documentação interativa (Swagger)
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api:schema"), name="docs"),
]
```

**Arquivo:** `library/urls.py` · **Ação:** acrescentar a rota da API logo abaixo da rota `contas/`

```python
    path("contas/", include("django.contrib.auth.urls")),
    # API REST (Aula 8): todos os endereços começam com /api/
    path("api/", include("catalog.api_urls")),
```

**Os endereços que o router criou:**

| Método | Endereço | Operação |
|---|---|---|
| GET | `/api/` | página inicial da API, com links |
| GET, POST | `/api/livros/` | listar, cadastrar |
| GET, PUT, PATCH, DELETE | `/api/livros/{id}/` | consultar, alterar, apagar |
| POST | `/api/livros/{id}/emprestar/` | emprestar |
| GET | `/api/categorias/`, `/api/categorias/{id}/` | listar, consultar |
| GET | `/api/emprestimos/`, `/api/emprestimos/{id}/` | os seus empréstimos |
| POST | `/api/emprestimos/{id}/devolver/` | devolver |
| POST | `/api/token/` | trocar usuário e senha por um token |
| GET | `/api/docs/` | documentação interativa |

A rota `api/` precisa vir **antes** da rota `""` (que inclui o `catalog.urls`). As duas não colidem hoje, mas manter as rotas mais específicas primeiro é um bom hábito.

---

## Parte 5 — Explorando a API

### Passo 9 — No navegador

Rode `python manage.py runserver` e acesse:

1. **<http://127.0.0.1:8000/api/>**: a **interface navegável** do DRF, com os links dos recursos. Clique em `livros`: aparece o JSON do acervo, formatado. Acrescente `?q=machado` à URL.
2. **<http://127.0.0.1:8000/api/docs/>**: a **documentação interativa** (Swagger), igual ao `/docs` do FastAPI. Abra `GET /api/livros/`, clique em **Try it out** e depois em **Execute**.
3. **Para usar operações que exigem login na documentação:**
   - abra `POST /api/token/`, clique em **Try it out**, preencha usuário e senha e clique em **Execute**;
   - copie o token da resposta;
   - clique no botão **Authorize** no topo da página e, no campo **tokenAuth**, escreva `Token ` seguido do token, por exemplo `Token 9944b0...`. A palavra `Token` e o espaço são obrigatórios;
   - agora experimente `POST /api/livros/{id}/emprestar/` e `GET /api/emprestimos/`.

Se você estiver logado no site no mesmo navegador, a interface navegável do DRF (item 1) já reconhece a sua sessão, sem token.

### Passo 10 — Pelo PowerShell

O PowerShell tem o comando `Invoke-RestMethod`, que faz pedidos HTTP e converte o JSON em objetos:

```powershell
# Buscar livros (não precisa de login)
$livros = Invoke-RestMethod "http://127.0.0.1:8000/api/livros/?q=machado"
$livros.results | Select-Object id, title, available

# Trocar usuário e senha por um token
$resposta = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/token/" -Body @{username = "maria"; password = "sua-senha"}
$cabecalho = @{Authorization = "Token $($resposta.token)"}

# Emprestar o livro 2 e listar os seus empréstimos (troque o 2 pelo id de um livro que apareceu na busca)
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/livros/2/emprestar/" -Headers $cabecalho
(Invoke-RestMethod "http://127.0.0.1:8000/api/emprestimos/" -Headers $cabecalho).results
```

Quando a API responde com erro (4xx), o `Invoke-RestMethod` mostra uma mensagem de erro vermelha com o JSON da resposta. Tente emprestar o mesmo livro duas vezes para ver o 409.

No **Windows PowerShell 5.1** (o que já vem no Windows), os acentos aparecem trocados, como "MemÃ³rias". A API está correta: é o PowerShell antigo que lê o texto com a codificação errada. No navegador, no cliente Python da Parte 6 ou no PowerShell 7, os acentos aparecem certos.

---

## Parte 6 — Testes da API

### Passo 11 — Escrever os testes

**Arquivo:** `catalog/tests.py` · **Ação:** acrescentar um import e uma classe no final

Logo abaixo da linha `from django.utils import timezone`, acrescente:

```python
from rest_framework.test import APIClient, APITestCase  # testes da API (Aula 8)
```

E no final do arquivo:

```python
class ApiTests(APITestCase):
    """Testes da Aula 8: a API REST.

    APITestCase é o TestCase do DRF: o self.client entende JSON e autenticação por token.
    """

    def setUp(self):
        self.maria = User.objects.create_user("maria", password="senha-forte-123")
        self.joao = User.objects.create_user("joao", password="senha-forte-123")
        self.equipe = User.objects.create_user("bibliotecaria", password="senha-forte-123", is_staff=True)
        self.romance = Category.objects.create(name="Romance")
        self.book = Book.objects.create(title="Dom Casmurro", author="Machado de Assis", isbn="1111111111111",
                                        copies_total=1, category=self.romance)
        Book.objects.create(title="Vidas Secas", author="Graciliano Ramos", isbn="2222222222222")

    # ---------- leitura pública ----------

    def test_lista_de_livros_e_publica_e_paginada(self):
        response = self.client.get("/api/livros/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)  # a paginação devolve o total...
        self.assertEqual(len(response.data["results"]), 2)  # ...e os itens da página em "results"

    def test_busca_na_api_usa_os_filtros_do_acervo(self):
        response = self.client.get("/api/livros/", {"q": "machado"})
        titulos = [livro["title"] for livro in response.data["results"]]
        self.assertEqual(titulos, ["Dom Casmurro"])

    def test_detalhe_do_livro(self):
        response = self.client.get(f"/api/livros/{self.book.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["category_name"], "Romance")
        self.assertEqual(response.data["available"], 1)

    def test_livro_inexistente_da_404(self):
        response = self.client.get("/api/livros/9999/")
        self.assertEqual(response.status_code, 404)

    # ---------- escrita: só a equipe ----------

    def test_visitante_nao_cadastra_livro(self):
        response = self.client.post("/api/livros/", {"title": "Novo", "author": "A", "isbn": "3333333333333"})
        self.assertEqual(response.status_code, 401)  # 401: não informou quem é

    def test_leitor_nao_cadastra_livro(self):
        self.client.force_authenticate(self.maria)
        response = self.client.post("/api/livros/", {"title": "Novo", "author": "A", "isbn": "3333333333333"})
        self.assertEqual(response.status_code, 403)  # 403: sabe quem é, mas não tem permissão

    def test_equipe_cadastra_altera_e_apaga_livro(self):
        self.client.force_authenticate(self.equipe)
        response = self.client.post("/api/livros/", {"title": "Iracema", "author": "José de Alencar",
                                                     "isbn": "3333333333333", "copies_total": 2}, format="json")
        self.assertEqual(response.status_code, 201)
        novo_id = response.data["id"]
        self.assertEqual(response.data["available"], 2)

        response = self.client.patch(f"/api/livros/{novo_id}/", {"copies_total": 4}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Book.objects.get(pk=novo_id).copies_total, 4)

        response = self.client.delete(f"/api/livros/{novo_id}/")
        self.assertEqual(response.status_code, 204)  # 204: apagado, resposta sem conteúdo
        self.assertFalse(Book.objects.filter(pk=novo_id).exists())

    def test_isbn_repetido_da_400(self):
        self.client.force_authenticate(self.equipe)
        response = self.client.post("/api/livros/", {"title": "X", "author": "Y", "isbn": "1111111111111"},
                                    format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("isbn", response.data)  # a resposta diz qual campo está errado

    def test_nao_apaga_livro_com_historico(self):
        make_loan(self.book, self.maria)
        self.client.force_authenticate(self.equipe)
        response = self.client.delete(f"/api/livros/{self.book.id}/")
        self.assertEqual(response.status_code, 409)
        self.assertTrue(Book.objects.filter(pk=self.book.id).exists())

    # ---------- empréstimos ----------

    def test_emprestar_pela_api(self):
        self.client.force_authenticate(self.maria)
        response = self.client.post(f"/api/livros/{self.book.id}/emprestar/")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["book_title"], "Dom Casmurro")
        self.assertTrue(Loan.objects.filter(user=self.maria, book=self.book).exists())

    def test_emprestar_sem_copias_da_409(self):
        make_loan(self.book, self.joao)  # a única cópia
        self.client.force_authenticate(self.maria)
        response = self.client.post(f"/api/livros/{self.book.id}/emprestar/")
        self.assertEqual(response.status_code, 409)
        self.assertIn("Não há cópias", response.data["detail"])

    def test_emprestar_exige_autenticacao(self):
        response = self.client.post(f"/api/livros/{self.book.id}/emprestar/")
        self.assertEqual(response.status_code, 401)

    def test_cada_um_ve_so_os_proprios_emprestimos(self):
        make_loan(self.book, self.maria)
        make_loan(Book.objects.get(isbn="2222222222222"), self.joao)
        self.client.force_authenticate(self.maria)
        response = self.client.get("/api/emprestimos/")
        self.assertEqual([e["book_title"] for e in response.data["results"]], ["Dom Casmurro"])

    def test_devolver_pela_api(self):
        loan = make_loan(self.book, self.maria)
        self.client.force_authenticate(self.maria)
        response = self.client.post(f"/api/emprestimos/{loan.id}/devolver/")
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data["returned_at"])

    def test_nao_devolve_emprestimo_de_outra_pessoa(self):
        loan = make_loan(self.book, self.joao)
        self.client.force_authenticate(self.maria)
        response = self.client.post(f"/api/emprestimos/{loan.id}/devolver/")
        self.assertEqual(response.status_code, 404)

    # ---------- token e documentação ----------

    def test_token_permite_usar_a_api(self):
        response = self.client.post("/api/token/", {"username": "maria", "password": "senha-forte-123"})
        self.assertEqual(response.status_code, 200)
        token = response.data["token"]
        # Um cliente novo, sem sessão: só o token no cabeçalho Authorization
        cliente = APIClient()
        cliente.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(cliente.get("/api/emprestimos/").status_code, 200)

    def test_senha_errada_nao_gera_token(self):
        response = self.client.post("/api/token/", {"username": "maria", "password": "errada"})
        self.assertEqual(response.status_code, 400)

    def test_pagina_inicial_da_api_e_publica(self):
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("livros", response.data)  # links para os recursos

    def test_documentacao_da_api(self):
        self.assertEqual(self.client.get("/api/docs/").status_code, 200)
        self.assertEqual(self.client.get("/api/schema/").status_code, 200)
```

#### Entendendo o código

- **`APITestCase`** e **`APIClient`** são as versões do DRF para `TestCase` e para o navegador simulado.
- **`response.data`** já traz a resposta como dicionário Python, sem precisar converter o JSON.
- **`force_authenticate(usuario)`** faz os pedidos seguintes como se viessem desse usuário, sem token nem senha. É o equivalente do `force_login` das aulas anteriores.
- **`format="json"`** envia os dados como JSON, como faria um aplicativo. Sem ele, o DRF envia como formulário.
- **`credentials(HTTP_AUTHORIZATION=...)`** coloca o cabeçalho `Authorization` em todos os pedidos daquele cliente. É assim que o teste do token prova o caminho completo: usuário e senha, depois token, depois acesso.

```powershell
python manage.py test
```

O resultado esperado é `Ran 58 tests ... OK`: os 39 anteriores e os 19 da API.

---

## Parte 7 — Um programa que consome a API

### Passo 12 — O cliente em Python

Até aqui, testamos a API com o navegador e com o PowerShell. Agora vamos escrever um programa Python independente, que não sabe nada de Django: ele só envia pedidos HTTP e lê as respostas. É o mesmo tipo de programa da aula "Consumindo uma API REST".

**Arquivo:** `cliente_api.py` (na pasta do projeto, ao lado do `manage.py`) · **Ação:** criar

```python
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
```

Com o servidor rodando num terminal, abra **outro terminal** (com o `.venv` ativo) e execute:

```powershell
python cliente_api.py
```

#### Entendendo o código

**As funções do `requests` usadas no cliente:**

| Função do `requests` | O que faz |
|---|---|
| `requests.get(url, params={...})` | pedido GET; o `params` vira `?q=...` na URL |
| `requests.post(url, data={...}, headers={...})` | pedido POST com dados e cabeçalhos |
| `resposta.status_code` | o código de status (200, 201, 404...) |
| `resposta.json()` | o corpo da resposta convertido em dicionário |
| `resposta.raise_for_status()` | levanta um erro se o status indicar falha |

**Outros detalhes:**

- **`timeout=10`** faz o programa desistir depois de 10 segundos sem resposta, em vez de ficar parado para sempre.
- **`getpass`** lê a senha sem mostrá-la na tela.
- **`if __name__ == "__main__":`** executa o `main()` só quando o arquivo é rodado diretamente. Se outro programa fizer `import cliente_api`, as funções ficam disponíveis sem que o menu comece sozinho.

---

## Parte 8 — Publicando a API

### Passo 13 — Atualizar o site publicado

É o ciclo de atualização da Aula 7, Parte 5. No seu computador:

```powershell
git add .
git commit -m "API REST com Django REST Framework"
git push
```

No console Bash do PythonAnywhere:

```bash
cd ~/biblioteca
source .venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Depois clique em **Reload** na aba **Web**. Os três comandos fazem diferença desta vez:

- o `pip install` instala o DRF;
- o `migrate` cria a tabela de tokens;
- o `collectstatic` copia o CSS da interface navegável do DRF.

Confira em `https://seunome.pythonanywhere.com/api/` e em `https://seunome.pythonanywhere.com/api/docs/`. Rode também o cliente apontando para o servidor:

```powershell
python cliente_api.py https://seunome.pythonanywhere.com/api
```

**Segurança:** o token vale como uma senha. Fora do computador local, use a API sempre por **HTTPS** (a opção **Force HTTPS** da Aula 7 garante isso) e nunca publique um token em código que vai para o GitHub.

---

## Parte 9 — FastAPI, DRF e Django Ninja lado a lado

O mesmo endpoint, "consultar um livro pelo id", escrito nas três ferramentas. Os trechos são **só para comparação**: não precisam ser digitados.

**FastAPI** (como no guia prático):

```python
@app.get("/livros/{livro_id}")
def buscar_livro(livro_id: int):
    for livro in livros:
        if livro["id"] == livro_id:
            return livro
    raise HTTPException(status_code=404, detail="Livro não encontrado")
```

**Django REST Framework** (esta aula): o `ModelViewSet` já inclui a consulta por id. Escrita à mão, ela ficaria assim:

```python
class BookDetail(generics.RetrieveAPIView):
    queryset = Book.objects.all()      # os dados vêm do banco
    serializer_class = BookSerializer  # o formato do JSON
    permission_classes = [permissions.AllowAny]
```

**Django Ninja** (alternativa com a sintaxe do FastAPI, dentro do Django):

```python
@api.get("/livros/{livro_id}", response=BookSchema)
def buscar_livro(request, livro_id: int):
    return get_object_or_404(Book, id=livro_id)
```

| | FastAPI | Django REST Framework | Django Ninja |
|---|---|---|---|
| Estilo | funções com decorators | classes (ViewSets, serializers) | funções com decorators |
| Banco e usuários | escolhidos à parte (SQLAlchemy, por exemplo) | os do Django | os do Django |
| Documentação `/docs` | pronta | com o drf-spectacular | pronta |
| Uso no mercado | muito alto, em APIs independentes | muito alto, em projetos Django | pequeno, em crescimento |
| Quando escolher | uma API nova, sem site Django | um sistema Django que precisa de API | um sistema Django, preferindo a sintaxe do FastAPI |

Não existe a "melhor" ferramenta, e sim a mais adequada ao contexto. Para um sistema que já é Django, como a nossa biblioteca, o DRF aproveita tudo o que foi construído nas sete aulas anteriores.

---

## Checkpoint

- [ ] `/api/` e `/api/docs/` abrem no navegador.
- [ ] `/api/livros/?q=machado` devolve só os livros de Machado de Assis.
- [ ] Pela documentação, com **Authorize**, você consegue emprestar e listar os seus empréstimos.
- [ ] Emprestar o mesmo livro duas vezes devolve 409, e sem login devolve 401.
- [ ] Um leitor comum recebe 403 ao tentar cadastrar livro; a equipe consegue.
- [ ] `python manage.py test` mostra 58 testes OK.
- [ ] O `cliente_api.py` funciona com o servidor local e com o site publicado.
- [ ] A API está no ar no PythonAnywhere.

---

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `No module named 'rest_framework'` | DRF não instalado | `pip install -r requirements.txt` com o `.venv` ativo |
| `no such table: authtoken_token` | Falta migrar | `python manage.py migrate` |
| 401 em tudo, mesmo com token | O cabeçalho está sem a palavra `Token` ou sem o espaço | O formato é `Authorization: Token <código>` |
| 403 **CSRF Failed** ao usar a interface navegável | Pedido feito por sessão sem o token CSRF | Recarregue a página do DRF antes de enviar, ou use o token |
| O Swagger mostra 401 depois de preencher o **Authorize** | Faltou `Token ` antes do código | Preencha `Token 9944b0...` |
| `NoReverseMatch ... 'api:schema'` | Falta `app_name = "api"` ou o nome da rota está diferente | Confira o Passo 8 |
| Acentos trocados no PowerShell | Limitação do Windows PowerShell 5.1 | Confira no navegador, no cliente Python ou no PowerShell 7 |
| `/api/` sem estilo no PythonAnywhere | Faltou o `collectstatic` depois da atualização | Rode `python manage.py collectstatic` e clique em **Reload** |
| O cliente mostra `ConnectionError` | O servidor não está rodando, ou o endereço está errado | Confira o `runserver` em outro terminal ou a URL passada ao cliente |

---

## Resumo

Criamos uma API REST para o sistema de biblioteca com o Django REST Framework: dados reais do banco, autenticação por token, permissões, documentação interativa, testes, um programa cliente e publicação no PythonAnywhere.

O que ficou de ideia principal:

- **Serializers** convertem models em JSON e validam o que chega, como o Pydantic no FastAPI.
- **ViewSets** reúnem as operações de um recurso, e o **router** cria os endereços. Com o **`@action`**, criamos operações além do CRUD.
- **Permissões** definem quem pode o quê: 401 quando ninguém se identificou e 403 quando falta permissão. A API é **segura por padrão**.
- **Token** identifica programas; **sessão** identifica o navegador.
- **Regras de negócio num lugar só** (`services.py`): as páginas e a API usam as mesmas.
- **Códigos de status** comunicam o resultado: 200, 201, 204, 400, 401, 403, 404 e 409.
- **Não existe ferramenta melhor em geral:** FastAPI, DRF e Django Ninja resolvem o mesmo problema em contextos diferentes.

---

## Exercícios

1. Crie o endpoint `GET /api/livros/{id}/avaliacoes/`, público, que devolve as avaliações de um livro (nome de quem avaliou, nota, comentário e data). Dica: um `ReviewSerializer` e uma `@action` no `BookViewSet`.
2. Limite a quantidade de pedidos: visitantes podem fazer até 100 pedidos por hora, e usuários logados até 1000. Passando do limite, a API deve responder **429 Too Many Requests**. Dica: procure por "throttling" na documentação do DRF.
3. No `cliente_api.py`, crie a função `exportar_csv()`, que percorre **todas** as páginas de `/api/livros/` (seguindo o campo `next` da resposta) e grava o acervo inteiro num arquivo `acervo.csv`.

---

## Perguntas para revisar

<details>
<summary>1. Qual o papel de um serializer? A que ele corresponde no FastAPI?</summary>

Converter objetos do banco em JSON para as respostas e validar o JSON recebido antes de gravar. No FastAPI, esse papel é do `BaseModel` do Pydantic.
</details>

<details>
<summary>2. Qual a diferença entre as respostas 401 e 403?</summary>

401: o pedido não informou quem está pedindo (sem token ou sessão). 403: a API sabe quem é, mas essa pessoa não tem permissão para a operação (um leitor tentando cadastrar livro, por exemplo).
</details>

<details>
<summary>3. Por que as regras de empréstimo foram para o <code>services.py</code>?</summary>

Porque as páginas e a API precisam das mesmas regras. Com a regra num lugar só, as duas se comportam igual e qualquer mudança vale para ambas. Se a regra fosse copiada, um dia as duas versões ficariam diferentes.
</details>

<details>
<summary>4. Por que a API responde 409 ao tentar emprestar um livro sem cópias, e não 400?</summary>

O 400 indica que os dados enviados estão errados. No empréstimo, o pedido está correto: o problema é o estado atual dos dados (não há cópia disponível). É um conflito com o estado do sistema, e para isso existe o 409.
</details>

<details>
<summary>5. Por que a API usa token e não só a sessão?</summary>

A sessão depende de um cookie de navegador, criado no login do site. Programas como aplicativos e scripts não passam pela tela de login: eles trocam usuário e senha por um token uma vez e depois enviam o token em cada pedido.
</details>

<details>
<summary>6. Quando você escolheria FastAPI em vez de DRF?</summary>

Para uma API nova e independente, sem um sistema Django por trás. Por exemplo, um serviço que só entrega dados ou resultados de um modelo de IA. Se o sistema já é Django, o DRF aproveita models, usuários, permissões e testes que já existem.
</details>

---

Próxima aula: [Aula 9 — Qualidade de código e concorrência](Aula_09_Qualidade_de_Codigo_e_Concorrencia.md).
