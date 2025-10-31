# Sistema de Gerenciamento de Biblioteca

> Sistema web  para gestão de acervo e empréstimos de biblioteca, desenvolvido em Django 5.2.7

## Índice

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Uso](#uso)
- [Arquitetura](#arquitetura)
- [Modelos de Dados](#modelos-de-dados)
- [API de Rotas](#api-de-rotas)
- [Testes](#testes)
- [Configuração](#configuração)
- [Segurança](#segurança)
- [FAQ](#faq)

---

## Visão Geral

Sistema web desenvolvido em Django que permite o gerenciamento completo de uma biblioteca, incluindo:
- Cadastro e consulta de livros **com capas ilustradas**
- Sistema de empréstimos com controle de prazos
- Gestão de disponibilidade (múltiplas cópias por título)
- Identificação automática de atrasos
- Painel administrativo completo
- Interface responsiva com tema claro/escuro

**Stack Tecnológica:**
- Backend: Django 5.2.7 + Python 3.10+
- Banco de dados: SQLite (desenvolvimento)
- Frontend: Templates Django + CSS puro + JavaScript vanilla
- Autenticação: Sistema de autenticação nativo do Django
- Processamento de imagens: Pillow

---

## Funcionalidades

### Para Usuários Autenticados

**Catálogo de Livros**
- Visualizar todos os livros cadastrados **com capas ilustrativas**
- Ver disponibilidade em tempo real (cópias disponíveis/total)
- Pesquisar por título, autor ou ISBN
- Miniaturas das capas em todas as listagens

**Empréstimos**
- Emprestar livros disponíveis (prazo padrão: 14 dias)
- Devolver livros emprestados
- Visualizar histórico completo de empréstimos **com capas**

**Minha Conta**
- Ver empréstimos ativos e devolvidos
- Identificação visual de empréstimos atrasados
- Status em tempo real (Ativo, Atrasado, Devolvido)
- Capas dos livros emprestados exibidas no histórico

### Para Administradores (Staff)

**Gestão de Acervo**
- Adicionar/editar/remover livros via Django Admin
- **Upload de capas de livros** (JPEG, PNG, GIF, WebP)
- Gerenciar número de cópias por título
- Consultar ISBN único para evitar duplicatas

**Controle de Empréstimos**
- Ver quem está com cada livro (empréstimos ativos) **com capa em destaque**
- Listar todos os empréstimos atrasados
- Marcar empréstimos como devolvidos manualmente
- Ação em massa no Django Admin para devoluções

**Relatórios**
- Visualizar histórico completo de empréstimos
- Filtrar por usuário, livro, status ou data
- Exportar dados via Django Admin

### Interface

**Tema Claro/Escuro**
- Alternância via botão no menu superior
- Preferência salva localmente (localStorage)
- Respeita configuração do sistema operacional

---

## Requisitos

### Ambiente
- **Python:** 3.10 ou superior
- **Sistema Operacional:** Windows, Linux ou macOS
- **Shell (Windows):** PowerShell 5.1+ ou PowerShell Core

### Dependências Python
- Django >= 4.2, < 6.0
- Pillow >= 10.0 (processamento de imagens)
- Pacotes nativos: `asgiref`, `sqlparse`, `tzdata`

---

## Instalação

### 1. Clonar/Baixar o Projeto

```powershell
cd C:\Users\SeuUsuario\Desktop
# (ou extraia o zip aqui)
cd Django
```

### 2. Criar Ambiente Virtual

```powershell
python -m venv .venv
```

### 3. Ativar Ambiente Virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

> **Nota:** Se houver erro de política de execução, execute como Administrador:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 4. Instalar Dependências

```powershell
python -m pip install --upgrade pip
pip install "django>=4.2,<6.0" Pillow
```

> **Pillow** é necessário para o campo de imagem (ImageField) do Django. Permite upload e processamento de capas de livros.

### 5. Aplicar Migrações

```powershell
python manage.py migrate
```

### 6. (Opcional) Criar Superusuário

O sistema já vem com um usuário admin pré-criado (`admin`/`admin123`), mas você pode criar o seu próprio:

```powershell
python manage.py createsuperuser
```

### 7. (Opcional) Carregar Dados de Exemplo

O sistema já possui 3 livros de exemplo. Para adicionar mais:

```powershell
python manage.py shell
```

Dentro do shell Python:
```python
from catalog.models import Book
Book.objects.create(title="Seu Livro", author="Autor", isbn="1234567890123", copies_total=2)
exit()
```

---

## Uso

### Iniciar o Servidor

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

Acesse: **http://127.0.0.1:8000/**

### Credenciais Padrão

**Administrador:**
- Usuário: `admin`
- Senha: `admin123`

### Navegação

| Página | URL | Descrição |
|--------|-----|-----------|
| Página Inicial | `/` | Lista de livros disponíveis |
| Meus Empréstimos | `/me/loans/` | Histórico pessoal |
| Login | `/login/` | Autenticação |
| Django Admin | `/admin/` | Painel administrativo |
| Empréstimos Atrasados | `/staff/overdue/` | Apenas staff |
| Quem Emprestou | `/staff/book/<id>/borrowers/` | Apenas staff |

### Fluxo de Empréstimo

1. Usuário faz login
2. Navega até a página inicial (Livros)
3. Clica em "Emprestar" no livro desejado
4. Sistema cria empréstimo com prazo de 14 dias
5. Usuário recebe confirmação com data de devolução
6. Para devolver: acessa "Meus empréstimos" → "Devolver"

### Fluxo Administrativo

1. Admin acessa `/admin/`
2. Gerencia livros em "Books"
   - **Adicionar capa:** Clique em "Add Book" ou edite existente → campo "Image" → escolha arquivo → salve
3. Consulta empréstimos em "Loans"
4. Para marcar devolvido: seleciona empréstimos → "Marcar como devolvido"
5. Ou acessa `/staff/overdue/` para ver atrasados

### Gerenciamento de Capas

**Adicionar/Atualizar Capa:**
1. Acesse `/admin/catalog/book/`
2. Selecione o livro (ou crie novo)
3. Role até o campo **"Image"**
4. Clique em **"Choose File"** e selecione a imagem (JPEG, PNG, GIF, WebP)
5. Salve

**Remover Capa:**
1. Edite o livro no admin
2. Marque a caixa **"Clear"** ao lado do campo Image
3. Salve

> Imagens são salvas automaticamente em `media/book_covers/`

---

## Arquitetura

### Estrutura de Diretórios

```
Django/
├── .venv/                    # Ambiente virtual Python
├── catalog/                  # App principal
│   ├── migrations/          # Migrações do banco
│   │   ├── 0001_initial.py
│   │   ├── 0002_remove_loan_loan_due_after_borrowed_and_more.py
│   │   └── 0003_book_image.py  # Migração que adiciona campo de imagem
│   ├── __pycache__/
│   ├── admin.py             # Configuração Django Admin
│   ├── apps.py
│   ├── models.py            # Modelos Book e Loan
│   ├── tests.py             # Testes unitários
│   ├── urls.py              # Rotas do app
│   └── views.py             # Views (controladores)
├── library/                  # Projeto Django
│   ├── __pycache__/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py          # Configurações globais (inclui MEDIA_ROOT)
│   ├── urls.py              # Rotas principais (serve media files)
│   └── wsgi.py
├── media/                    # Uploads de usuários
│   └── book_covers/         # Imagens das capas dos livros
│       ├── exemplo1.jpg
│       ├── exemplo2.png
│       └── ...
├── templates/                # Templates HTML
│   ├── base.html            # Template base (herança)
│   ├── catalog/
│   │   ├── admin_book_borrowers.html
│   │   ├── admin_overdue.html
│   │   ├── book_list.html
│   │   └── my_loans.html
│   └── registration/
│       └── login.html
├── db.sqlite3               # Banco de dados SQLite
├── manage.py                # CLI do Django
└── README.md                # Esta documentação
```

### Camadas da Aplicação

```
┌─────────────────────────────────┐
│      Templates (HTML/CSS/JS)    │  ← Apresentação
├─────────────────────────────────┤
│      Views (views.py)           │  ← Lógica de negócio
├─────────────────────────────────┤
│      Models (models.py)         │  ← Camada de dados
├─────────────────────────────────┤
│      Database (SQLite)          │  ← Persistência
└─────────────────────────────────┘
```

---

## Modelos de Dados

### Book (Livro)

Representa um título do acervo.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer (PK) | Identificador único |
| `title` | CharField(255) | Título do livro |
| `author` | CharField(255) | Nome do autor |
| `isbn` | CharField(13, unique) | ISBN (único) |
| `copies_total` | PositiveInteger | Total de cópias |
| `image` | ImageField (null, blank) | Capa do livro (opcional) |
| `created_at` | DateTime | Data de cadastro |

**Propriedade Calculada:**
- `copies_available`: Número de cópias disponíveis (total - empréstimos ativos)

**Detalhes do Campo Image:**
- Salvo em: `media/book_covers/`
- Formatos aceitos: JPEG, PNG, GIF, WebP, BMP
- Opcional (blank=True, null=True)
- Acesso no template: `{{ book.image.url }}`

### Loan (Empréstimo)

Representa um empréstimo de livro para um usuário.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer (PK) | Identificador único |
| `book` | ForeignKey(Book) | Livro emprestado |
| `user` | ForeignKey(User) | Usuário que pegou |
| `borrowed_at` | DateTime | Data/hora do empréstimo |
| `due_date` | Date | Data limite de devolução |
| `returned_at` | DateTime (null) | Data/hora da devolução |

**Propriedades Calculadas:**
- `is_active`: `True` se ainda não foi devolvido
- `is_overdue`: `True` se passou da data e ainda está ativo

**Constraints:**
- `due_date >= date(borrowed_at)`: garante data de devolução válida

### Relacionamentos

```
User (Django Auth)
  ↓ (1:N)
Loan ← (N:1) → Book
```

- Um usuário pode ter vários empréstimos
- Um livro pode ter vários empréstimos (histórico)
- Cada empréstimo pertence a um usuário e um livro

---

## API de Rotas

### Rotas Públicas

| Método | URL | Nome | Descrição |
|--------|-----|------|-----------|
| GET/POST | `/login/` | `login` | Página de autenticação |
| POST | `/logout/` | `logout` | Deslogar (requer POST) |

### Rotas de Usuário (requer login)

| Método | URL | Nome | Descrição |
|--------|-----|------|-----------|
| GET | `/` | `catalog:book_list` | Lista livros disponíveis |
| POST | `/borrow/<id>/` | `catalog:borrow_book` | Emprestar livro |
| POST | `/return/<id>/` | `catalog:return_book` | Devolver livro |
| GET | `/me/loans/` | `catalog:my_loans` | Meus empréstimos |

### Rotas Staff (requer is_staff)

| Método | URL | Nome | Descrição |
|--------|-----|------|-----------|
| GET | `/staff/overdue/` | `catalog:admin_overdue_loans` | Empréstimos atrasados |
| GET | `/staff/book/<id>/borrowers/` | `catalog:admin_book_borrowers` | Quem pegou o livro |
| POST | `/staff/loan/<id>/return/` | `catalog:admin_mark_returned` | Marcar devolvido |

### Django Admin

| URL | Descrição |
|-----|-----------|
| `/admin/` | Painel administrativo completo |
| `/admin/catalog/book/` | Gerenciar livros **(incluindo upload de capas)** |
| `/admin/catalog/loan/` | Gerenciar empréstimos |

### Arquivos de Media (uploads)

| URL | Descrição |
|-----|-----------|
| `/media/book_covers/<arquivo>` | Acesso direto às capas dos livros |

> Em produção, configure o servidor web (Nginx/Apache) para servir `/media/` diretamente, sem passar pelo Django.

---

## Testes

### Executar Suite de Testes

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py test
```

Com verbosidade:
```powershell
python manage.py test -v 2
```

### Cobertura de Testes

**Testes Implementados:**

1. **`test_overdue_logic`**: Valida cálculo de atraso
2. **`test_mark_returned_sets_timestamp`**: Valida devolução
3. **`test_copies_available_counts_active_loans`**: Valida disponibilidade
4. **`test_logout_requires_post_and_redirects`**: Valida segurança logout

**Comando de Teste com Cobertura (opcional):**
```powershell
pip install coverage
coverage run --source='catalog' manage.py test
coverage report
```

---

## Configuração

### settings.py - Principais Configurações

```python
# Idioma e Timezone
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'

# Apps instalados
INSTALLED_APPS = [
    # ... apps padrão do Django
    'catalog',  # nosso app
]

# Templates
TEMPLATES = [{
    'DIRS': [BASE_DIR / 'templates'],  # templates globais
    'APP_DIRS': True,
}]

# Arquivos estáticos e media
STATIC_URL = 'static/'
MEDIA_URL = 'media/'              # Prefixo URL para uploads
MEDIA_ROOT = BASE_DIR / 'media'  # Pasta física dos uploads

# Redirecionamentos de autenticação
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'catalog:book_list'
LOGOUT_REDIRECT_URL = 'login'
```

### Variáveis de Ambiente (Produção)

Para deploy, configure:

```bash
# .env (não incluído no repositório)
SECRET_KEY=sua-chave-secreta-longa-e-aleatoria
DEBUG=False
ALLOWED_HOSTS=seudominio.com,www.seudominio.com
DATABASE_URL=postgres://...
```

---

## Segurança

### Medidas Implementadas

**Autenticação Obrigatória**
- Todas as views principais requerem login (`@login_required`)
- Views administrativas requerem `is_staff`

**Proteção CSRF**
- Todos os formulários usam `{% csrf_token %}`
- Ações de estado (borrow, return) só aceitam POST

**Logout Seguro**
- Django 5.x: logout via POST (não GET)
- Previne logout acidental via link malicioso

**Constraints de Banco**
- ISBN único (não permite livros duplicados)
- Data de devolução válida (constraint CHECK)

**Validações**
- Verifica disponibilidade antes de emprestar
- Apenas dono do empréstimo pode devolver
- Staff não pode modificar empréstimos de outros sem permissão

### Recomendações para Produção

**Antes de fazer deploy:**

1. Altere `SECRET_KEY` em `settings.py`
2. Configure `DEBUG = False`
3. Defina `ALLOWED_HOSTS`
4. Use PostgreSQL/MySQL em vez de SQLite
5. **Configure servidor web para servir `/media/`:**
   ```nginx
   # Nginx
   location /media/ {
       alias /caminho/absoluto/para/media/;
   }
   ```
6. Configure HTTPS e cookies seguros:
   ```python
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```
7. **Considere CDN ou S3 para imagens** (opcional, para alta escalabilidade)

---

## FAQ

### Como adicionar um novo livro?

1. Acesse `/admin/` como administrador
2. Clique em "Books" → "Add Book"
3. Preencha título, autor, ISBN (13 dígitos) e número de cópias
4. **(Opcional)** Faça upload da capa no campo "Image"
5. Salve

### Como adicionar/alterar a capa de um livro?

1. Acesse `/admin/catalog/book/`
2. Clique no livro desejado
3. Role até o campo **"Image"**
4. Clique em **"Choose File"** e selecione a imagem
5. Salve

**Formatos aceitos:** JPEG (.jpg), PNG (.png), GIF (.gif), WebP (.webp), BMP (.bmp)

**Dica:** Use imagens com proporção 2:3 (ex: 400x600px) para melhor visualização.

### O que acontece se eu não adicionar capa?

O sistema exibe um placeholder visual com a mensagem "Sem capa". O livro funciona normalmente.

### Como funciona o cálculo de disponibilidade?

```python
copies_available = copies_total - empréstimos_ativos
```

Exemplo:
- Livro tem 3 cópias totais
- 2 empréstimos ativos (não devolvidos)
- Disponibilidade = 3 - 2 = 1 cópia disponível

### Um livro pode ter ISBN duplicado?

Não. O campo `isbn` é único. Se tentar cadastrar um ISBN existente, o Django retornará erro.

### Qual o prazo padrão de empréstimo?

14 dias a partir da data do empréstimo. Configurável em `views.py`:
```python
due_date = timezone.localdate() + timedelta(days=14)
```

### Como alterar o prazo padrão?

Edite `catalog/views.py`, função `borrow_book`:
```python
# Linha ~43
due_date = timezone.localdate() + timedelta(days=30)  # 30 dias
```

### Posso ter empréstimos sem data de devolução?

Tecnicamente sim (campo `returned_at` pode ser nulo), mas não é recomendado. O sistema identifica automaticamente como "ativo".

### Como um usuário comum vira administrador?

1. Acesse `/admin/` como superuser
2. Vá em "Users"
3. Edite o usuário desejado
4. Marque "Staff status" e "Superuser status" (se necessário)
5. Salve

### O que acontece se devolver um livro atrasado?

O sistema registra a devolução normalmente. Não há multa automática, mas o histórico fica registrado com a data real de devolução.

### Posso mudar o tema padrão (claro/escuro)?

Sim. O sistema detecta a preferência do navegador/sistema operacional. Para forçar um tema:

Edite `templates/base.html`, linha do script:
```javascript
var saved = 'dark'; // ou 'light'
```

### Como exportar dados dos empréstimos?

Via Django Admin:
1. Acesse `/admin/catalog/loan/`
2. Filtre conforme necessário
3. Selecione os registros
4. No dropdown de ações, escolha uma action customizada ou use extensão de export

### Posso usar outro banco além de SQLite?

Sim. Configure `DATABASES` em `settings.py`:

**PostgreSQL:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'biblioteca',
        'USER': 'usuario',
        'PASSWORD': 'senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Depois rode:
```powershell
pip install psycopg2-binary
python manage.py migrate
```

### Onde ficam as imagens das capas?

Fisicamente em: `Django/media/book_covers/`

Acessíveis via URL: `http://127.0.0.1:8000/media/book_covers/nome_arquivo.jpg`

### Como fazer backup das imagens?

**Desenvolvimento:**
Copie a pasta `media/` regularmente.

**Produção:**
1. Configure backup automático da pasta MEDIA_ROOT
2. Ou use serviço de armazenamento (AWS S3, Google Cloud Storage)
3. Considere django-storages para integração com cloud storage

### As imagens aumentam o tamanho do banco de dados?

Não. O banco armazena apenas o **caminho do arquivo** (ex: `book_covers/capa.jpg`). As imagens ficam no sistema de arquivos.

### Posso limitar o tamanho das imagens?

Sim. Adicione validação customizada no modelo ou use biblioteca como `django-imagekit` para redimensionamento automático.

---

## Suporte e Contribuição

### Reportar Bugs

Descreva:
1. Comportamento esperado
2. Comportamento atual
3. Passos para reproduzir
4. Versão do Python e Django


---

## Licença

Este projeto foi criado para fins educacionais.

---

## Créditos

- **Framework:** Django Software Foundation
- **Python:** Python Software Foundation
- **Desenvolvido em:** Outubro 2025
