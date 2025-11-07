# Melhorias implementadas — Aula 07/11

Este documento descreve o que foi implementado no sistema de biblioteca e traz um passo a passo para que qualquer pessoa (mesmo sem conhecimento prévio em Python/Django) consiga reproduzir as melhorias.


## Visão geral do que foi entregue

- Busca básica com destaques e autocomplete
- Busca avançada (campos separados + filtros)
- Filtros por disponibilidade, categoria, idioma e faixa de ano
- Ordenação por título, autor ou disponibilidade
- Paginação (20 itens) ou exibição de todos
- Exportação dos resultados e do histórico (CSV e Excel)
- Histórico de buscas por usuário/sessão
- Cadastro de usuário (signup)
- Recuperação de senha (password reset)
- Ajustes no Admin (categorias e histórico cadastrados, filtros extras)


## O que você precisa antes de começar

- Windows 10/11
- Python instalado (https://www.python.org/downloads/)
- VS Code (opcional, recomendado)
- Internet para baixar dependências


## Passo a passo (reprodução simplificada)

Siga na ordem. Os comandos abaixo são para o PowerShell do Windows.

### 1) Abrir a pasta do projeto

```powershell
cd C:\Users\03615153162\Desktop\Django
```

### 2) Criar e ativar o ambiente virtual (uma vez)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se já existir, basta ativar:
```powershell
.\.venv\Scripts\Activate.ps1
```

### 3) Instalar dependências

O arquivo `requirements.txt` já inclui tudo (Django, Pillow, tzdata, openpyxl):
```powershell
pip install -r requirements.txt
```

### 4) Aplicar migrações do banco de dados

```powershell
python manage.py migrate
```

Se você alterou os modelos (models.py) e ainda não gerou migrações:
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5) Rodar o servidor

```powershell
python manage.py runserver
```

Acesse no navegador:
- Lista de livros (busca básica): http://127.0.0.1:8000/
- Busca avançada: http://127.0.0.1:8000/advanced-search/
- Histórico de buscas: http://127.0.0.1:8000/me/searches/
- Cadastro (signup): http://127.0.0.1:8000/signup/
- Esqueci a senha: http://127.0.0.1:8000/password_reset/
- Admin (se tiver superusuário): http://127.0.0.1:8000/admin/

> Dica: crie um usuário admin com `python manage.py createsuperuser`.


## Como essas melhorias foram feitas (guia para replicar em outro projeto Django)

A seguir, um roteiro de edições por arquivo. Não precisa decorar, basta seguir com calma.

### A) Modelos (models.py)

Onde: `catalog/models.py`
- Criar o modelo `Category (name, description)`.
- Adicionar à classe `Book` os campos opcionais: `category` (FK), `language`, `publisher`, `edition_year`, `series`, `subject`, `material`.
- Criar o modelo `SearchQuery` para registrar pesquisas (usuário/sessão, `q` e `params`, `created_at`).
- Já existe o modelo `Loan` para empréstimos.

Depois de salvar: rode `makemigrations` e `migrate` (item 4 acima).

### B) Views (regras de tela) — `catalog/views.py`

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
Documento preparado em 07/11.
