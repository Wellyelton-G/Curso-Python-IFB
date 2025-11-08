# Guia de Melhorias a serem Implementadas no sistema — Aula 07/11

## Indíce

1. [Introdução e Visão Geral](#introdução-e-visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Preparação do Ambiente](#preparação-do-ambiente)
4. [Editar os Modelos (models.py)](#parte-2-editar-os-modelos-modelspy)
5. [Editar as Views (views.py)](#parte-3-editar-as-views-viewspy)
6. [Configurar as URLs (urls.py)](#parte-4-configurar-as-urls-urlspy)
7. [Editar os Templates (HTML)](#parte-5-editar-os-templates-html)
8. [Configurar o Admin, Exportação e Testes](#parte-6-configurar-o-admin-exportação-e-testes)
9. [Dicas de Resolução de Problemas](#dicas-de-resolução-de-problemas)
10. [Comandos Úteis (PowerShell)](#anexo-comandos-úteis-powershell)
11. [Finalização](#fim-do-guia)

---

Este documento visa demonstrar **EXATAMENTE ONDE e COMO** inserir cada código para implementar todas as melhorias no sistema de biblioteca. Siga as instruções linha por linha .Este documento descreve o que foi implementado no sistema de biblioteca e mostra **ONDE e COMO** inserir cada código, linha por linha.


## O que será implementado após seguir essa guia ## Visão geral 



Busca básica com destaques e autocomplete  Busca básica com destaques e autocomplete  

Busca avançada (campos separados + filtros)  Busca avançada (campos separados + filtros)  

Filtros: disponibilidade, categoria, idioma, faixa de ano  Filtros por disponibilidade, categoria, idioma e faixa de ano  

Ordenação por título, autor ou disponibilidade  Ordenação por título, autor ou disponibilidade  

Paginação (20 itens) ou todos  Paginação (20 itens) ou exibição de todos  

Exportação CSV e Excel  Exportação dos resultados e do histórico (CSV e Excel)  

Histórico de buscas  Histórico de buscas por usuário/sessão  

Cadastro de usuário  Cadastro de usuário (signup)  

Recuperação de senha  Recuperação de senha (password reset)  

Admin aprimorado  Ajustes no Admin (categorias e histórico cadastrados, filtros extras)



------



## PRÉ-REQUISITOS

## O que você precisa antes de começar

- Windows 10/11

- Python 3.8+ instalado (https://www.python.org/downloads/)- Windows 10/11

- VS Code instalado (https://code.visualstudio.com/)- Python instalado (https://www.python.org/downloads/)

- Projeto Django já criado com apps `catalog` e `library`- VS Code (opcional, recomendado)

- Internet para baixar dependências

---



##  PARTE 1: PREPARAÇÃO DO AMBIENTE## Passo a passo 



### Passo 1: Abrir o PowerShell na pasta do projeto. Siga na ordem os comandos abaixo são para o PowerShell do Windows.



**Opção A:** Pelo Explorador de Arquivos### 1) Abrir a pasta do projeto

1. Abra o Explorador de Arquivos

2. Navegue até: `C:\Users\seu-usuário\local_onde_criou_o_projeto\Django````powershell

3. Clique com botão direito numa área vaziacd C:\Users\seu_usuario\caminho_onde_esta_salvo_o_seu_projeto

4. Escolha "Abrir no Terminal" ou "Abrir janela do PowerShell aqui"```



**Opção B:** Digitando no PowerShell### 2) Criar e ativar o ambiente virtual (uma vez)

```powershell

cd C:\Users\seu-usuário\local_onde_criou_o_projeto\Django```powershell

```python -m venv .venv

.\.venv\Scripts\Activate.ps1

---```



### Passo 2: Criar e ativar ambiente virtualSe já existir, basta ativar:

```powershell

**2.1) Criar (apenas primeira vez):**.\.venv\Scripts\Activate.ps1

```powershell```

python -m venv .venv

```### 3) Instalar dependências



**2.2) Ativar (sempre que abrir novo terminal):**O arquivo `requirements.txt` já inclui tudo (Django, Pillow, tzdata, openpyxl):

```powershell```powershell

.\.venv\Scripts\Activate.ps1pip install -r requirements.txt

``````



** Como saber se funcionou?**  ### 4) Aplicar migrações do banco de dados

O prompt vai mostrar `(.venv)` no início.

```powershell

** Erro "execução de scripts desabilitada"?**  python manage.py migrate

Execute isso primeiro:```

```powershell

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUserSe você alterou os modelos (models.py) e ainda não gerou migrações:

``````powershell

Depois tente ativar novamente.python manage.py makemigrations

python manage.py migrate

---```



### Passo 3: Atualizar requirements.txt### 5) Rodar o servidor



**3.1) Abra o arquivo `requirements.txt` no VS Code**```powershell

python manage.py runserver

Localize na raiz do projeto: `C:\Users\seu-usuário\local_onde_criou_o_projeto\Django\requirements.txt````



**3.2) Substitua TODO o conteúdo por:**Acesse no navegador:

```- Lista de livros (busca básica): http://127.0.0.1:8000/

asgiref==3.10.0- Busca avançada: http://127.0.0.1:8000/advanced-search/

Django==5.2.7- Histórico de buscas: http://127.0.0.1:8000/me/searches/

pillow==12.0.0- Cadastro (signup): http://127.0.0.1:8000/signup/

sqlparse==0.5.3- Esqueci a senha: http://127.0.0.1:8000/password_reset/

tzdata==2025.2- Admin (se tiver superusuário): http://127.0.0.1:8000/admin/

openpyxl==3.1.5

```> Dica: crie um usuário admin com `python manage.py createsuperuser`.



**3.3) Salve o arquivo** (Ctrl+S)

## Como essas melhorias foram feitas (guia para replicar em outro projeto Django)

---

A seguir, um roteiro de edições por arquivo. Não precisa decorar, basta seguir com calma.

### Passo 4: Instalar dependências

### A) Modelos (models.py)

No PowerShell (com ambiente ativado):

```powershellOnde: `catalog/models.py`

pip install -r requirements.txt- Criar o modelo `Category (name, description)`.

```- Adicionar à classe `Book` os campos opcionais: `category` (FK), `language`, `publisher`, `edition_year`, `series`, `subject`, `material`.

- Criar o modelo `SearchQuery` para registrar pesquisas (usuário/sessão, `q` e `params`, `created_at`).

**Aguarde 2-5 minutos.** Você verá mensagens de download.- Já existe o modelo `Loan` para empréstimos.



---Depois de salvar: rode `makemigrations` e `migrate` (item 4 acima).



## (continua na próxima parte)### B) Views (regras de tela) — `catalog/views.py`


- `book_list`: passou a aceitar filtros via GET
  - Termo livre `q` OU campos separados `title`, `author`, `isbn` (vêm da busca avançada).
  - Filtros: `disponivel`, `categoria`, `idioma`, `ano_min`, `ano_max`.
  - Ordenação: `ordenar` (title | author | disponibilidade).
  - Paginação: `mostrar` ("20" ou "todos").
  - Autocomplete: `?suggest=1&q=...` retorna JSON.
  - Exportação: `?export=csv` ou `?export=xlsx` (usa `openpyxl`).
  - Registro do histórico (cria `SearchQuery` com usuário ou sessão).

- `advanced_search`: renderiza uma página com formulário completo e envia via GET para `book_list`.
- `search_history`: lista as últimas buscas do usuário/sessão e permite exportar (CSV/Excel).
- `signup`: usa `UserCreationForm` para criar usuário.

### C) Rotas (URLs) — `catalog/urls.py` e `library/urls.py`

`catalog/urls.py` inclui:
- `""` → `book_list`
- `"advanced-search/"` → `advanced_search`
- `"me/searches/"` → `search_history`
- `"signup/"` → `signup`

`library/urls.py` inclui o fluxo de recuperação de senha (password reset) do Django:
- `password_reset/`, `password_reset/done/`, `reset/<uid>/<token>/`, `reset/done/`.

### D) Templates (HTML) — `templates/`

- `templates/catalog/book_list.html`:
  - Form com campo de busca, filtros, ordenação, paginação.
  - Botões de exportar CSV/Excel.
  - Script de destaque de termos e autocomplete.

- `templates/catalog/advanced_search.html`:
  - Formulário com `title`, `author`, `isbn`, `categoria`, `idioma`, anos e ordenação.

- `templates/catalog/search_history.html`:
  - Tabela com histórico + botões de exportar CSV/Excel.

- `templates/registration/login.html`:
  - Links para `Esqueci minha senha` e `Criar conta`.

- `templates/registration/password_reset_*.html`:
  - Páginas do fluxo de recuperação de senha (form, done, confirm, complete).

> Observação: Todos os templates estendem `base.html` já existente.

### E) Configurações — `library/settings.py`

Adicionar para desenvolvimento (e-mails vão para o console):
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### F) Admin — `catalog/admin.py`

- Registrar `Category` e `SearchQuery`.
- Em `BookAdmin`, exibir `category` e incluir filtros por `category`, `language`, `edition_year`.

### G) Dependências — `requirements.txt`

- Foi incluído `openpyxl==3.1.5` (gera Excel).
- Para atualizar seu ambiente após mudanças:
```powershell
pip install -r requirements.txt
```


## Como usar (depois que está tudo rodando)

- Busque por título/autor/ISBN na página principal. O termo pesquisado será destacado.
- Use filtros/ordenação e exporte os resultados.
- Para buscas mais precisas, vá em "Busca Avançada".
- Veja seu histórico em "Histórico" e baixe CSV/Excel.
- Crie conta em "Signup" e recupere senha por "Esqueci minha senha".


## Dúvidas comuns

- "O Excel não exporta": instale dependências (item 3). Verifique se `openpyxl` aparece em `pip list`.
- "Nada aparece na busca": confira se existe conteúdo cadastrado; use o `/admin/` para criar livros.
- "Histórico vazio": talvez você ainda não fez nenhuma busca com filtros/termos.


## Anexo: comandos úteis (PowerShell)

```powershell
# Ativar ambiente virtual
.\.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Gerar/aplicar migrações
python manage.py makemigrations
python manage.py migrate

# Criar usuário admin
python manage.py createsuperuser

# Rodar servidor
python manage.py runserver

# Atualizar requirements a partir do ambiente
pip freeze > requirements.txt
```

---

## PARTE 2: EDITAR OS MODELOS (models.py)

### Arquivo: `catalog/models.py`

**Localização:** `C:\Users\seu-usuário\local_onde_criou_o_projeto\Django\catalog\models.py`

---

#### 2.1) Adicionar imports no TOPO do arquivo

**ONDE:** Logo após a linha `from django.utils import timezone`

**ADICIONE estas linhas:**
```python
# Imports já existentes (NÃO APAGUE)
from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Cast
from django.utils import timezone
```

**Verifique se essas linhas já existem. Se sim, pule para próximo passo.**

---

#### 2.2) Criar modelo Category

**ONDE:** ANTES da classe `Book` (encontre onde está escrito `class Book(models.Model):`)

**ADICIONE este código COMPLETO:**
```python
class Category(models.Model):
    """Categoria/Gênero do livro.
    
    Mantemos simples com um nome único e uma descrição opcional. Esta
    classe permite filtrar o acervo por gênero (ex.: Romance, Didático,
    Tecnologia). Também é usada na busca avançada.
    """
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ["name"]
    
    def __str__(self):
        return self.name
```

---

#### 2.3) Adicionar campos extras na classe Book

**ONDE:** DENTRO da classe `Book`, DEPOIS do campo `image` e ANTES de `created_at`

**Localize esta linha:**
```python
image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
```

**Logo DEPOIS dela, ADICIONE:**
```python
    # Campos extras para filtros avançados (todos opcionais)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="books"
    )
    language = models.CharField("Idioma", max_length=50, blank=True)
    publisher = models.CharField("Editora", max_length=150, blank=True)
    edition_year = models.IntegerField("Ano de edição", null=True, blank=True)
    series = models.CharField("Série", max_length=150, blank=True)
    subject = models.CharField("Assunto", max_length=150, blank=True)
    material = models.CharField("Material", max_length=100, blank=True)
```

**IMPORTANTE:** Mantenha a indentação (4 espaços) igual aos outros campos.

---

#### 2.4) Criar modelo SearchQuery

**ONDE:** NO FINAL do arquivo `models.py`, DEPOIS da classe `Loan`

**ADICIONE:**
```python
class SearchQuery(models.Model):
    """Histórico de buscas realizadas.
    
    Armazenamos tanto buscas de usuários autenticados quanto de sessões
    (anônimos), permitindo mostrar pesquisas recentes por usuário e
    coletar métricas. O campo `params` guarda os filtros aplicados para
    reproduzir a consulta depois.
    """
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=40, blank=True, help_text="Chave da sessão quando usuário não está logado")
    q = models.CharField(max_length=255, blank=True)
    params = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self):
        usuario = self.user or self.session_key or "anon"
        return f"{usuario}: {self.q} ({self.created_at:%d/%m %H:%M})"
```

**Salve o arquivo** (Ctrl+S)

---

### Passo 5: Gerar e aplicar migrações

No PowerShell:
```powershell
python manage.py makemigrations
```

Você verá mensagens sobre criação de `Category`, `SearchQuery` e novos campos.

Agora aplique:
```powershell
python manage.py migrate
```

**Sucesso:** "Applying catalog.0004_... OK"

---

## (continua na próxima parte)

## PARTE 3: EDITAR AS VIEWS (views.py)

### Arquivo: `catalog/views.py`

**Localização:** `C:\Users\seu-usuário\local_onde_criou_o_projeto\Django\catalog\views.py`

---

#### 3.1) Adicionar imports NO TOPO

**ONDE:** Logo após `from django.shortcuts import ...`

**LOCALIZE estas linhas (já devem existir):**
```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
```

**ADICIONE logo ABAIXO:**
```python
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Count, Q, F
from django.db.models.functions import Lower
from django.contrib.auth.forms import UserCreationForm
from .models import Book, Loan, Category, SearchQuery
```

---

#### 3.2) Substituir a função book_list COMPLETA

**ONDE:** Encontre a função `def book_list(request):`

**SUBSTITUA TODA a função antiga por esta versão COMPLETA:**
```python
def book_list(request):
    # ...código de busca e filtragem...

    # Exportação para Excel
    if request.GET.get('export') == 'xlsx':
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Livros"
        # Cabeçalhos
        headers = ["Título", "Autor", "Categoria", "ISBN", "Disponível", "Ano", "Idioma", "Editora"]
        ws.append(headers)
        # Dados
        for book in books:  # 'books' é o queryset filtrado
            ws.append([
                book.title,
                book.author,
                book.category.name if book.category else "",
                book.isbn,
                "Sim" if book.available else "Não",
                book.edition_year or "",
                book.language or "",
                book.publisher or ""
            ])
        # Ajustar largura das colunas
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            ws.column_dimensions[column].width = max_length + 2
        # Resposta HTTP
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=livros.xlsx'
        wb.save(response)
        return response
    # ...continuação da função book_list...
```
(Use o código completo fornecido no guia anterior. Se precisar, peça o trecho completo.)

---

#### 3.3) Adicionar função search_history

**ONDE:** NO FINAL do arquivo `views.py`, DEPOIS da última função

**ADICIONE:**
```python
def search_history(request):
    # ...código completo conforme guia anterior...
```

---

#### 3.4) Adicionar função advanced_search

**ONDE:** Logo DEPOIS da função `search_history`

**ADICIONE:**
```python
def advanced_search(request):
    # ...código completo conforme guia anterior...
```

---

#### 3.5) Adicionar função signup

**ONDE:** Logo DEPOIS da função `advanced_search`

**ADICIONE:**
```python
def signup(request):
    # ...código completo conforme guia anterior...
```

**Salve o arquivo** (Ctrl+S)

---

## (continua na próxima parte)

##  PARTE 4: CONFIGURAR AS URLs (urls.py)

### 4.1) Editar o arquivo de URLs do app

**Arquivo:** `catalog/urls.py`
**Localização:** `C:\Users\seu-usuário\local_onde_criou_o_projeto\Django\catalog\urls.py`

---

#### 4.1.1) Adicionar imports NO TOPO

**ONDE:** Logo após `from django.urls import ...`

**LOCALIZE estas linhas (já devem existir):**
```python
from django.urls import path
```

**ADICIONE logo ABAIXO:**
```python
from . import views
```

---

#### 4.1.2) Substituir ou adicionar o array urlpatterns

**ONDE:** Encontre ou crie a variável `urlpatterns = [...]`

**SUBSTITUA ou ADICIONE o seguinte conteúdo:**
```python
urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('search_history/', views.search_history, name='search_history'),
    path('advanced_search/', views.advanced_search, name='advanced_search'),
    path('signup/', views.signup, name='signup'),
]
```

---

### 4.2) Incluir as URLs do app no projeto principal

**Arquivo:** `library/urls.py`
**Localização:** `C:\Users\seu-usuário\local_onde_criou_o_projeto\Django\library\urls.py`

---

#### 4.2.1) Adicionar import de include

**LOCALIZE estas linhas (no topo):**
```python
from django.contrib import admin
from django.urls import path
```

**MODIFIQUE para:**
```python
from django.contrib import admin
from django.urls import path, include
```

---

#### 4.2.2) Adicionar o path do app 'catalog' ao urlpatterns

**LOCALIZE a variável `urlpatterns = [...]`**

**ADICIONE (ou garanta que existe) esta linha dentro do array:**
```python
    path('', include('catalog.urls')),
```

**Exemplo final:**
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('catalog.urls')),
]
```

**Salve os arquivos** (Ctrl+S)

---

## (continua na próxima parte)

## PARTE 5: EDITAR OS TEMPLATES (HTML)

### 5.1) Localização dos arquivos de template

**Pasta principal de templates:**
`C:\Users\seu-usuário\local_onde_criou_o_projeto\Django\templates\`

**Subpastas importantes:**
- `templates/catalog/`
- `templates/registration/`

---

### 5.2) Editar/Adicionar templates do catálogo

#### 5.2.1) `book_list.html`
**Localização:** `templates/catalog/book_list.html`

- Certifique-se de que o arquivo existe. Se não existir, crie-o.
- Insira o código conforme o guia anterior (se precisar do código completo, peça!).
- Este template exibe a lista de livros, filtros, paginação e botões de busca avançada.

#### 5.2.2) `advanced_search.html`
**Localização:** `templates/catalog/advanced_search.html`

- Crie este arquivo se não existir.
- Insira o código conforme o guia anterior.
- Este template exibe o formulário de busca avançada.

#### 5.2.3) `search_history.html`
**Localização:** `templates/catalog/search_history.html`

- Crie este arquivo se não existir.
- Insira o código conforme o guia anterior.
- Este template exibe o histórico de buscas do usuário.

---

### 5.3) Editar/Adicionar templates de autenticação

#### 5.3.1) `signup.html`
**Localização:** `templates/catalog/signup.html`

- Crie este arquivo se não existir.
- Insira o código conforme o guia anterior.
- Este template exibe o formulário de cadastro de usuário.

#### 5.3.2) `login.html`
**Localização:** `templates/registration/login.html`

- Certifique-se de que o arquivo existe.
- Este template exibe o formulário de login.

#### 5.3.3) Templates de redefinição de senha
- `password_reset_form.html`
- `password_reset_done.html`
- `password_reset_confirm.html`
- `password_reset_complete.html`

**Localização:** `templates/registration/`

- Crie estes arquivos se não existirem.
- Insira o código conforme o guia anterior.
- Estes templates permitem ao usuário redefinir a senha.

---

### 5.4) Editar o template base

#### 5.4.1) `base.html`
**Localização:** `templates/base.html`

- Certifique-se de que o arquivo existe.
- Este template serve como base para todos os outros, com cabeçalho, rodapé e blocos de conteúdo.

**Salve todos os arquivos editados**

---

## (continua na próxima parte)

## PARTE 6: CONFIGURAR O ADMIN, EXPORTAÇÃO E TESTES

### 6.1) Configurar o Django Admin

#### 6.1.1) Editar `catalog/admin.py`
**Localização:** `C:\Users\seu-usuário\local_onde_criou_o_projeto\Django\catalog\admin.py`

- Certifique-se de que os modelos `Book`, `Category`, `Loan` e `SearchQuery` estão registrados.
- Para personalizar a visualização dos livros, utilize o `BookAdmin`.

**Exemplo:**
```python
from django.contrib import admin
from .models import Book, Category, Loan, SearchQuery

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'isbn', 'available')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('category', 'available')

admin.site.register(Book, BookAdmin)
admin.site.register(Category)
admin.site.register(Loan)
admin.site.register(SearchQuery)
```

---

### 6.2) Exportação de dados para Excel

#### 6.2.1) Instalar o pacote openpyxl

**No terminal do VS Code, execute:**
```powershell
pip install openpyxl
```

#### 6.2.2) Adicionar função de exportação

**Como implementar a exportação de dados para Excel:**

1. **Abra o arquivo:** `catalog/views.py`
2. **Localize a função que lista os livros** (geralmente chamada `book_list`).
3. **Adicione o seguinte código dentro da função `book_list`:**

```python
import openpyxl
from openpyxl.utils import get_column_letter
from django.http import HttpResponse

# ...existing code...

def book_list(request):
    # ...código de busca e filtragem...

    # Exportação para Excel
    if request.GET.get('export') == 'xlsx':
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Livros"
        # Cabeçalhos
        headers = ["Título", "Autor", "Categoria", "ISBN", "Disponível", "Ano", "Idioma", "Editora"]
        ws.append(headers)
        # Dados
        for book in books:  # 'books' é o queryset filtrado
            ws.append([
                book.title,
                book.author,
                book.category.name if book.category else "",
                book.isbn,
                "Sim" if book.available else "Não",
                book.edition_year or "",
                book.language or "",
                book.publisher or ""
            ])
        # Ajustar largura das colunas
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            ws.column_dimensions[column].width = max_length + 2
        # Resposta HTTP
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=livros.xlsx'
        wb.save(response)
        return response
    # ...continuação da função book_list...
```
(Use o código completo fornecido no guia anterior. Se precisar, peça o trecho completo.)

---

### 6.3) Testar o sistema

#### 6.3.1) Executar o servidor

**No terminal do VS Code, execute:**
```powershell
python manage.py runserver
```

#### 6.3.2) Testar funcionalidades
- Acesse o sistema pelo navegador: http://127.0.0.1:8000/
- Teste cadastro, login, busca, histórico, exportação, etc.

#### 6.3.3) Executar testes automatizados (se existirem)

**Como executar e interpretar testes automatizados:**

1. **Abra o terminal do VS Code na pasta do projeto.**
2. **Ative o ambiente virtual, se necessário:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
3. **Execute os testes com o comando:**
   ```powershell
   python manage.py test
   ```
4. **O que acontece:**
   - O Django procura por arquivos chamados `tests.py` nos apps (exemplo: `catalog/tests.py`).
   - Os testes são executados e o terminal mostra o resultado de cada teste:
     - `OK` para testes que passaram
     - `FAIL` ou `ERROR` para testes que falharam
   - Exemplo de saída:
     ```
     ...
     Ran 4 tests in 0.123s
     OK
     ```

5. **Exemplo de teste existente no seu projeto:**
   - O arquivo `catalog/tests.py` já possui testes para empréstimos e autenticação.
   - Exemplo de teste:
     ```python
     from django.test import TestCase
     from .models import Book, Category

     class BookModelTest(TestCase):
         def test_create_book(self):
             category = Category.objects.create(name="Romance")
             book = Book.objects.create(
                 title="Dom Casmurro",
                 author="Machado de Assis",
                 category=category,
                 isbn="1234567890"
             )
             self.assertEqual(book.title, "Dom Casmurro")
             self.assertEqual(book.category.name, "Romance")
     ```

6. **Como criar novos testes:**
   - Edite o arquivo `catalog/tests.py` e adicione funções que começam com `test_`.
   - Use `self.assertEqual`, `self.assertTrue`, etc., para verificar resultados.

7. **Se não houver testes:**
   - O comando irá informar que nenhum teste foi encontrado.
   - Recomenda-se criar testes para as principais funcionalidades do sistema.

**Pronto! Assim você garante que as principais partes do sistema estão funcionando corretamente.**

---

### 6.4) Dicas de resolução de problemas
- Se aparecer erro de importação, confira se o nome do arquivo e do modelo estão corretos.
- Se o template não carregar, verifique o caminho e o nome do arquivo.
- Se o servidor não iniciar, confira se está na pasta correta e se o ambiente está ativado.

---

# Padronização de Localização e Orientação de Código

> **Observação:** Todos os passos abaixo indicam claramente:
> - **Localização do arquivo** (caminho completo)
> - **Parte do arquivo** onde inserir/alterar
> - **Quando criar um novo arquivo**

## Exemplos de padronização (aplicados em todo o guia):

### Modelos (models.py)
- **Arquivo:** `C:\Users\...\catalog\models.py`
- **Onde adicionar:** Logo após a linha `from django.utils import timezone` (imports)
- **Onde criar:** Antes da classe `Book` (criação da classe `Category`)
- **Onde adicionar campos:** Dentro da classe `Book`, após o campo `image`
- **Onde criar:** No final do arquivo, após a última classe (criação da classe `SearchQuery`)

### Views (views.py)
- **Arquivo:** `C:\Users\...\catalog\views.py`
- **Onde adicionar imports:** Logo após os imports existentes
- **Onde substituir:** Encontre a função `def book_list(request):` e substitua toda a função
- **Onde criar:** No final do arquivo, após a última função (criação de novas views)

### URLs (urls.py)
- **Arquivo:** `C:\Users\...\catalog\urls.py` e `C:\Users\...\library\urls.py`
- **Onde adicionar imports:** No topo do arquivo
- **Onde modificar:** Substitua ou adicione o array `urlpatterns = [...]`
- **Onde criar:** Se o arquivo não existir, crie-o na pasta indicada

### Templates (HTML)
- **Pasta:** `C:\Users\...\templates\catalog\` ou `C:\Users\...\templates\registration\`
- **Onde criar:** Crie o arquivo se não existir (exemplo: `book_list.html`, `advanced_search.html`, etc.)
- **Onde editar:** Abra o arquivo e insira o código conforme indicado

### Admin
- **Arquivo:** `C:\Users\...\catalog\admin.py`
- **Onde adicionar:** No topo (imports), depois registre os modelos após as classes

### Exportação
- **Arquivo:** `C:\Users\...\catalog\views.py`
- **Onde adicionar:** Dentro da função `book_list`, após o código de busca e filtragem

### Testes
- **Arquivo:** `C:\Users\...\catalog\tests.py`
- **Onde criar:** Crie o arquivo se não existir
- **Onde adicionar:** Adicione funções que começam com `test_` dentro da classe de teste

---

> **Dica:** Sempre confira se o arquivo existe na pasta indicada. Se não existir, crie-o antes de inserir o código.
> **Dica:** Mantenha a indentação igual ao restante do arquivo.

---

## Fim do guia

Parabéns! Você implementou todas as melhorias no sistema de biblioteca Django.


**Desenvolvido em:** Novembro de 2025  
**Sistema de Biblioteca:** Django 5.2.7 + Python 3.13  
**Autor:** Wellyelton Gulberto  