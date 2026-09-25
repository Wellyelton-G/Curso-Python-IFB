# Aula 4 — Categorias, busca avançada, histórico e exportação

Sistema de Biblioteca com Django · Aula 4 de 10 · [Roteiro do curso](README.md)

## Objetivos da aula

- **Evoluir os models** de um sistema que já tem dados: categoria, idioma, editora e ano.
- Criar um **comando próprio** (`python manage.py popular_acervo`) que cadastra um acervo de exemplo.
- **Refatorar** a busca numa função reaproveitável.
- Filtrar por **categoria, idioma e ano**, **ordenar** e oferecer uma página de **busca avançada**.
- Guardar o **histórico de buscas** de cada usuário (com `JSONField`).
- **Exportar** o resultado para **CSV** e **Excel**.
- Parte opcional: uma pequena **API JSON** e um **autocompletar** em JavaScript.

Ao final da aula, o acervo tem 27 livros em 5 categorias, filtros combináveis, histórico com o botão "Refazer" e download em planilha.

| Aula 1 | Aula 2 | Aula 3 | Aula 4 | Aula 5 | Aula 6 | Aula 7 | Aula 8 | Aula 9 | Aula 10 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Concluída | Concluída | Concluída | **Aula atual** | Contas e avaliações | Relatórios e banco | Publicação | API REST | Qualidade de código | Git em equipe |

## Antes de começar

- [ ] Ambiente virtual ativo.
- [ ] `python manage.py test` mostra 14 testes OK (Aula 3).
- [ ] Faça um commit no Git (ou uma cópia da pasta): hoje vamos mexer em muitos arquivos.

---

## Parte 1 — Conceitos

### 1.1 Mudar models quando o banco já tem dados

O banco já tem livros. Se criarmos um campo **obrigatório** (a categoria, por exemplo), que valor os livros antigos receberiam? O Django não tem como saber e pergunta durante o `makemigrations`.

O jeito mais simples é tornar os campos novos **opcionais**:

| Tipo de campo | Como deixar opcional | O que os livros antigos recebem |
|---|---|---|
| Texto (`CharField`) | `blank=True` | texto vazio `""` |
| Número ou data | `null=True, blank=True` | NULL |
| `ForeignKey` | `null=True, blank=True` | NULL (sem categoria) |

### 1.2 `on_delete=SET_NULL`

O que deve acontecer com os livros se alguém apagar a categoria "Romance"? Com `CASCADE`, os livros seriam apagados junto, o que não faz sentido aqui. Com `SET_NULL`, os livros continuam, só que sem categoria. Essa opção exige `null=True`.

### 1.3 `JSONField`

Para o histórico, queremos guardar **todos os filtros** de uma busca (`{"q": "python", "categoria": "3", "ordenar": "author"}`), e eles variam de uma busca para outra. O `JSONField` guarda um dicionário inteiro numa coluna.

### 1.4 Refatorar para não repetir código

A página do acervo e a exportação para Excel precisam da **mesma** lógica de filtros. Copiar e colar deixaria duas versões para manter, e um dia elas ficariam diferentes. Por isso vamos **extrair** essa lógica para uma função, `filter_books(params)`, e chamá-la nos dois lugares. É o princípio conhecido como **DRY** (*Don't Repeat Yourself*).

### 1.5 Como funciona um download

Uma view não precisa devolver HTML. Ela pode devolver qualquer tipo de arquivo, desde que avise o navegador:

```python
response = HttpResponse(content_type="text/csv")                        # "isto é um CSV"
response["Content-Disposition"] = 'attachment; filename="livros.csv"'  # "baixe com este nome"
```

---

## Parte 2 — Models e dados de exemplo

### Passo 1 — Instalar o openpyxl

O `openpyxl` gera arquivos do Excel.

```powershell
pip install openpyxl
```

E acrescente ao `requirements.txt`:

```text
Django>=5.2,<6.0
Pillow
openpyxl
```

### Passo 2 — Os models novos

Vamos criar `Category`, acrescentar quatro campos opcionais ao `Book` e criar `SearchQuery`. O `Loan` não muda.

**Arquivo:** `catalog/models.py` · **Ação:** substituir todo o conteúdo

```python
from urllib.parse import urlencode  # transforma um dicionário em texto de URL: {"q": "x"} -> "q=x"

from django.conf import settings  # dá acesso às configurações do projeto (settings.py)
from django.db import models  # classes base para criar models e campos
from django.utils import timezone  # datas e horas respeitando o TIME_ZONE do projeto


class Category(models.Model):
    """Gênero ou assunto de um livro (Romance, Tecnologia, História...)."""

    name = models.CharField("Nome", max_length=100, unique=True)  # não pode haver duas categorias iguais
    description = models.TextField("Descrição", blank=True)  # texto longo e opcional

    class Meta:
        ordering = ["name"]
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.name


class Book(models.Model):
    """Um título do acervo da biblioteca. Cada objeto vira uma linha da tabela catalog_book."""

    # Cada atributo abaixo vira uma coluna da tabela.
    # O primeiro texto de cada campo é o nome que aparece no Admin e nos formulários.
    title = models.CharField("Título", max_length=255)  # texto curto, até 255 caracteres
    author = models.CharField("Autor(a)", max_length=255)
    isbn = models.CharField("ISBN", max_length=13, unique=True)  # unique: o banco não aceita ISBN repetido
    copies_total = models.PositiveIntegerField("Cópias totais", default=1)  # inteiro >= 0; vale 1 se ninguém informar
    # Capa opcional: o arquivo é salvo em media/book_covers/ e o banco guarda só o caminho
    image = models.ImageField("Capa", upload_to="book_covers/", blank=True, null=True)

    # Campos da Aula 4. Todos são opcionais para não quebrar os livros que já estavam cadastrados.
    # SET_NULL: se a categoria for apagada, o livro continua existindo, só que sem categoria.
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="books",  # permite fazer categoria.books.all()
        verbose_name="Categoria",
    )
    language = models.CharField("Idioma", max_length=50, blank=True)
    publisher = models.CharField("Editora", max_length=150, blank=True)
    edition_year = models.PositiveSmallIntegerField("Ano de edição", null=True, blank=True)

    created_at = models.DateTimeField("Cadastrado em", auto_now_add=True)  # preenchido sozinho na criação

    class Meta:
        ordering = ["title"]  # ordem padrão das consultas: alfabética pelo título
        verbose_name = "Livro"  # nome no singular, usado pelo Admin
        verbose_name_plural = "Livros"  # nome no plural, usado pelo Admin

    def __str__(self):
        # Texto que representa o livro no Admin, no shell e nas listas
        return f"{self.title} — {self.author}"

    @property
    def copies_available(self):
        """Cópias que podem ser emprestadas agora (calculado, não é coluna do banco)."""
        # self.loans existe por causa do related_name="loans" definido no model Loan.
        # returned_at__isnull=True seleciona os empréstimos que ainda não foram devolvidos.
        active_loans = self.loans.filter(returned_at__isnull=True).count()
        # max(..., 0) garante que o resultado nunca seja negativo
        return max(self.copies_total - active_loans, 0)


class Loan(models.Model):
    """O empréstimo de um livro para um usuário. Um empréstimo nunca é apagado: ele é o histórico."""

    # ForeignKey liga cada empréstimo a UM livro (no banco, fica guardado o id do livro).
    # on_delete=CASCADE: se o livro for apagado, os empréstimos dele também são.
    # related_name="loans": permite fazer book.loans.all() para ver os empréstimos de um livro.
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="loans", verbose_name="Livro"
    )
    # O usuário vem do sistema de contas do próprio Django (settings.AUTH_USER_MODEL)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loans",  # permite fazer user.loans.all()
        verbose_name="Usuário",
    )
    borrowed_at = models.DateTimeField("Emprestado em", auto_now_add=True)  # data e hora do empréstimo
    due_date = models.DateField("Devolver até")  # só a data do prazo, sem hora
    # Vazio (NULL) enquanto o livro não voltar; preenchido na devolução
    returned_at = models.DateTimeField("Devolvido em", null=True, blank=True)

    class Meta:
        ordering = ["-borrowed_at"]  # o sinal de menos inverte a ordem: mais recentes primeiro
        verbose_name = "Empréstimo"
        verbose_name_plural = "Empréstimos"

    def __str__(self):
        status = "devolvido" if self.returned_at else "emprestado"
        return f"{self.book.title} para {self.user} ({status})"

    @property
    def is_active(self):
        """Verdadeiro enquanto o livro não foi devolvido."""
        return self.returned_at is None

    @property
    def is_overdue(self):
        """Verdadeiro se o livro ainda não voltou e o prazo já passou."""
        # localdate() devolve a data de hoje no fuso horário configurado no projeto
        return self.is_active and timezone.localdate() > self.due_date

    def mark_returned(self):
        """Registra a devolução (só na primeira vez)."""
        if self.returned_at is None:
            self.returned_at = timezone.now()  # data e hora atuais
            # update_fields grava só esta coluna, sem regravar o registro inteiro
            self.save(update_fields=["returned_at"])


class SearchQuery(models.Model):
    """Uma busca feita por um usuário, guardada para o histórico."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="searches",  # permite fazer user.searches.all()
        verbose_name="Usuário",
    )
    q = models.CharField("Texto buscado", max_length=255, blank=True)
    # JSONField guarda um dicionário inteiro, ex.: {"q": "python", "categoria": "3"}.
    # default=dict (sem parênteses): cada busca nova recebe o seu próprio dicionário vazio.
    params = models.JSONField("Filtros usados", default=dict, blank=True)
    created_at = models.DateTimeField("Feita em", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # buscas mais recentes primeiro
        verbose_name = "Busca"
        verbose_name_plural = "Buscas"

    def __str__(self):
        return f"{self.user} buscou “{self.q or '(só filtros)'}”"

    def as_querystring(self):
        """Transforma os filtros guardados de volta em texto de URL ('q=...&categoria=...')."""
        return urlencode(self.params)
```

#### Entendendo o código

- **`Category`** é simples: um nome único e uma descrição opcional (`TextField` é texto longo, sem limite de tamanho).
- **Campos novos do `Book`**: todos opcionais, pelo motivo visto na seção 1.1. O `PositiveSmallIntegerField` é um inteiro positivo pequeno (até 32767), suficiente para um ano.
- **`SearchQuery.params`** guarda o dicionário de filtros. Repare no `default=dict` **sem parênteses**: passamos a função `dict`, e o Django a chama para cada registro novo. Com `default={}`, todos os registros compartilhariam o mesmo dicionário, um erro clássico em Python.
- **`as_querystring()`** faz o caminho inverso: transforma o dicionário salvo em texto de URL (`q=python&ordenar=author`). É ele que permite o botão "Refazer" do histórico.

### Passo 3 — Migrar

```powershell
python manage.py makemigrations
python manage.py migrate
```

O `makemigrations` deve mostrar:

```text
Migrations for 'catalog':
  catalog\migrations\0002_category_book_edition_year_book_language_and_more.py
    + Create model Category
    + Add field edition_year to book
    + Add field language to book
    + Add field publisher to book
    + Add field category to book
    + Create model SearchQuery
```

O Django não fez nenhuma pergunta, porque todos os campos novos são opcionais. Os livros antigos continuam lá, sem categoria.

### Passo 4 — Atualizar o Admin

**Arquivo:** `catalog/admin.py` · **Ação:** substituir todo o conteúdo

```python
from django.contrib import admin

from .models import Book, Category, Loan, SearchQuery  # o ponto significa "deste mesmo app"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)  # a vírgula faz disto uma tupla de um item só


# O decorator @admin.register liga o model Book à classe de configuração logo abaixo
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # Colunas mostradas na lista de livros (pode incluir @property, como copies_available)
    list_display = ("title", "author", "category", "language", "edition_year",
                    "copies_total", "copies_available")
    # Filtros laterais por categoria e idioma
    list_filter = ("category", "language")
    # Campos pesquisados pela caixa de busca do Admin
    search_fields = ("title", "author", "isbn", "publisher")


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    # "atrasado" não é um campo: é o método definido mais abaixo nesta classe
    list_display = ("book", "user", "borrowed_at", "due_date", "returned_at", "atrasado")
    # Filtros que aparecem na lateral direita da lista
    list_filter = ("returned_at", "due_date")
    # Dois sublinhados "atravessam" a ForeignKey: busca no título do livro e no nome do usuário
    search_fields = ("book__title", "user__username")
    # Ações em massa disponíveis no menu "Ação" da lista
    actions = ["marcar_como_devolvido"]

    # boolean=True faz o Admin mostrar um ícone de sim/não em vez de True/False
    @admin.display(boolean=True, description="Atrasado?")
    def atrasado(self, obj):
        # obj é o empréstimo da linha que está sendo desenhada
        return obj.is_overdue

    @admin.action(description="Marcar como devolvido")
    def marcar_como_devolvido(self, request, queryset):
        # queryset contém os empréstimos que o usuário marcou na lista
        ativos = queryset.filter(returned_at__isnull=True)  # ignora os que já foram devolvidos
        total = ativos.count()
        for loan in ativos:
            loan.mark_returned()  # reaproveita a regra que está no model
        # Mensagem que aparece no topo da página do Admin
        self.message_user(request, f"{total} empréstimo(s) marcado(s) como devolvido(s).")


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ("user", "q", "created_at")
    list_filter = ("created_at",)
    search_fields = ("q", "user__username")
```

As mudanças em relação à Aula 1: `Category` e `SearchQuery` foram registrados, e o `BookAdmin` ganhou colunas e filtros por categoria e idioma.

### Passo 5 — Um comando próprio para popular o acervo

Cadastrar 27 livros à mão no Admin seria cansativo. O Django permite criar comandos próprios do `manage.py`, como os que já usamos (`runserver`, `migrate`). O nosso vai se chamar `popular_acervo`.

O Django só encontra o comando se ele estiver exatamente nesta estrutura, dentro do app:

```
catalog/
└── management/
    ├── __init__.py          ← arquivo vazio
    └── commands/
        ├── __init__.py      ← arquivo vazio
        └── popular_acervo.py
```

Crie as pastas e os arquivos vazios pelo terminal:

```powershell
mkdir catalog\management\commands
New-Item catalog\management\__init__.py, catalog\management\commands\__init__.py
```

Os arquivos `__init__.py`, mesmo vazios, indicam ao Python que a pasta é um pacote, ou seja, algo que pode ser importado.

**Arquivo:** `catalog/management/commands/popular_acervo.py` · **Ação:** criar

```python
from django.core.management.base import BaseCommand  # classe base de todo comando do manage.py

from catalog.models import Book, Category

# Dados de exemplo. Cada tupla: (título, autor, categoria, ano, idioma, cópias)
LIVROS = [
    ("Dom Casmurro", "Machado de Assis", "Romance", 1899, "Português", 3),
    ("Memórias Póstumas de Brás Cubas", "Machado de Assis", "Romance", 1881, "Português", 2),
    ("O Cortiço", "Aluísio Azevedo", "Romance", 1890, "Português", 2),
    ("Iracema", "José de Alencar", "Romance", 1865, "Português", 1),
    ("Capitães da Areia", "Jorge Amado", "Romance", 1937, "Português", 2),
    ("Vidas Secas", "Graciliano Ramos", "Romance", 1938, "Português", 2),
    ("A Hora da Estrela", "Clarice Lispector", "Romance", 1977, "Português", 1),
    ("Pride and Prejudice", "Jane Austen", "Romance", 1813, "Inglês", 1),
    ("Cien años de soledad", "Gabriel García Márquez", "Romance", 1967, "Espanhol", 1),
    ("1984", "George Orwell", "Ficção científica", 1949, "Português", 3),
    ("Admirável Mundo Novo", "Aldous Huxley", "Ficção científica", 1932, "Português", 2),
    ("Fahrenheit 451", "Ray Bradbury", "Ficção científica", 1953, "Português", 1),
    ("Duna", "Frank Herbert", "Ficção científica", 1965, "Português", 2),
    ("Eu, Robô", "Isaac Asimov", "Ficção científica", 1950, "Português", 1),
    ("Python Fluente", "Luciano Ramalho", "Tecnologia", 2015, "Português", 2),
    ("Código Limpo", "Robert C. Martin", "Tecnologia", 2008, "Português", 2),
    ("Entendendo Algoritmos", "Aditya Bhargava", "Tecnologia", 2016, "Português", 3),
    ("Pense em Python", "Allen B. Downey", "Tecnologia", 2012, "Português", 2),
    ("Automate the Boring Stuff with Python", "Al Sweigart", "Tecnologia", 2015, "Inglês", 1),
    ("Sapiens", "Yuval Noah Harari", "História", 2011, "Português", 2),
    ("O Povo Brasileiro", "Darcy Ribeiro", "História", 1995, "Português", 1),
    ("Raízes do Brasil", "Sérgio Buarque de Holanda", "História", 1936, "Português", 1),
    ("Casa-Grande & Senzala", "Gilberto Freyre", "História", 1933, "Português", 1),
    ("Reinações de Narizinho", "Monteiro Lobato", "Infantojuvenil", 1931, "Português", 2),
    ("Harry Potter e a Pedra Filosofal", "J. K. Rowling", "Infantojuvenil", 1997, "Português", 3),
    ("O Hobbit", "J. R. R. Tolkien", "Infantojuvenil", 1937, "Português", 2),
    ("Le Petit Prince", "Antoine de Saint-Exupéry", "Infantojuvenil", 1943, "Francês", 1),
]


class Command(BaseCommand):
    # Texto mostrado em: python manage.py help popular_acervo
    help = "Cadastra categorias e livros de exemplo (pode rodar várias vezes sem duplicar)."

    def handle(self, *args, **options):
        """Método chamado pelo Django quando o comando é executado."""
        # enumerate numera os livros a partir de 1; a tupla é desempacotada direto no for
        for numero, (titulo, autor, categoria, ano, idioma, copias) in enumerate(LIVROS, start=1):
            # Busca a categoria pelo nome ou cria se ainda não existir.
            # get_or_create devolve (objeto, criou?); o _ indica que não usaremos o segundo valor.
            cat, _ = Category.objects.get_or_create(name=categoria)

            # ISBN fictício, só para testes: 978 + número com 10 dígitos (9780000000001, ...)
            isbn = f"978{numero:010d}"

            # Procura o livro pelo ISBN: se existir, atualiza com os "defaults"; se não, cria.
            # Por isso o comando pode rodar várias vezes sem duplicar nada.
            _, criado = Book.objects.update_or_create(
                isbn=isbn,
                defaults={
                    "title": titulo,
                    "author": autor,
                    "category": cat,
                    "edition_year": ano,
                    "language": idioma,
                    "copies_total": copias,
                },
            )
            acao = "criado" if criado else "atualizado"
            self.stdout.write(f"{acao}: {titulo}")  # escreve no terminal

        # style.SUCCESS pinta a mensagem de verde no terminal
        self.stdout.write(self.style.SUCCESS(f"Pronto! {len(LIVROS)} livros no acervo de exemplo."))
```

#### Entendendo o código

- O comando é uma classe `Command` que herda de `BaseCommand`. O Django chama o método `handle` quando o comando é executado.
- `get_or_create` e `update_or_create` são o que permite rodar o comando várias vezes **sem duplicar dados**. Essa propriedade tem nome: **idempotência**.
- Os ISBNs `9780000000001` a `9780000000025` são os mesmos dos "Livros de teste" criados na Aula 3. Por isso, o comando **atualiza** esses livros (transformando-os em livros de verdade) em vez de criar outros.

Rode o comando:

```powershell
python manage.py popular_acervo
```

Rode de novo: agora todas as linhas dizem `atualizado` e nada foi duplicado.

---

## Parte 3 — As views

### Passo 6 — Views com filtros reaproveitáveis

As views ganham as constantes `ORDER_OPTIONS` e `SEARCH_FIELDS`, as funções auxiliares `filter_books` e `filter_choices`, uma nova `book_list` e quatro views novas: `advanced_search`, `search_history`, `export_books` e `book_suggestions`. As views de empréstimo e da equipe não mudam.

**Arquivo:** `catalog/views.py` · **Ação:** substituir todo o conteúdo

```python
import csv  # módulo do Python para escrever arquivos CSV
from datetime import timedelta  # representa um intervalo de tempo (ex.: 14 dias)
from functools import wraps  # ajuda a escrever decorators

from django.contrib import messages  # mensagens de retorno ("Empréstimo feito!")
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied  # gera a resposta 403 (proibido)
from django.core.paginator import Paginator  # divide listas em páginas
from django.db.models import Count, F, Q  # ferramentas para montar consultas
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Book, Category, Loan, SearchQuery

LOAN_DAYS = 14  # prazo padrão de empréstimo, em dias
BOOKS_PER_PAGE = 10  # quantos livros aparecem por página

# Opções de ordenação: valor que vai na URL -> (texto exibido, campos do order_by).
# O sinal de menos em "-edition_year" significa ordem decrescente.
ORDER_OPTIONS = {
    "title": ("Título (A–Z)", ["title"]),
    "author": ("Autor(a) (A–Z)", ["author", "title"]),
    "recent": ("Edição mais recente", ["-edition_year", "title"]),
    "available": ("Mais cópias disponíveis", ["-available", "title"]),
}

# Filtros que, se preenchidos, fazem a busca entrar no histórico
SEARCH_FIELDS = ["q", "title", "author", "publisher", "categoria", "idioma", "ano_min", "ano_max", "disponivel"]


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


def filter_books(params):
    """Aplica busca, filtros e ordenação.

    Recebe os parâmetros da URL (request.GET) e devolve um queryset de livros,
    já com o campo calculado `available` (cópias disponíveis).
    É usada pela listagem E pela exportação, para as duas mostrarem o mesmo resultado.
    """
    # Consulta base: traz a categoria junto (select_related) e calcula as cópias disponíveis
    books = Book.objects.select_related("category").annotate(
        available=F("copies_total") - Count("loans", filter=Q(loans__returned_at__isnull=True))
    )

    # Busca simples: um texto procurado em vários campos ao mesmo tempo (OU)
    q = params.get("q", "").strip()
    if q:
        books = books.filter(
            Q(title__icontains=q) | Q(author__icontains=q) | Q(isbn__icontains=q)
        )

    # Busca avançada: cada campo filtra só a sua coluna.
    # **{...} transforma o dicionário em argumento nomeado: {"author__icontains": "x"} -> author__icontains="x"
    for field in ["title", "author", "publisher"]:
        value = params.get(field, "").strip()
        if value:
            books = books.filter(**{f"{field}__icontains": value})

    # isdigit() ignora valores que não são números (ex.: ?categoria=abc)
    categoria = params.get("categoria", "")
    if categoria.isdigit():
        books = books.filter(category_id=int(categoria))

    # __iexact: igual, sem diferenciar maiúsculas de minúsculas
    idioma = params.get("idioma", "").strip()
    if idioma:
        books = books.filter(language__iexact=idioma)

    # __gte: maior ou igual; __lte: menor ou igual
    ano_min = params.get("ano_min", "")
    if ano_min.isdigit():
        books = books.filter(edition_year__gte=int(ano_min))

    ano_max = params.get("ano_max", "")
    if ano_max.isdigit():
        books = books.filter(edition_year__lte=int(ano_max))

    if params.get("disponivel") == "1":
        books = books.filter(available__gt=0)

    # Ordenação: só aceitamos valores do dicionário ORDER_OPTIONS; qualquer outro vira "title"
    order_key = params.get("ordenar", "title")
    if order_key not in ORDER_OPTIONS:
        order_key = "title"
    _, order_fields = ORDER_OPTIONS[order_key]  # pega só a lista de campos (ignora o texto)
    return books.order_by(*order_fields)  # o * espalha a lista em vários argumentos


def filter_choices():
    """Dados usados para montar os <select> dos formulários de busca."""
    return {
        "categories": Category.objects.all(),
        # values_list(..., flat=True) devolve uma lista simples; distinct() remove repetidos
        "languages": Book.objects.exclude(language="").values_list("language", flat=True)
                                 .distinct().order_by("language"),
        # Lista de pares (valor, texto) para as opções de ordenação
        "order_options": [(key, label) for key, (label, _) in ORDER_OPTIONS.items()],
    }


@login_required
def book_list(request):
    """Lista o acervo com busca, filtros, ordenação e paginação."""
    books = filter_books(request.GET)

    # Guarda no histórico, mas só na 1ª página e só se algum filtro foi usado
    used = {key: request.GET[key] for key in SEARCH_FIELDS if request.GET.get(key)}
    if used and "page" not in request.GET:
        params = request.GET.dict()  # todos os parâmetros da URL como dicionário comum
        SearchQuery.objects.create(user=request.user, q=used.get("q", ""), params=params)

    paginator = Paginator(books, BOOKS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "params": request.GET,  # para os campos do formulário "lembrarem" o que foi digitado
        **filter_choices(),  # espalha categories, languages e order_options no contexto
    }
    return render(request, "catalog/book_list.html", context)


@login_required
def advanced_search(request):
    """Formulário completo de busca. Ele envia os dados (GET) para a book_list."""
    return render(request, "catalog/advanced_search.html", filter_choices())


@login_required
def search_history(request):
    """As últimas 50 buscas do usuário logado."""
    # searches existe por causa do related_name do SearchQuery; [:50] limita a 50 resultados
    searches = request.user.searches.all()[:50]
    return render(request, "catalog/search_history.html", {"searches": searches})


@login_required
def export_books(request, file_format):
    """Baixa o resultado da busca atual em CSV ou Excel (mesmos filtros da listagem)."""
    books = filter_books(request.GET)
    header = ["Título", "Autor(a)", "ISBN", "Categoria", "Idioma", "Ano", "Disponíveis", "Total"]
    # Uma lista por livro, na mesma ordem do cabeçalho
    rows = [
        [b.title, b.author, b.isbn, b.category.name if b.category else "",
         b.language, b.edition_year or "", b.available, b.copies_total]
        for b in books
    ]

    if file_format == "csv":
        # content_type diz ao navegador o tipo do arquivo;
        # Content-Disposition "attachment" manda baixar em vez de abrir na tela
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="livros.csv"'
        response.write("\ufeff")  # "BOM": faz o Excel reconhecer os acentos
        writer = csv.writer(response, delimiter=";")  # ; é o separador que o Excel em português espera
        writer.writerow(header)
        writer.writerows(rows)
        return response

    if file_format == "xlsx":
        from openpyxl import Workbook  # importado aqui: só é necessário nesta parte

        workbook = Workbook()  # planilha nova
        sheet = workbook.active  # a primeira aba
        sheet.title = "Livros"
        sheet.append(header)  # append adiciona uma linha
        for row in rows:
            sheet.append(row)
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="livros.xlsx"'
        workbook.save(response)  # grava a planilha direto na resposta
        return response

    # Qualquer outro formato na URL: página não encontrada
    raise Http404("Formato desconhecido.")


@login_required
def book_suggestions(request):
    """API para o autocompletar: /api/sugestoes/?q=mach -> {"suggestions": [...]}"""
    q = request.GET.get("q", "").strip()
    suggestions = []
    if len(q) >= 2:  # só sugere a partir de 2 letras
        titles = Book.objects.filter(title__icontains=q).values_list("title", flat=True)[:5]
        authors = Book.objects.filter(author__icontains=q).values_list("author", flat=True).distinct()[:5]
        # dict.fromkeys junta as duas listas e remove repetidos mantendo a ordem
        suggestions = list(dict.fromkeys([*titles, *authors]))
    # JsonResponse devolve dados (JSON) em vez de uma página HTML
    return JsonResponse({"suggestions": suggestions})


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

#### Entendendo o código: `filter_books`

A função recebe os parâmetros da URL e aplica apenas os filtros preenchidos:

| Parâmetro | Filtro aplicado | Detalhe |
|---|---|---|
| `q=machado` | título, autor **ou** ISBN contém | igual à Aula 3 |
| `title=`, `author=`, `publisher=` | cada um na sua coluna | vêm da busca avançada |
| `categoria=3` | `category_id=3` | `.isdigit()` ignora valores como `?categoria=abc` |
| `idioma=inglês` | `language__iexact` | igual, sem diferenciar maiúsculas |
| `ano_min=1900` / `ano_max=2000` | `edition_year__gte` / `__lte` | maior ou igual / menor ou igual |
| `disponivel=1` | `available__gt=0` | igual à Aula 3 |
| `ordenar=author` | `order_by(...)` | veja abaixo |

Três recursos de Python aparecem aqui:

1. **Filtro com nome montado na hora.** `books.filter(**{f"{field}__icontains": value})`: quando `field` vale `"author"`, isso é o mesmo que `books.filter(author__icontains=value)`. O `**` desempacota o dicionário em argumentos nomeados, e assim um único `for` trata três campos.
2. **Ordenação por lista de opções.** Em vez de uma sequência de `if/elif`, o dicionário `ORDER_OPTIONS` liga o valor da URL ao texto e aos campos de ordenação. Um valor desconhecido (`?ordenar=qualquercoisa`) cai no padrão `"title"`. Assim, **nada que venha direto do usuário chega ao `order_by` sem conferência**.
3. **`**filter_choices()` dentro do contexto.** Espalha as chaves de outro dicionário (`categories`, `languages`, `order_options`) dentro do `context`.

#### Entendendo o código: histórico, busca avançada e exportação

- **Histórico.** A busca só é salva se algum filtro foi usado **e** não se trata de uma troca de página. Sem essa segunda condição, cada clique em "Próxima" geraria uma entrada repetida no histórico.
- **`advanced_search`** só mostra o formulário. Quem busca de fato é a `book_list`, porque o formulário é enviado para ela.
- **CSV.** A `HttpResponse` funciona como um arquivo aberto, e o `csv.writer` escreve direto nela. O separador é `;` porque é o que o Excel em português espera. O `"\ufeff"` é o **BOM**, um caractere invisível no início do arquivo que avisa ao Excel que o texto está em UTF-8. Sem ele, "Ficção" aparece como "FicÃ§Ã£o".
- **Excel.** O `openpyxl` monta a planilha linha a linha, e `workbook.save(response)` grava direto na resposta. O `import` fica dentro do `if`, então a biblioteca só é carregada quando alguém pede um Excel.
- **API de sugestões.** `JsonResponse` devolve dados, e não uma página: `{"suggestions": ["Machado de Assis"]}`. Um endereço feito para ser usado por programas (no nosso caso, o JavaScript do navegador) é o que chamamos de **API**.

### Passo 7 — URLs

**Arquivo:** `catalog/urls.py` · **Ação:** substituir todo o conteúdo

```python
from django.urls import path

from . import views

# Namespace do app: nos templates escrevemos {% url 'catalog:book_list' %}
app_name = "catalog"

urlpatterns = [
    # Página inicial: lista de livros
    path("", views.book_list, name="book_list"),
    path("busca-avancada/", views.advanced_search, name="advanced_search"),
    path("historico/", views.search_history, name="search_history"),
    # <str:file_format> captura um texto: /exportar/csv/ -> file_format="csv"
    path("exportar/<str:file_format>/", views.export_books, name="export_books"),
    # Endereço usado pelo JavaScript do autocompletar
    path("api/sugestoes/", views.book_suggestions, name="book_suggestions"),
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

---

## Parte 4 — Templates

### Passo 8 — Novos links no menu

**Arquivo:** `templates/base.html` · **Ação:** acrescentar duas linhas abaixo do link "Meus empréstimos"

```html
        <a href="{% url 'catalog:my_loans' %}">Meus empréstimos</a>
        <a href="{% url 'catalog:advanced_search' %}">Busca avançada</a>
        <a href="{% url 'catalog:search_history' %}">Histórico</a>
```

### Passo 9 — O acervo com filtros, exportação e autocompletar

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
        {# params é o request.GET enviado pela view: params.q é o texto buscado #}
        {# list="suggestions" liga o campo à lista de sugestões do autocompletar #}
        <input id="q" type="text" name="q" value="{{ params.q }}" placeholder="Ex.: Machado"
               list="suggestions" autocomplete="off">
        <datalist id="suggestions"></datalist>
      </div>
      <div>
        <label for="categoria">Categoria</label>
        <select id="categoria" name="categoria">
          <option value="">Todas</option>
          {% for category in categories %}
            {# Da URL tudo chega como texto ("3"); stringformat:"s" converte o id (3) em texto para comparar #}
            <option value="{{ category.id }}" {% if params.categoria == category.id|stringformat:"s" %}selected{% endif %}>
              {{ category.name }}
            </option>
          {% endfor %}
        </select>
      </div>
      <div>
        <label for="ordenar">Ordenar por</label>
        <select id="ordenar" name="ordenar">
          {# order_options é a lista de pares (valor, texto) montada na view #}
          {% for value, label in order_options %}
            <option value="{{ value }}" {% if params.ordenar == value %}selected{% endif %}>{{ label }}</option>
          {% endfor %}
        </select>
      </div>
    </div>
    <div class="actions">
      <label>
        <input type="checkbox" name="disponivel" value="1" {% if params.disponivel == "1" %}checked{% endif %}>
        Somente com cópias disponíveis
      </label>
      <button class="btn btn-primary" type="submit">Filtrar</button>
      <a class="btn" href="{% url 'catalog:book_list' %}">Limpar</a>
      <a href="{% url 'catalog:advanced_search' %}">Busca avançada »</a>
    </div>
  </form>

  <div class="actions">
    <span class="muted">{{ page_obj.paginator.count }} livro(s) encontrado(s).</span>
    <span class="spacer"></span>
    {# request.GET.urlencode repete os filtros atuais no link: o arquivo traz o mesmo resultado da tela #}
    <a class="btn" href="{% url 'catalog:export_books' 'csv' %}?{{ request.GET.urlencode }}">Baixar CSV</a>
    <a class="btn" href="{% url 'catalog:export_books' 'xlsx' %}?{{ request.GET.urlencode }}">Baixar Excel</a>
  </div>

  {# Tabela com os livros da página atual #}
  {% if page_obj %}
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Capa</th>
            <th>Título</th>
            <th>Autor(a)</th>
            <th>Categoria</th>
            <th>Ano</th>
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
              {# O idioma só aparece quando não é português #}
              <td>{{ book.title }}{% if book.language and book.language != "Português" %} <span class="muted">({{ book.language }})</span>{% endif %}</td>
              <td>{{ book.author }}</td>
              {# default mostra um travessão quando o valor está vazio #}
              <td>{{ book.category.name|default:"—" }}</td>
              <td>{{ book.edition_year|default:"—" }}</td>
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
        {# querystring copia os parâmetros atuais da URL e troca só o page #}
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

  <script>
    // Autocompletar: enquanto a pessoa digita, pedimos sugestões à nossa API
    (function () {
      const input = document.getElementById("q");
      const list = document.getElementById("suggestions");
      let timer;  // guarda o "cronômetro" da última tecla

      input.addEventListener("input", function () {
        clearTimeout(timer);  // cancela o pedido agendado pela tecla anterior
        const text = input.value.trim();
        if (text.length < 2) { list.innerHTML = ""; return; }  // menos de 2 letras: sem sugestões

        // Espera a pessoa parar de digitar por 300 ms antes de perguntar ao servidor
        timer = setTimeout(async function () {
          // encodeURIComponent protege acentos e espaços dentro da URL
          const url = "{% url 'catalog:book_suggestions' %}?q=" + encodeURIComponent(text);
          const response = await fetch(url);  // chama a API sem recarregar a página
          const data = await response.json();  // {"suggestions": [...]}
          list.innerHTML = "";  // limpa as sugestões antigas
          for (const suggestion of data.suggestions) {
            const option = document.createElement("option");
            option.value = suggestion;
            list.appendChild(option);
          }
        }, 300);
      });
    })();
  </script>
{% endblock %}
```

#### Entendendo o código

- A view agora envia `params` (o próprio `request.GET`), e o formulário lê `{{ params.q }}`, `params.categoria` etc. para lembrar os filtros.
- Tudo o que chega pela URL é **texto** (`"3"`), mas `category.id` é **número** (`3`), e `"3" == 3` é falso. Por isso o `|stringformat:"s"` converte o número em texto antes da comparação.
- Os links de download repetem os filtros atuais com `?{{ request.GET.urlencode }}`. Como a `export_books` também usa `filter_books`, o arquivo tem exatamente os livros da tela, sem paginação.
- **O autocompletar** (parte opcional) usa um `<datalist>`, a lista de sugestões nativa do HTML. A cada tecla, o JavaScript espera 300 ms sem digitação (técnica chamada *debounce*, que evita um pedido ao servidor por letra), chama a API com `fetch` e preenche a lista. Se preferir deixar o JavaScript para depois, apague o bloco `<script>`: o resto funciona igual.

### Passo 10 — Página de busca avançada

**Arquivo:** `templates/catalog/advanced_search.html` · **Ação:** criar

```html
{% extends "base.html" %}
{% block title %}Busca avançada · Biblioteca{% endblock %}
{% block content %}
  <h1>Busca avançada</h1>
  <p class="muted">Preencha só o que quiser usar. Os campos vazios são ignorados.</p>

  {# action aponta para a lista de livros: quem faz a busca é a book_list #}
  {# Os "name" dos campos são os mesmos parâmetros lidos pela função filter_books #}
  <form class="card" method="get" action="{% url 'catalog:book_list' %}">
    <div class="form-grid">
      <div>
        <label for="title">Título contém</label>
        <input id="title" type="text" name="title">
      </div>
      <div>
        <label for="author">Autor(a) contém</label>
        <input id="author" type="text" name="author">
      </div>
      <div>
        <label for="publisher">Editora contém</label>
        <input id="publisher" type="text" name="publisher">
      </div>
      <div>
        <label for="categoria">Categoria</label>
        <select id="categoria" name="categoria">
          <option value="">Todas</option>
          {% for category in categories %}
            <option value="{{ category.id }}">{{ category.name }}</option>
          {% endfor %}
        </select>
      </div>
      <div>
        <label for="idioma">Idioma</label>
        <select id="idioma" name="idioma">
          <option value="">Qualquer</option>
          {# languages traz apenas os idiomas que existem no acervo #}
          {% for language in languages %}
            <option value="{{ language }}">{{ language }}</option>
          {% endfor %}
        </select>
      </div>
      <div>
        <label for="ano_min">Ano de edição — de</label>
        <input id="ano_min" type="number" name="ano_min" placeholder="Ex.: 1900">
      </div>
      <div>
        <label for="ano_max">Ano de edição — até</label>
        <input id="ano_max" type="number" name="ano_max" placeholder="Ex.: 2000">
      </div>
      <div>
        <label for="ordenar">Ordenar por</label>
        <select id="ordenar" name="ordenar">
          {% for value, label in order_options %}
            <option value="{{ value }}">{{ label }}</option>
          {% endfor %}
        </select>
      </div>
    </div>
    <div class="actions">
      <label><input type="checkbox" name="disponivel" value="1"> Somente com cópias disponíveis</label>
      <button class="btn btn-primary" type="submit">Buscar</button>
      <a class="btn" href="{% url 'catalog:book_list' %}">Voltar</a>
    </div>
  </form>
{% endblock %}
```

O detalhe mais importante é o `action="{% url 'catalog:book_list' %}"`: o formulário é enviado para outra página. A busca avançada não tem lógica própria, só monta a URL certa para a `book_list`.

### Passo 11 — Página de histórico

**Arquivo:** `templates/catalog/search_history.html` · **Ação:** criar

```html
{% extends "base.html" %}
{% block title %}Histórico de buscas · Biblioteca{% endblock %}
{% block content %}
  <h1>Minhas buscas recentes</h1>

  {% if searches %}
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Quando</th>
            <th>Texto</th>
            <th>Filtros</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {% for search in searches %}
            <tr>
              <td>{{ search.created_at|date:"d/m/Y H:i" }}</td>
              <td>{{ search.q|default:"—" }}</td>
              <td class="muted">
                {# params é o dicionário do JSONField; .items percorre chave e valor, como no Python #}
                {% for key, value in search.params.items %}
                  {% if value and key != "q" %}{{ key }}={{ value }} {% endif %}
                {% endfor %}
              </td>
              {# as_querystring (método do model) remonta a URL da busca #}
              <td><a class="btn" href="{% url 'catalog:book_list' %}?{{ search.as_querystring }}">Refazer</a></td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  {% else %}
    <p class="muted">Você ainda não fez nenhuma busca.</p>
  {% endif %}
{% endblock %}
```

---

## Parte 5 — Testes

### Passo 12 — Testes da Aula 4

**Arquivo:** `catalog/tests.py` · **Ação:** duas alterações

**12.1)** Troque a linha de import dos models por:

```python
from .models import Book, Category, Loan, SearchQuery
```

**12.2)** Adicione esta classe no final do arquivo:

```python
class CatalogFiltersTests(TestCase):
    """Testes da Aula 4: filtros, ordenação, histórico e exportação."""

    def setUp(self):
        self.user = User.objects.create_user("maria", password="senha-forte-123")
        self.client.force_login(self.user)
        romance = Category.objects.create(name="Romance")
        tecnologia = Category.objects.create(name="Tecnologia")
        Book.objects.create(title="Dom Casmurro", author="Machado de Assis", isbn="1111111111111",
                            category=romance, language="Português", edition_year=1899)
        Book.objects.create(title="Python Fluente", author="Luciano Ramalho", isbn="2222222222222",
                            category=tecnologia, language="Português", edition_year=2015)
        Book.objects.create(title="Pride and Prejudice", author="Jane Austen", isbn="3333333333333",
                            category=romance, language="Inglês", edition_year=1813)
        self.romance = romance

    def titles(self, response):
        """Títulos que apareceram na página, na ordem em que apareceram."""
        return [book.title for book in response.context["page_obj"]]

    def test_filtro_por_categoria(self):
        response = self.client.get(reverse("catalog:book_list"), {"categoria": self.romance.id})
        self.assertEqual(self.titles(response), ["Dom Casmurro", "Pride and Prejudice"])

    def test_filtro_por_idioma_e_ano(self):
        # "português" em minúsculas: o filtro __iexact ignora maiúsculas
        response = self.client.get(reverse("catalog:book_list"), {"idioma": "português", "ano_min": "1900"})
        self.assertEqual(self.titles(response), ["Python Fluente"])

    def test_ordenar_por_edicao_mais_recente(self):
        response = self.client.get(reverse("catalog:book_list"), {"ordenar": "recent"})
        self.assertEqual(self.titles(response), ["Python Fluente", "Dom Casmurro", "Pride and Prejudice"])

    def test_busca_entra_no_historico(self):
        self.client.get(reverse("catalog:book_list"), {"q": "python"})
        busca = SearchQuery.objects.get(user=self.user)  # get falharia se não houvesse exatamente uma
        self.assertEqual(busca.q, "python")

    def test_abrir_a_lista_sem_filtros_nao_gera_historico(self):
        self.client.get(reverse("catalog:book_list"))
        self.assertEqual(SearchQuery.objects.count(), 0)

    def test_exportar_csv_respeita_os_filtros(self):
        response = self.client.get(reverse("catalog:export_books", args=["csv"]), {"q": "python"})
        conteudo = response.content.decode("utf-8")  # bytes -> texto
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("Python Fluente", conteudo)
        self.assertNotIn("Dom Casmurro", conteudo)

    def test_exportar_excel(self):
        response = self.client.get(reverse("catalog:export_books", args=["xlsx"]))
        self.assertEqual(response.status_code, 200)
        # Todo arquivo .xlsx é, por dentro, um arquivo ZIP, e arquivos ZIP começam com "PK"
        self.assertTrue(response.content.startswith(b"PK"))

    def test_sugestoes_devolvem_json(self):
        response = self.client.get(reverse("catalog:book_suggestions"), {"q": "mach"})
        self.assertEqual(response.json(), {"suggestions": ["Machado de Assis"]})
```

Rode:

```powershell
python manage.py test
```

O resultado esperado é `Ran 22 tests ... OK`: os 14 da Aula 3 e os 8 novos. Os testes antigos continuam passando mesmo depois da refatoração da `book_list`, e é justamente para isso que eles servem.

---

## Checkpoint

- [ ] O Admin tem os menus **Categorias** e **Buscas**, e a lista de livros mostra categoria, idioma e ano.
- [ ] `python manage.py popular_acervo` roda duas vezes sem duplicar livros.
- [ ] O acervo filtra por categoria e ordena por autor, por edição mais recente e por disponibilidade.
- [ ] A busca avançada filtra por idioma e faixa de anos.
- [ ] O histórico mostra as buscas, e o botão **Refazer** funciona.
- [ ] **Baixar CSV** e **Baixar Excel** trazem os mesmos livros da tela, com acentos corretos no Excel.
- [ ] (Opcional) Ao digitar "ma" na busca, aparecem sugestões.
- [ ] `python manage.py test` mostra 22 testes OK.

---

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `Unknown command: 'popular_acervo'` | Pasta ou `__init__.py` faltando, ou nome errado | Confira a estrutura do Passo 5 (`management/commands/`, no plural) |
| `No module named 'openpyxl'` | Biblioteca não instalada | `pip install openpyxl` com o `.venv` ativo |
| `makemigrations` pergunta *"Please select a fix"* | Algum campo novo ficou obrigatório | Confira `blank=True` / `null=True` nos campos novos |
| A categoria escolhida não fica marcada | Comparação de texto com número | Use `category.id\|stringformat:"s"` |
| CSV abre no Excel com `Ã§` | Falta o BOM | `response.write("\ufeff")` antes de escrever as linhas |
| Todas as colunas do CSV numa só no Excel | Separador errado | Use `delimiter=";"` |
| Histórico cheio de itens repetidos | Salvando também nas trocas de página | Confira o `"page" not in request.GET` |
| Sugestões não aparecem | Erro no JavaScript | Abra F12 → Console no navegador e leia a mensagem |

---

## Resumo

Acrescentamos categorias e novos dados aos livros, um acervo de exemplo carregado por comando, busca avançada, ordenação, histórico de buscas, exportação para CSV e Excel e uma pequena API com autocompletar.

O que ficou de ideia principal:

- **Evoluir models sem perder dados**: campos opcionais (`blank`/`null`) e `SET_NULL`.
- **Comando próprio** com `BaseCommand`, que pode rodar várias vezes graças a `get_or_create` e `update_or_create`.
- **Refatoração**: a lógica de filtros foi para `filter_books`, usada pela listagem e pela exportação.
- **Lista de valores permitidos**: a ordenação usa um dicionário de opções, sem passar a entrada do usuário direto ao banco.
- **`JSONField`** guarda os filtros, e `urlencode` os transforma de volta em URL.
- **Views que não devolvem HTML**: arquivos (com `Content-Type` e `Content-Disposition`) e JSON (`JsonResponse`).

---

## Exercícios

1. Acrescente a ordenação "Título (Z–A)" ao `ORDER_OPTIONS`. Quantas linhas do template precisaram mudar? Por quê?
2. Cadastre uma descrição para cada categoria no Admin e mostre-a como dica (`title`) nas opções do `<select>`.
3. Na página de histórico, crie um botão para apagar todo o histórico do usuário. É uma ação que altera dados, então use POST.
4. (Desafio) Acrescente ao `Book` o campo `pages` (número de páginas, opcional) e um filtro "até N páginas" na busca avançada. Percorra todo o caminho: model → migração → `filter_books` → template → teste.

---

## Perguntas para revisar

<details>
<summary>1. Por que os campos novos do <code>Book</code> são opcionais?</summary>

Porque o banco já tinha livros. Um campo obrigatório exigiria um valor para todos os livros antigos. Com `blank=True`/`null=True`, eles recebem vazio ou NULL e a migração roda sem perguntas.
</details>

<details>
<summary>2. Qual a diferença entre <code>on_delete=CASCADE</code> e <code>on_delete=SET_NULL</code>?</summary>

`CASCADE` apaga os registros ligados junto: se o livro for apagado, os empréstimos dele também são. `SET_NULL` mantém os registros e só desfaz a ligação: se a categoria for apagada, os livros ficam sem categoria.
</details>

<details>
<summary>3. Por que criamos a função <code>filter_books</code>?</summary>

Porque a mesma lógica é usada pela listagem e pela exportação. Com uma função só, as duas mostram sempre o mesmo resultado e qualquer ajuste é feito num lugar.
</details>

<details>
<summary>4. Por que não fazer simplesmente <code>books.order_by(request.GET["ordenar"])</code>?</summary>

Porque o usuário pode colocar qualquer coisa na URL: um campo inexistente derrubaria a página com erro 500, ou alguém poderia ordenar por campos indevidos. O `ORDER_OPTIONS` funciona como uma lista de valores permitidos.
</details>

<details>
<summary>5. O que é uma API JSON e como o autocompletar a usa?</summary>

É um endereço que devolve dados em JSON em vez de uma página HTML. Enquanto a pessoa digita, o JavaScript chama `/api/sugestoes/?q=...` com `fetch` e preenche o `<datalist>` com as sugestões, sem recarregar a página.
</details>

---

Próxima aula: [Aula 5 — Contas, detalhes e avaliações](Aula_05_Contas_Detalhes_e_Avaliacoes.md).
