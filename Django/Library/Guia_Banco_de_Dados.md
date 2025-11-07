# Instruções de Banco de Dados (Django + SQLite)

Guia para entender, visualizar e administrar o banco de dados deste projeto, além de opções para gerar diagramas de relacionamento.

---

## 1) Como funciona o banco de dados neste sistema?

### 1.1 SQLite – banco embutido

Você não precisou criar um banco manualmente porque o Django usa o **SQLite por padrão** em ambientes de desenvolvimento.

- Não precisa instalar servidor de banco de dados
- Armazena os dados em um único arquivo local
- Zero configuração adicional para começar
- Ideal para estudo e prototipagem

### 1.2 Onde está o banco?

Estrutura típica do projeto:

```
Django/
├── db.sqlite3    ← ESTE É O SEU BANCO DE DADOS
├── manage.py
├── catalog/
└── library/
```

O arquivo `db.sqlite3` contém todas as tabelas (livros, empréstimos, usuários etc.).

### 1.3 Como o arquivo foi criado?

Ao executar as migrações:

```powershell
python manage.py migrate
```

O Django:
1. Lê os modelos em `catalog/models.py` (Book, Loan)
2. Cria o arquivo `db.sqlite3` (se não existir)
3. Executa o SQL necessário para criar/atualizar as tabelas

Tabelas principais criadas por este projeto:
- `catalog_book` (id, title, author, isbn, copies_total, image, created_at)
- `catalog_loan` (id, book_id, user_id, borrowed_at, due_date, returned_at)
- `auth_user` (usuários do Django) e outras tabelas internas

### 1.4 Onde está a configuração do banco?

Arquivo: `library/settings.py`:

```python
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',  # Usa SQLite
		'NAME': BASE_DIR / 'db.sqlite3',          # Caminho do arquivo
	}
}
```

Essa é a “conexão” com o banco. O Django cuida do restante automaticamente.

### 1.5 Como o Django gerencia as tabelas? (modelo → migração → SQL)

Passos típicos:

1) Defina os modelos (`catalog/models.py`)

```python
class Book(models.Model):
	title = models.CharField(max_length=255)
	author = models.CharField(max_length=255)
	isbn = models.CharField(max_length=13, unique=True)
	copies_total = models.PositiveIntegerField(default=1)
	image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
```

2) Gere a migração:

```powershell
python manage.py makemigrations
```

3) Aplique a migração (gera/atualiza tabelas no SQLite):

```powershell
python manage.py migrate
```

4) O SQL equivalente (exemplo simplificado):

```sql
CREATE TABLE catalog_book (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	title VARCHAR(255) NOT NULL,
	author VARCHAR(255) NOT NULL,
	isbn VARCHAR(13) UNIQUE NOT NULL,
	copies_total INTEGER NOT NULL,
	image VARCHAR(100),
	created_at DATETIME NOT NULL
);
```

### 1.6 Ver dados do banco

Opção A) Django Shell (ORM):

```powershell
python manage.py shell
```

```python
from catalog.models import Book, Loan

# Todos os livros
Book.objects.all()

# Empréstimos ativos
Loan.objects.filter(returned_at__isnull=True)

# Busca por título
Book.objects.filter(title__icontains="1984")

exit()
```

Opção B) SQL direto (dbshell):

```powershell
python manage.py dbshell
```

```sql
-- Listar livros
SELECT * FROM catalog_book;

-- Empréstimos ativos
SELECT * FROM catalog_loan WHERE returned_at IS NULL;

.exit
```

Opção C) Ferramenta gráfica: [DB Browser for SQLite](https://sqlitebrowser.org/)

1. Abra o programa e carregue o arquivo `db.sqlite3`
2. Use as abas “Database Structure”, “Browse Data” e “Execute SQL”

### 1.7 Fluxo completo (resumo)

```
┌─────────────────────────────────────────────┐
│ 1. Edita models.py                          │
├─────────────────────────────────────────────┤
│ 2. Gera migração (makemigrations)           │
├─────────────────────────────────────────────┤
│ 3. Aplica migração (migrate)                │
├─────────────────────────────────────────────┤
│ 4. Banco atualizado (SQLite)                │
└─────────────────────────────────────────────┘
```


### 1.10 Trocar para PostgreSQL (opcional)

Criar DB/usuário:

```sql
CREATE DATABASE biblioteca;
CREATE USER bibliotecauser WITH PASSWORD 'senha123';
GRANT ALL PRIVILEGES ON DATABASE biblioteca TO bibliotecauser;
```

Configurar `settings.py`:

```python
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': 'biblioteca',
		'USER': 'bibliotecauser',
		'PASSWORD': 'senha123',
		'HOST': 'localhost',
		'PORT': '5432',
	}
}
```

Driver:

```powershell
pip install psycopg2-binary
```

Migrar:

```powershell
python manage.py migrate
```

### 1.11 Comandos úteis do Django

```powershell
# SQL que seria executado para uma migração
python manage.py sqlmigrate catalog 0001

# Status das migrações
python manage.py showmigrations

# Resetar banco (CUIDADO: apaga tudo!)
del db.sqlite3
python manage.py migrate

# Criar dado de teste rápido (ORM)
python manage.py shell
>>> from catalog.models import Book
>>> Book.objects.create(title="Teste", author="Autor", isbn="1234567890123")

# Backup do SQLite (Windows)
copy db.sqlite3 db_backup_31-10-2025.sqlite3
```

### 1.12 O que é o ORM?

O ORM (Object-Relational Mapping) converte código Python em SQL automaticamente.

Exemplo (Python → SQL):

```python
book = Book.objects.get(id=1)
book.title = "Novo Título"
book.save()
```

```sql
SELECT * FROM catalog_book WHERE id = 1;
UPDATE catalog_book SET title = 'Novo Título' WHERE id = 1;
```

Vantagens: portabilidade entre bancos, menos SQL manual, proteção contra SQL injection, sintaxe Python.

---

## 2) Como visualizar diagramas (ER) usando SQLite

### Opção 1: DB Browser for SQLite (recomendado, visual e simples)

1. Baixe e instale: https://sqlitebrowser.org/
2. Abra `db.sqlite3`
3. Aba “Database Structure” → clique em uma tabela (ex.: `catalog_loan`)
4. Veja “Foreign Keys” no painel direito, por exemplo:
   - `book_id` → `catalog_book(id)`
   - `user_id` → `auth_user(id)`

### Opção 2: Django Extensions + Graphviz (gera imagem automática)

Instalar dependências:

```powershell
pip install django-extensions pydotplus
```

Instalar Graphviz (Windows): https://graphviz.org/download/ (adicione ao PATH)

Ativar app em `library/settings.py`:

```python
INSTALLED_APPS = [
	# ...
	'django_extensions',
]
```

Gerar diagrama:

```powershell
python manage.py graph_models catalog -o diagrama.png
# Alternativas:
python manage.py graph_models -a -o diagrama_completo.png   # todos os apps
python manage.py graph_models catalog -o diagrama.svg       # formato SVG
python manage.py graph_models catalog -g -o diagrama_g.png  # agrupado
```

### Opção 3: VS Code – extensões SQLite

- Extensão “SQLite” (alexcvzz)
- Abra `db.sqlite3` → “Open Database” → explore estrutura e dados

### Opção 4: DBeaver (IDE de banco)

1. Baixe: https://dbeaver.io/download/
2. New → Database Connection → SQLite → selecione `db.sqlite3`
3. Clique com botão direito → “View Diagram” / “ER Diagram”

### Opção 5: Ver relacionamentos via SQL (PRAGMA)

```powershell
python manage.py dbshell
```

```sql
-- Chaves estrangeiras da tabela de empréstimos
PRAGMA foreign_key_list(catalog_loan);

-- Estrutura da tabela
.schema catalog_loan
.exit
```

### Diagrama textual simplificado

```
auth_user (Django)
  id (PK)
  username
  ...
	   ▲ 1
	   │
	   │ N                   
catalog_loan
  id (PK)
  book_id (FK) ───────┐
  user_id (FK) ───────┤
  borrowed_at          │
  due_date             │
  returned_at          │
					   │
					   ▼
catalog_book
  id (PK)
  title
  author
  isbn (UNIQUE)
  copies_total
  image
  created_at
```

---

## 3) Quando trocar de SQLite para outro banco?

- Produção em larga escala (muitos usuários simultâneos)
- Necessidade de recursos avançados (replicação, tuning, extensões)
- Políticas de backup/alta disponibilidade

Enquanto aprende e desenvolve localmente, o SQLite é a opção mais prática.

---

## 4) Resumo prático

- O Django cria e gerencia o `db.sqlite3` via migrações
- Configuração mínima em `settings.py`
- Use o ORM para consultas, ou `dbshell` para SQL
- Para diagramas: DB Browser (simples) ou Django Extensions + Graphviz (automático)