# Aula 1 — Fundamentos, modelos e o painel Admin

Sistema de Biblioteca com Django · Aula 1 de 6 · [Roteiro do curso](README.md)

## Objetivos da aula

- Entender o que é o Django e como ele monta uma página.
- Preparar o ambiente virtual e instalar o Django.
- Criar o projeto `library` e o app `catalog`.
- Descrever os dados da biblioteca (livros e empréstimos) como classes Python, os **models**.
- Criar as tabelas do banco com as **migrações**.
- Cadastrar e consultar livros pelo **Django Admin** e pelo **shell**, ainda sem escrever nenhuma página.

Ao final da aula teremos um painel administrativo funcionando, onde já é possível cadastrar livros (com capa) e empréstimos.

| Aula 1 | Aula 2 | Aula 3 | Aula 4 | Aula 5 | Aula 6 |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **Aula atual** | Páginas e empréstimos | Equipe, busca e testes | Categorias e exportação | Contas e avaliações | Relatórios e banco |

---

## Parte 1 — Conceitos

### 1.1 O que é o Django

O Django é um **framework web** escrito em Python. Ele já resolve os problemas que todo sistema web tem (banco de dados, login, segurança, formulários) e deixa para nós apenas o que é específico do nosso sistema.

### 1.2 Como uma página é montada (padrão MTV)

Quando alguém acessa um endereço do sistema, o caminho é este:

```
 Navegador                               Django
┌──────────┐   1. pede /emprestimos/   ┌──────────────┐
│          │ ────────────────────────▶ │  urls.py     │  "Qual função cuida deste endereço?"
│          │                           └──────┬───────┘
│          │                                  ▼
│          │                           ┌──────────────┐   3. consulta   ┌──────────────┐
│          │                           │  VIEW        │ ──────────────▶ │  MODEL       │ ◀──▶ Banco de
│          │                           │  (views.py)  │ ◀────────────── │  (models.py) │      dados
│          │                           └──────┬───────┘   4. dados      └──────────────┘
│          │                                  ▼ 5. entrega os dados
│          │   6. devolve o HTML       ┌──────────────┐
│          │ ◀──────────────────────── │  TEMPLATE    │  "Monta o HTML com os dados"
└──────────┘                           │  (.html)     │
                                       └──────────────┘
```

| Camada | Arquivo | Responsabilidade | Na biblioteca, seria... |
|---|---|---|---|
| **M**odel | `models.py` | Como os dados são guardados | o arquivo de fichas |
| **T**emplate | arquivos `.html` | Como os dados aparecem na tela | o cartaz no mural |
| **V**iew | `views.py` | Recebe o pedido, consulta, decide e responde | o bibliotecário no balcão |
| URLs | `urls.py` | Liga cada endereço a uma view | a placa "Empréstimos: balcão 2" |

Nesta aula trabalhamos só com o **M**. Views, templates e URLs entram na Aula 2.

### 1.3 Projeto e app

- O **projeto** é o sistema inteiro. Guarda as configurações gerais (`settings.py`) e as URLs principais. O nosso vai se chamar `library`.
- Um **app** é um módulo com uma responsabilidade. Um projeto pode ter vários apps. O nosso vai se chamar `catalog` e vai cuidar do acervo e dos empréstimos.

### 1.4 ORM: conversando com o banco em Python

O Django tem um **ORM** (Object-Relational Mapper), que traduz Python para SQL. Cada classe vira uma tabela e cada objeto vira uma linha. Por exemplo:

```python
# Em Python: "livros cujo autor é Machado de Assis"
Book.objects.filter(author="Machado de Assis")
```

O Django transforma isso em algo como:

```sql
SELECT * FROM catalog_book WHERE author = 'Machado de Assis';
```

### 1.5 Migrações

As **migrações** são o histórico de mudanças do banco. Sempre que um model muda (classe nova, campo novo), rodamos dois comandos:

1. `makemigrations`: o Django compara os models com o histórico e **escreve** um arquivo descrevendo a mudança.
2. `migrate`: o Django **executa** essas mudanças no banco.

---

## Parte 2 — Preparando o ambiente

### Passo 1 — Conferir o Python

No PowerShell (ou no terminal do VS Code, com ``Ctrl+` ``):

```powershell
python --version
```

A versão deve ser `Python 3.10` ou mais nova. Se aparecer erro, instale o Python pelo site oficial e marque **"Add python.exe to PATH"** durante a instalação.

### Passo 2 — Criar a pasta do projeto

```powershell
cd $HOME\Documents
mkdir biblioteca
cd biblioteca
code .
```

O último comando abre a pasta no VS Code. Daqui em diante, use o terminal do VS Code, que já abre dentro da pasta `biblioteca`.

### Passo 3 — Criar e ativar o ambiente virtual

O **ambiente virtual** é uma pasta com uma instalação de Python só para este projeto. Assim, os pacotes deste projeto não se misturam com os de outros.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Com o ambiente ativo, aparece `(.venv)` no começo da linha do terminal.

> **Erro "a execução de scripts foi desabilitada neste sistema"?** Rode o comando abaixo uma vez e tente ativar de novo:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> No Linux ou no macOS, a ativação é `source .venv/bin/activate`.

Sempre que abrir um terminal novo, ative o ambiente de novo. Se aparecer `No module named django`, quase sempre o problema é o `(.venv)` desativado.

### Passo 4 — Instalar o Django e o Pillow

```powershell
python -m pip install --upgrade pip
pip install "Django>=5.2,<6.0" Pillow
```

O **Pillow** é uma biblioteca de imagens. O Django precisa dela para guardar as capas dos livros.

Crie na pasta `biblioteca` o arquivo **`requirements.txt`**. Ele lista as dependências do projeto: quem baixar o projeto instala tudo com `pip install -r requirements.txt`.

**Arquivo:** `requirements.txt` · **Ação:** criar

```text
Django>=5.2,<6.0
Pillow
```

Se você usa Git, crie também o **`.gitignore`**, com o que não deve ir para o repositório:

**Arquivo:** `.gitignore` · **Ação:** criar

```text
.venv/
__pycache__/
db.sqlite3
media/
```

---

## Parte 3 — Criando o projeto e o app

### Passo 5 — Criar o projeto `library`

```powershell
django-admin startproject library .
```

**Atenção ao ponto no final.** Ele indica "crie o projeto nesta pasta". Sem ele, o Django cria uma pasta a mais e os caminhos deste guia deixam de bater.

### Passo 6 — Criar o app `catalog`

```powershell
python manage.py startapp catalog
```

A pasta fica assim:

```
biblioteca/
├── .venv/                 ← ambiente virtual (não mexa)
├── catalog/               ← o nosso app
│   ├── migrations/        ← histórico de mudanças do banco
│   ├── admin.py           ← configuração do painel Admin
│   ├── apps.py
│   ├── models.py          ← os dados (livros, empréstimos)
│   ├── tests.py           ← testes automatizados (Aula 3)
│   └── views.py           ← a lógica das páginas (Aula 2)
├── library/               ← configurações do projeto
│   ├── settings.py
│   └── urls.py
├── manage.py              ← executa os comandos do Django
└── requirements.txt
```

Todo comando do Django começa com `python manage.py ...`.

### Passo 7 — Configurar o `settings.py`

**Arquivo:** `library/settings.py` · **Ação:** alterar três trechos

**7.1)** Na lista `INSTALLED_APPS`, adicione o nosso app no final:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'catalog',  # o nosso app: sem esta linha o Django ignora models, templates e migrações dele
]
```

**7.2)** Mais abaixo, troque o idioma e o fuso horário:

```python
LANGUAGE_CODE = 'pt-br'  # textos do Django (Admin, mensagens de erro) em português

TIME_ZONE = 'America/Sao_Paulo'  # datas e horas no horário de Brasília
```

**7.3)** Logo abaixo da linha `STATIC_URL = 'static/'`, adicione:

```python
# Arquivos enviados pelos usuários (ex.: capas dos livros)
MEDIA_URL = 'media/'  # endereço usado no navegador: /media/book_covers/capa.jpg
MEDIA_ROOT = BASE_DIR / 'media'  # pasta do computador onde os arquivos ficam guardados
```

`BASE_DIR` é a pasta do projeto (`biblioteca/`). O próprio Django a define no início do arquivo.

---

## Parte 4 — Os models: livros e empréstimos

### Passo 8 — Pensar antes de programar

O que a biblioteca precisa guardar?

```
┌──────────────────────┐          ┌──────────────────────┐          ┌──────────────┐
│ Book (livro)         │ 1      N │ Loan (empréstimo)    │ N      1 │ User         │
│──────────────────────│◀─────────│──────────────────────│─────────▶│ (do Django)  │
│ title       título   │          │ book       → Book    │          │ username     │
│ author      autor    │          │ user       → User    │          │ password     │
│ isbn        único    │          │ borrowed_at  quando  │          │ email ...    │
│ copies_total cópias  │          │ due_date     prazo   │          └──────────────┘
│ image        capa    │          │ returned_at  devol.  │
│ created_at           │          └──────────────────────┘
└──────────────────────┘
```

- Um **livro** (um título) pode ter várias cópias e muitos empréstimos ao longo do tempo: é uma relação de 1 para N.
- Cada **empréstimo** é de um livro para um usuário.
- O **usuário** não precisamos criar: o Django já traz o model `User`, com login e senha.
- O empréstimo está **ativo** enquanto `returned_at` estiver vazio. Na devolução preenchemos essa data. O empréstimo nunca é apagado, porque ele é o histórico.

### Passo 9 — Escrever os models

**Arquivo:** `catalog/models.py` · **Ação:** substituir todo o conteúdo

```python
from django.conf import settings  # dá acesso às configurações do projeto (settings.py)
from django.db import models  # classes base para criar models e campos
from django.utils import timezone  # datas e horas respeitando o TIME_ZONE do projeto


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
```

#### Entendendo o código

**Herança.** As duas classes herdam de `models.Model`. Por causa disso, `Book` e `Loan` já sabem salvar, apagar e consultar sem que a gente escreva nada disso.

**Tipos de campo usados:**

| Campo | Guarda | Observação |
|---|---|---|
| `CharField` | texto curto | `max_length` é obrigatório |
| `PositiveIntegerField` | inteiro maior ou igual a zero | |
| `ImageField` | caminho de uma imagem | exige o Pillow |
| `DateTimeField` | data e hora | `auto_now_add=True` preenche sozinho na criação |
| `DateField` | só a data | usado no prazo de devolução |
| `ForeignKey` | ligação com outra tabela | no banco, guarda o `id` do registro ligado |

**`blank=True` e `null=True`** costumam confundir:

- `blank=True` diz respeito ao **formulário**: o campo pode ficar vazio.
- `null=True` diz respeito ao **banco**: a coluna pode guardar NULL.

A capa e a data de devolução usam os dois, porque são realmente opcionais.

**`class Meta`** guarda configurações que não são colunas: a ordem padrão das consultas e os nomes em português usados no Admin.

**`__str__`** define como o objeto aparece quando vira texto. Sem ele, o Admin mostraria algo como `Book object (1)`.

**`@property`** permite usar um método como se fosse atributo: `book.copies_available`, sem parênteses. O valor **não fica guardado no banco**: ele é calculado na hora, contando os empréstimos ativos. O `__isnull` é um *lookup*. Os lookups sempre vêm depois de dois sublinhados, e vamos ver vários outros ao longo do curso (`__icontains`, `__lt`, `__gte`...).

**Por que colocar `mark_returned()` no model?** Porque assim a regra "devolver = preencher `returned_at`" fica num lugar só. O Admin, a página do leitor e a área da equipe vão usar o mesmo método.

### Passo 10 — Criar e aplicar as migrações

```powershell
python manage.py makemigrations
```

O resultado esperado é:

```text
Migrations for 'catalog':
  catalog\migrations\0001_initial.py
    + Create model Book
    + Create model Loan
```

Vale abrir o arquivo `catalog/migrations/0001_initial.py` para ver a "receita" que o Django escreveu a partir das classes. Não edite esse arquivo.

Agora aplique:

```powershell
python manage.py migrate
```

Aparecem várias linhas `Applying ... OK`. Além das nossas tabelas, o Django cria as dele (usuários, sessões, permissões). O banco fica no arquivo **`db.sqlite3`**, que acaba de aparecer na pasta.

O **SQLite** é um banco que cabe num único arquivo, ótimo para estudo e desenvolvimento. Na Aula 6 veremos como trocar para PostgreSQL.

---

## Parte 5 — O painel Admin

O Django traz um painel administrativo completo. Basta registrar os models nele.

### Passo 11 — Registrar os models

**Arquivo:** `catalog/admin.py` · **Ação:** substituir todo o conteúdo

```python
from django.contrib import admin

from .models import Book, Loan  # o ponto significa "deste mesmo app"


# O decorator @admin.register liga o model Book à classe de configuração logo abaixo
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # Colunas mostradas na lista de livros (pode incluir @property, como copies_available)
    list_display = ("title", "author", "isbn", "copies_total", "copies_available")
    # Campos pesquisados pela caixa de busca do Admin
    search_fields = ("title", "author", "isbn")


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
```

#### Entendendo o código

- **`@admin.register(Book)`** é um *decorator*: uma função que recebe a classe logo abaixo e a registra no Admin.
- **`list_display`**, **`search_fields`** e **`list_filter`** configuram a tela de listagem: colunas, caixa de busca e filtros laterais.
- **`book__title`**: os dois sublinhados seguem a `ForeignKey`, então a busca acontece no título do livro do empréstimo.
- **`atrasado`** é uma coluna calculada. O `@admin.display(boolean=True)` troca "True/False" por um ícone.
- **`actions`** cria ações em massa. Você marca vários empréstimos, escolhe "Marcar como devolvido" e clica em "Ir". A ação usa o `mark_returned()` do model.

### Passo 12 — Criar o superusuário

O **superusuário** pode fazer tudo no Admin.

```powershell
python manage.py createsuperuser
```

Informe um nome de usuário (por exemplo, `admin`), um e-mail (pode deixar em branco) e a senha duas vezes. A senha não aparece enquanto você digita, o que é normal. Se o Django reclamar que a senha é simples demais, ele pergunta se você quer usá-la mesmo assim. Num projeto de estudo, pode responder `y`.

### Passo 13 — Rodar o servidor e explorar o Admin

```powershell
python manage.py runserver
```

Acesse <http://127.0.0.1:8000/admin/> e entre com o superusuário.

O terminal fica ocupado pelo servidor. Para parar, use `Ctrl+C`. Para rodar outros comandos ao mesmo tempo, abra outro terminal (botão **+** do terminal do VS Code) e ative o `.venv` nele.

Faça o seguinte:

1. Em **Livros → Adicionar**, cadastre três livros. Em pelo menos um, envie uma imagem de capa.
2. Observe as colunas **Cópias totais** e **copies available** na lista de livros.
3. Em **Usuários → Adicionar**, crie um usuário comum chamado `maria`. **Anote a senha**: vamos usá-la na Aula 2.
4. Em **Empréstimos → Adicionar**, empreste um livro para a `maria`. Volte à lista de livros: as cópias disponíveis diminuíram.
5. Crie outro empréstimo com **Devolver até** numa data passada. Na coluna **Atrasado?**, o ícone muda.
6. Selecione esse empréstimo, escolha **Marcar como devolvido** no menu de ações e clique em **Ir**.

A pasta `media/book_covers/` apareceu com a imagem enviada. Ainda não dá para abrir a imagem pelo link do Admin. Isso é esperado e será resolvido na Aula 2.

---

## Parte 6 — O shell: consultando o banco em Python

O **shell do Django** é um terminal Python que já conhece o projeto. É o melhor lugar para experimentar o ORM.

### Passo 14 — Explorar o ORM

Com o `.venv` ativo:

```powershell
python manage.py shell
```

Digite linha por linha (o que vem depois de `#` é comentário e não precisa ser digitado):

```python
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from catalog.models import Book, Loan

# CRIAR
livro = Book.objects.create(title="Dom Casmurro", author="Machado de Assis", isbn="9788535910663", copies_total=2)
livro                      # <Book: Dom Casmurro — Machado de Assis>   (é o __str__!)

# LER
Book.objects.all()                                # todos os livros
Book.objects.count()                              # quantos livros
Book.objects.filter(author__icontains="machado")  # autor contém "machado" (ignora maiúsculas)
Book.objects.get(isbn="9788535910663")            # exatamente UM livro

# RELACIONAMENTOS
maria = User.objects.get(username="maria")        # o usuário que você criou no Admin
prazo = timezone.localdate() + timedelta(days=14)
emp = Loan.objects.create(book=livro, user=maria, due_date=prazo)
livro.copies_available     # 1  (2 cópias - 1 empréstimo ativo)
livro.loans.all()          # empréstimos DESTE livro (related_name="loans")
maria.loans.count()        # empréstimos DESTA pessoa

# ATUALIZAR
emp.mark_returned()
livro.copies_available     # 2 de novo
livro.copies_total = 3
livro.save()               # grava a mudança no banco

exit()
```

Se `User.objects.get(username="maria")` der `DoesNotExist`, o usuário não foi criado no Passo 13 ou foi criado com outro nome. Se o `create` do livro der `UNIQUE constraint failed`, é porque já existe um livro com esse ISBN: troque um dígito.

| Código | O que faz | Devolve |
|---|---|---|
| `Model.objects.all()` | todos os registros | um QuerySet (uma espécie de lista de objetos) |
| `.filter(campo=valor)` | só os que atendem à condição | QuerySet |
| `.get(campo=valor)` | exatamente um registro (erro se achar zero ou mais de um) | um objeto |
| `.create(...)` | cria e já salva | o objeto criado |
| `.count()` | conta, direto no banco | um número |
| `obj.save()` | grava as alterações de um objeto | — |

Os QuerySets são **preguiçosos** (*lazy*): o Django só consulta o banco quando os dados são realmente usados, por exemplo num `for` ou ao imprimir. Por isso dá para encadear `.filter().filter().order_by()` sem custo.

---

## Checkpoint

- [ ] `python manage.py check` responde `System check identified no issues`.
- [ ] O Admin abre em <http://127.0.0.1:8000/admin/> e aceita o login do superusuário.
- [ ] Os menus **Livros** e **Empréstimos** aparecem em português.
- [ ] É possível cadastrar um livro com capa, e a imagem aparece em `media/book_covers/`.
- [ ] As cópias disponíveis diminuem quando um empréstimo é criado.
- [ ] A ação **Marcar como devolvido** funciona.
- [ ] O roteiro do shell (Passo 14) foi feito.

---

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `No module named django` | Ambiente virtual desativado | `.\.venv\Scripts\Activate.ps1` |
| `Cannot use ImageField because Pillow is not installed` | Falta o Pillow | `pip install Pillow` |
| `no such table: catalog_book` | Migrações não aplicadas | `python manage.py makemigrations` e `python manage.py migrate` |
| `No changes detected` no `makemigrations` | App fora do `INSTALLED_APPS` ou arquivo não salvo | Confira o Passo 7.1 e salve com `Ctrl+S` |
| Models não aparecem no Admin | Erro no `admin.py` ou arquivo não salvo | Leia o terminal do `runserver`: o erro aparece lá |
| `That port is already in use` | Já existe um `runserver` aberto | Feche o outro terminal ou use `python manage.py runserver 8001` |
| `UNIQUE constraint failed: catalog_book.isbn` | ISBN repetido | Use outro ISBN. É a regra `unique=True` funcionando |

---

## Resumo

Nesta aula criamos o projeto `library` e o app `catalog`, descrevemos livros e empréstimos como classes (`Book` e `Loan`), geramos as tabelas com as migrações e ganhamos um painel administrativo completo.

O que ficou de ideia principal:

- **Model** é uma classe que herda de `models.Model`, e cada atributo vira uma coluna.
- **Relações** entre tabelas são feitas com `ForeignKey`.
- **Valores calculados** ficam em `@property`, e **regras** ficam em métodos do model.
- **Toda mudança nos models** passa por `makemigrations` e depois `migrate`.
- **O Admin** é configurado com classes `ModelAdmin`.

---

## Exercícios

1. Acrescente a linha `list_filter = ("author",)` ao `BookAdmin`. O que muda na tela?
2. No shell, liste só os livros com mais de uma cópia. Dica: o lookup `__gt` significa "maior que".
3. No shell, descubra quantos empréstimos **ativos** existem no sistema.
4. (Desafio) Adicione ao `Book` o campo opcional `pages` (número de páginas) com `models.PositiveIntegerField("Páginas", null=True, blank=True)`. Rode `makemigrations` e `migrate` e confira o campo no Admin.

---

## Perguntas para revisar

<details>
<summary>1. Qual a diferença entre projeto e app?</summary>

O projeto (`library`) é o sistema inteiro, com as configurações e as URLs principais. O app (`catalog`) é um módulo com uma responsabilidade, que tem os próprios models, views e templates. Um projeto pode ter vários apps.
</details>

<details>
<summary>2. Por que existem dois comandos, <code>makemigrations</code> e <code>migrate</code>?</summary>

O primeiro escreve um arquivo descrevendo a mudança, e o segundo aplica essa mudança no banco. Separar os dois permite revisar e versionar (no Git) as mudanças do banco e aplicá-las depois em outros computadores.
</details>

<details>
<summary>3. Por que <code>copies_available</code> não é uma coluna do banco?</summary>

Porque é um valor calculado a partir de outros (cópias totais menos empréstimos ativos). Se fosse uma coluna, teríamos que atualizá-la a cada empréstimo e devolução, e ela poderia ficar errada. Calculando na hora, o valor está sempre certo.
</details>

<details>
<summary>4. O que o <code>related_name="loans"</code> permite fazer?</summary>

Percorrer a relação no sentido contrário: a partir de um livro, `book.loans.all()` lista os empréstimos dele. O mesmo vale para `user.loans.all()`.
</details>

<details>
<summary>5. Qual a diferença entre <code>blank=True</code> e <code>null=True</code>?</summary>

`blank` trata da validação do formulário (pode ficar vazio?). `null` trata do banco (a coluna aceita NULL?).
</details>

---

Próxima aula: [Aula 2 — Login, páginas e empréstimos](Aula_02_Login_Paginas_e_Emprestimos.md).
