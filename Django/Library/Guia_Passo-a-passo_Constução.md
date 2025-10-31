# Tutorial: Construindo um Sistema de Biblioteca com Django

> Guia completo passo a passo para criar um sistema de gerenciamento de biblioteca do zero

## 📋 Índice

1. [Visão Geral do Projeto](#1-visão-geral-do-projeto)
2. [Preparação do Ambiente](#2-preparação-do-ambiente)
3. [Criação do Projeto Django](#3-criação-do-projeto-django)
4. [Criação dos Modelos](#4-criação-dos-modelos)
5. [Configuração do Django Admin](#5-configuração-do-django-admin)
6. [Sistema de Autenticação](#6-sistema-de-autenticação)
7. [Criação das Views](#7-criação-das-views)
8. [Configuração de URLs](#8-configuração-de-urls)
9. [Criação dos Templates](#9-criação-dos-templates)
10. [Adicionando Temas (Claro/Escuro)](#10-adicionando-temas-claroescuro)
11. [Implementando Upload de Imagens](#11-implementando-upload-de-imagens)
12. [Testes Unitários](#12-testes-unitários)
13. [Dados de Exemplo](#13-dados-de-exemplo)
14. [Executando o Projeto](#14-executando-o-projeto)

---

## 1. Visão Geral do Projeto

### O Que Vamos Construir?

Um sistema completo de biblioteca com:
- **Catálogo de livros** com capas ilustrativas
- **Sistema de empréstimos** com controle de prazos
- **Painel administrativo** para gestão
- **Autenticação de usuários**
- **Interface responsiva** com tema claro/escuro
- **Upload de imagens** para capas de livros

### Tecnologias Utilizadas

- **Python 3.10+**
- **Django 5.2.7** (framework web)
- **SQLite** (banco de dados)
- **Pillow** (processamento de imagens)

### Arquitetura MTV (Model-Template-View)

```
┌─────────────────────────────────┐
│  Model (models.py)              │  ← Estrutura de dados
│  - Book, Loan                   │
├─────────────────────────────────┤
│  View (views.py)                │  ← Lógica de negócio
│  - book_list, borrow_book, etc │
├─────────────────────────────────┤
│  Template (HTML)                │  ← Apresentação
│  - book_list.html, base.html   │
└─────────────────────────────────┘
```

---

## 2. Preparação do Ambiente

### Passo 2.1: Verificar Instalação do Python

Abra o PowerShell e verifique:

```powershell
python --version
```

**Resultado esperado:** `Python 3.10.x` ou superior

Se não tiver Python instalado, baixe em: https://www.python.org/downloads/

### Passo 2.2: Criar Pasta do Projeto

```powershell
cd C:\Users\SeuUsuario\Desktop
mkdir Django
cd Django
```

### Passo 2.3: Criar Ambiente Virtual

O ambiente virtual isola as dependências do projeto:

```powershell
python -m venv .venv
```

**O que acontece:** Cria uma pasta `.venv` com cópia do Python e pip.

### Passo 2.4: Ativar Ambiente Virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

**Como saber se ativou?** Aparece `(.venv)` no início da linha do terminal.

**Problema comum:** Se der erro de política de execução, execute como Administrador:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Passo 2.5: Instalar Django e Pillow

```powershell
python -m pip install --upgrade pip
pip install "django>=4.2,<6.0" Pillow
```

**O que instalamos:**
- **Django:** Framework web completo
- **Pillow:** Biblioteca para processar imagens (necessária para ImageField)

**Verificar instalação:**
```powershell
pip list
```

Deve aparecer Django e Pillow na lista.

---

## 3. Criação do Projeto Django

### Passo 3.1: Criar Projeto Django

```powershell
django-admin startproject library .
```

**Atenção ao ponto (`.`) no final!** Ele cria o projeto na pasta atual.

**Estrutura criada:**
```
Django/
├── library/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py    ← Configurações
│   ├── urls.py        ← URLs principais
│   └── wsgi.py
└── manage.py          ← CLI do Django
```

### Passo 3.2: Criar App "catalog"

Apps são módulos funcionais dentro do projeto:

```powershell
python manage.py startapp catalog
```

**Estrutura criada:**
```
catalog/
├── __init__.py
├── admin.py       ← Configuração do admin
├── apps.py
├── models.py      ← Modelos de dados
├── tests.py       ← Testes unitários
├── views.py       ← Lógica de negócio
└── migrations/    ← Migrações do banco
```

### Passo 3.3: Registrar App no Projeto

Abra `library/settings.py` e adicione `'catalog'` em `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'catalog',  # ← ADICIONE ESTA LINHA
]
```

**Por que?** Django precisa saber que este app existe.

### Passo 3.4: Configurar Idioma e Timezone

No mesmo arquivo `library/settings.py`, encontre e altere:

```python
# Linha ~106
LANGUAGE_CODE = 'pt-br'  # Antes era 'en-us'

# Linha ~108
TIME_ZONE = 'America/Sao_Paulo'  # Antes era 'UTC'
```

### Passo 3.5: Configurar Pasta de Templates

Ainda em `settings.py`, encontre `TEMPLATES` (linha ~55) e altere `'DIRS'`:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # ← ADICIONE ISTO
        'APP_DIRS': True,
        # ...
    },
]
```

### Passo 3.6: Configurar URLs de Autenticação

No final de `settings.py`, adicione:

```python
# Redirecionamentos de autenticação
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'catalog:book_list'
LOGOUT_REDIRECT_URL = 'login'
```

**O que faz:**
- `LOGIN_URL`: Para onde redireciona se não estiver logado
- `LOGIN_REDIRECT_URL`: Para onde vai após fazer login
- `LOGOUT_REDIRECT_URL`: Para onde vai após logout

### Passo 3.7: Configurar Media Files

Adicione no final de `settings.py`:

```python
# Media files (uploads de usuários)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**O que faz:**
- `MEDIA_URL`: Prefixo da URL (ex: `/media/book_covers/capa.jpg`)
- `MEDIA_ROOT`: Pasta física onde os uploads são salvos

---

## 4. Criação dos Modelos

### Passo 4.1: Entender os Modelos

Vamos criar dois modelos:
1. **Book** (Livro): Representa um título do acervo
2. **Loan** (Empréstimo): Representa um empréstimo de livro para usuário

### Passo 4.2: Criar Modelo Book

Abra `catalog/models.py` e substitua todo o conteúdo por:

```python
from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Cast
from django.utils import timezone


class Book(models.Model):
    """Livro do acervo da biblioteca."""
    
    # Campos básicos
    title = models.CharField(max_length=255, verbose_name="Título")
    author = models.CharField(max_length=255, verbose_name="Autor")
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    copies_total = models.PositiveIntegerField(default=1, verbose_name="Total de cópias")
    
    # Campo para upload de imagem (capa do livro)
    # blank=True: permite vazio no formulário
    # null=True: permite NULL no banco de dados
    # upload_to: subpasta onde as imagens serão salvas
    image = models.ImageField(
        upload_to='book_covers/', 
        blank=True, 
        null=True,
        verbose_name="Capa"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Cadastrado em")

    class Meta:
        ordering = ["title"]  # Ordena por título
        verbose_name = "Livro"
        verbose_name_plural = "Livros"

    def __str__(self):
        """Representação em texto do objeto."""
        return f"{self.title} — {self.author}"

    @property
    def copies_available(self):
        """Calcula quantas cópias estão disponíveis agora."""
        # Conta empréstimos ativos (returned_at é NULL)
        active_loans = self.loans.filter(returned_at__isnull=True).count()
        return max(self.copies_total - active_loans, 0)
```

**Explicação dos campos:**
- `CharField`: Texto curto (título, autor)
- `PositiveIntegerField`: Número inteiro positivo (cópias)
- `ImageField`: Campo para upload de imagem (requer Pillow)
- `DateTimeField`: Data e hora
- `unique=True`: Não permite duplicatas (ISBN)
- `@property`: Método que pode ser acessado como atributo

### Passo 4.3: Criar Modelo Loan

No mesmo arquivo `catalog/models.py`, adicione após a classe Book:

```python
class Loan(models.Model):
    """Empréstimo de um livro para um usuário."""
    
    # Relacionamentos (ForeignKey = chave estrangeira)
    book = models.ForeignKey(
        Book, 
        on_delete=models.CASCADE,  # Se livro for deletado, deleta empréstimos
        related_name="loans",  # Permite acessar book.loans
        verbose_name="Livro"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Modelo de usuário do Django
        on_delete=models.CASCADE,
        related_name="loans",
        verbose_name="Usuário"
    )
    
    # Datas
    borrowed_at = models.DateTimeField(auto_now_add=True, verbose_name="Emprestado em")
    due_date = models.DateField(verbose_name="Devolver até")
    returned_at = models.DateTimeField(null=True, blank=True, verbose_name="Devolvido em")

    class Meta:
        ordering = ["-borrowed_at"]  # Mais recentes primeiro (- = decrescente)
        verbose_name = "Empréstimo"
        verbose_name_plural = "Empréstimos"
        
        # Constraint: garante que due_date não seja antes de borrowed_at
        constraints = [
            models.CheckConstraint(
                check=Q(due_date__gte=Cast(F("borrowed_at"), output_field=models.DateField())),
                name="loan_due_after_borrowed",
            ),
        ]

    def __str__(self):
        status = "devolvido" if self.returned_at else "emprestado"
        return f"{self.book.title} para {self.user.username} ({status})"

    @property
    def is_active(self):
        """Verifica se o empréstimo está ativo (não devolvido)."""
        return self.returned_at is None

    @property
    def is_overdue(self):
        """Verifica se o empréstimo está atrasado."""
        return self.is_active and timezone.localdate() > self.due_date

    def mark_returned(self):
        """Marca o empréstimo como devolvido."""
        if not self.returned_at:
            self.returned_at = timezone.now()
            self.save(update_fields=["returned_at"])
```

**Conceitos importantes:**
- `ForeignKey`: Relacionamento N para 1 (muitos empréstimos → 1 livro)
- `related_name`: Nome reverso do relacionamento
- `on_delete=CASCADE`: Se o livro for deletado, deleta empréstimos também
- `CheckConstraint`: Regra de validação no banco de dados
- `@property`: Atributo calculado dinamicamente

### Passo 4.4: Criar Migrações

Migrações são scripts que criam/alteram tabelas no banco:

```powershell
python manage.py makemigrations
```

**Saída esperada:**
```
Migrations for 'catalog':
  catalog\migrations\0001_initial.py
    + Create model Book
    + Create model Loan
```

### Passo 4.5: Aplicar Migrações

```powershell
python manage.py migrate
```

**O que acontece:** Django cria as tabelas no banco de dados SQLite (`db.sqlite3`).

**Saída esperada:**
```
Running migrations:
  Applying catalog.0001_initial... OK
  (e outras...)
```

---

## 5. Configuração do Django Admin

O Django Admin é um painel pronto para gerenciar dados.

### Passo 5.1: Registrar Modelos no Admin

Abra `catalog/admin.py` e substitua todo o conteúdo:

```python
from django.contrib import admin
from django.utils import timezone
from .models import Book, Loan


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Configuração do Book no Django Admin."""
    
    # Colunas exibidas na listagem
    list_display = ("title", "author", "isbn", "copies_total", "copies_available")
    
    # Campos pesquisáveis
    search_fields = ("title", "author", "isbn")
    
    # Campos somente leitura (calculados)
    readonly_fields = ("created_at",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    """Configuração do Loan no Django Admin."""
    
    list_display = ("book", "user", "borrowed_at", "due_date", "returned_at", "_is_overdue")
    list_filter = ("returned_at",)  # Filtro lateral
    search_fields = ("book__title", "user__username")  # Busca em relacionamentos
    actions = ("marcar_como_devolvido",)  # Ação customizada

    @admin.display(boolean=True, description="Atrasado")
    def _is_overdue(self, obj):
        """Exibe ícone de alerta se atrasado."""
        return obj.is_overdue

    @admin.action(description="Marcar como devolvido")
    def marcar_como_devolvido(self, request, queryset):
        """Ação em massa para marcar empréstimos como devolvidos."""
        updated = 0
        now = timezone.now()
        
        # Só marca os que ainda não foram devolvidos
        for loan in queryset.filter(returned_at__isnull=True):
            loan.returned_at = now
            loan.save(update_fields=["returned_at"])
            updated += 1
        
        # Mensagem de sucesso
        self.message_user(request, f"{updated} empréstimo(s) marcados como devolvidos.")
```

**Recursos configurados:**
- `list_display`: Colunas na tabela
- `search_fields`: Campos pesquisáveis na barra de busca
- `list_filter`: Filtros laterais
- `actions`: Ações em massa (seleciona vários e executa)
- `@admin.display`: Customiza exibição de campos
- `@admin.action`: Cria ação customizada

### Passo 5.2: Criar Superusuário

```powershell
python manage.py createsuperuser
```

**Preencha:**
- Username: `admin`
- Email: (pode deixar em branco)
- Password: `admin123`
- Password (again): `admin123`

**Dica:** Para senha fraca, confirme com `y`.

### Passo 5.3: Testar o Admin

```powershell
python manage.py runserver
```

Acesse: http://127.0.0.1:8000/admin/

Login com `admin` / `admin123`.

---

## 6. Sistema de Autenticação

### Passo 6.1: Criar Template de Login

Crie a estrutura de pastas:

```powershell
mkdir templates
mkdir templates\registration
```

Crie o arquivo `templates/registration/login.html`:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login · Biblioteca</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
        }
        h1 {
            margin-bottom: 30px;
            color: #333;
            text-align: center;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .error {
            background: #fee;
            border: 1px solid #fcc;
            color: #c33;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>🏛️ Biblioteca</h1>
        
        {% if form.errors %}
            <div class="error">
                Usuário ou senha incorretos.
            </div>
        {% endif %}

        <form method="post">
            {% csrf_token %}
            
            <div class="form-group">
                <label for="{{ form.username.id_for_label }}">Usuário:</label>
                {{ form.username }}
            </div>
            
            <div class="form-group">
                <label for="{{ form.password.id_for_label }}">Senha:</label>
                {{ form.password }}
            </div>
            
            <button type="submit">Entrar</button>
        </form>
    </div>
</body>
</html>
```

**Conceitos:**
- `{% csrf_token %}`: Proteção contra ataques CSRF (obrigatório em formulários POST)
- `{{ form.username }}`: Renderiza campo do formulário
- `{% if form.errors %}`: Mostra erros de validação

---

## 7. Criação das Views

Views são funções que processam requisições e retornam respostas.

### Passo 7.1: Criar Views de Usuários

Abra `catalog/views.py` e substitua todo o conteúdo:

```python
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Book, Loan


# ========== VIEWS PARA USUÁRIOS COMUNS ==========

@login_required
def book_list(request):
    """Lista todos os livros com quantidade disponível."""
    # Anotação: adiciona campo calculado 'active_loans' em cada livro
    books = Book.objects.annotate(
        active_loans=Count('loans', filter=Q(loans__returned_at__isnull=True))
    )
    return render(request, 'catalog/book_list.html', {'books': books})


@login_required
def borrow_book(request, book_id):
    """Permite emprestar um livro."""
    if request.method != 'POST':
        return redirect('catalog:book_list')
    
    book = get_object_or_404(Book, pk=book_id)
    
    # Verifica se há cópias disponíveis
    if book.copies_available <= 0:
        messages.error(request, f"Não há cópias disponíveis de '{book.title}'.")
        return redirect('catalog:book_list')
    
    # Cria o empréstimo com prazo de 14 dias
    due_date = timezone.localdate() + timedelta(days=14)
    Loan.objects.create(
        book=book,
        user=request.user,
        due_date=due_date
    )
    
    messages.success(
        request, 
        f"Livro '{book.title}' emprestado com sucesso! Devolva até {due_date.strftime('%d/%m/%Y')}."
    )
    return redirect('catalog:book_list')


@login_required
def return_book(request, loan_id):
    """Permite devolver um livro."""
    if request.method != 'POST':
        return redirect('catalog:my_loans')
    
    loan = get_object_or_404(Loan, pk=loan_id)
    
    # Verifica se é o dono do empréstimo
    if loan.user != request.user:
        messages.error(request, "Você não pode devolver um empréstimo de outro usuário.")
        return redirect('catalog:my_loans')
    
    # Verifica se já foi devolvido
    if loan.returned_at:
        messages.warning(request, "Este livro já foi devolvido.")
        return redirect('catalog:my_loans')
    
    # Marca como devolvido
    loan.mark_returned()
    messages.success(request, f"Livro '{loan.book.title}' devolvido com sucesso!")
    return redirect('catalog:my_loans')


@login_required
def my_loans(request):
    """Lista todos os empréstimos do usuário logado."""
    loans = Loan.objects.filter(user=request.user).select_related('book')
    return render(request, 'catalog/my_loans.html', {'loans': loans})
```

**Conceitos importantes:**
- `@login_required`: Só permite acesso se estiver logado
- `get_object_or_404()`: Busca objeto ou retorna erro 404
- `messages`: Sistema de mensagens temporárias (feedback ao usuário)
- `select_related()`: Otimização para evitar queries N+1
- `annotate()`: Adiciona campos calculados na query

### Passo 7.2: Criar Views de Administradores

Adicione no mesmo arquivo `catalog/views.py`:

```python
# ========== VIEWS PARA ADMINISTRADORES (STAFF) ==========

def _is_staff(user):
    """Verifica se o usuário é staff (administrador)."""
    return user.is_staff


@login_required
@user_passes_test(_is_staff)
def admin_overdue_loans(request):
    """Lista todos os empréstimos atrasados."""
    today = timezone.localdate()
    loans = Loan.objects.filter(
        returned_at__isnull=True,  # Ainda não devolvidos
        due_date__lt=today  # Data de devolução passou
    ).select_related('book', 'user')
    
    return render(request, 'catalog/admin_overdue.html', {'loans': loans})


@login_required
@user_passes_test(_is_staff)
def admin_book_borrowers(request, book_id):
    """Mostra quem está com um livro específico."""
    book = get_object_or_404(Book, pk=book_id)
    active_loans = book.loans.filter(returned_at__isnull=True).select_related('user')
    
    return render(request, 'catalog/admin_book_borrowers.html', {
        'book': book,
        'active_loans': active_loans
    })


@login_required
@user_passes_test(_is_staff)
def admin_mark_returned(request, loan_id):
    """Permite admin marcar empréstimo como devolvido."""
    if request.method != 'POST':
        return redirect('catalog:admin_overdue_loans')
    
    loan = get_object_or_404(Loan, pk=loan_id)
    
    if loan.returned_at:
        messages.warning(request, "Este empréstimo já foi marcado como devolvido.")
    else:
        loan.mark_returned()
        messages.success(request, f"Empréstimo de '{loan.book.title}' marcado como devolvido.")
    
    return redirect('catalog:admin_overdue_loans')
```

**Conceitos:**
- `@user_passes_test()`: Restringe acesso baseado em teste customizado
- `_is_staff()`: Função auxiliar para verificar permissão
- `filter()`: Filtra registros do banco

---

## 8. Configuração de URLs

### Passo 8.1: Criar URLs do App Catalog

Crie o arquivo `catalog/urls.py`:

```python
from django.urls import path
from . import views

# Namespace permite referenciar URLs como 'catalog:book_list'
app_name = 'catalog'

urlpatterns = [
    # URLs para usuários comuns
    path('', views.book_list, name='book_list'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:loan_id>/', views.return_book, name='return_book'),
    path('me/loans/', views.my_loans, name='my_loans'),
    
    # URLs para administradores (prefixo /staff/)
    path('staff/overdue/', views.admin_overdue_loans, name='admin_overdue_loans'),
    path('staff/book/<int:book_id>/borrowers/', views.admin_book_borrowers, name='admin_book_borrowers'),
    path('staff/loan/<int:loan_id>/return/', views.admin_mark_returned, name='admin_mark_returned'),
]
```

**Conceitos:**
- `app_name`: Define namespace para evitar conflitos
- `<int:book_id>`: Captura parâmetro inteiro da URL
- `name`: Nome da rota (usado em `{% url 'name' %}`)

### Passo 8.2: Configurar URLs Principais

Abra `library/urls.py` e substitua todo o conteúdo:

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # App catalog (raiz do site)
    path('', include('catalog.urls', namespace='catalog')),
    
    # Redirecionamento de compatibilidade
    path('admin/overdue/', RedirectView.as_view(pattern_name='catalog:admin_overdue_loans', permanent=False)),
]

# Servir arquivos de media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**Conceitos:**
- `include()`: Inclui URLs de outro arquivo
- `auth_views`: Views prontas do Django para login/logout
- `static()`: Serve arquivos de media em desenvolvimento
- `RedirectView`: Redireciona URL antiga para nova

---

## 9. Criação dos Templates

### Passo 9.1: Criar Template Base

Crie `templates/base.html`:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Biblioteca{% endblock %}</title>
    <style>
        /* Variáveis CSS para tema claro (padrão) */
        :root {
            --bg: #ffffff;
            --text: #333333;
            --muted: #666666;
            --primary: #667eea;
            --accent: #e0e7ff;
            --danger: #dc2626;
            --border: #e5e7eb;
        }

        /* Variáveis para tema escuro */
        .theme-dark {
            --bg: #1a1a1a;
            --text: #e5e5e5;
            --muted: #a3a3a3;
            --primary: #818cf8;
            --accent: #312e81;
            --danger: #f87171;
            --border: #404040;
        }

        /* Reset e estilos globais */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            transition: background 0.3s, color 0.3s;
        }

        /* Header / Menu */
        header {
            background: var(--primary);
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }

        nav h1 {
            font-size: 1.5rem;
        }

        nav ul {
            list-style: none;
            display: flex;
            gap: 1.5rem;
            align-items: center;
        }

        nav a {
            color: white;
            text-decoration: none;
            font-weight: 500;
            transition: opacity 0.2s;
        }

        nav a:hover {
            opacity: 0.8;
        }

        /* Botão de tema */
        #theme-toggle {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1.2rem;
            transition: background 0.2s;
        }

        #theme-toggle:hover {
            background: rgba(255,255,255,0.3);
        }

        /* Container principal */
        main {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }

        /* Mensagens de feedback */
        .messages {
            margin-bottom: 1.5rem;
        }

        .message {
            padding: 1rem;
            border-radius: 6px;
            margin-bottom: 0.5rem;
        }

        .message.success {
            background: #d1fae5;
            color: #065f46;
            border: 1px solid #10b981;
        }

        .message.error {
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #ef4444;
        }

        .message.warning {
            background: #fef3c7;
            color: #92400e;
            border: 1px solid #f59e0b;
        }

        /* Tabelas */
        table {
            width: 100%;
            border-collapse: collapse;
            background: var(--bg);
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }

        thead {
            background: var(--accent);
        }

        th, td {
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }

        th {
            font-weight: 600;
            color: var(--text);
        }

        tr:hover {
            background: var(--accent);
        }

        /* Botões */
        .btn, button[type="submit"] {
            background: var(--primary);
            color: white;
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: transform 0.2s, opacity 0.2s;
        }

        .btn:hover, button[type="submit"]:hover {
            transform: translateY(-2px);
            opacity: 0.9;
        }

        .btn:disabled, button[type="submit"]:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        /* Classes utilitárias */
        .muted {
            color: var(--muted);
        }

        .danger {
            color: var(--danger);
        }

        /* Formulários inline (para não quebrar layout) */
        form {
            display: inline;
        }

        /* Logout como botão (não como link) */
        form button.logout-btn {
            background: transparent;
            border: 1px solid white;
            padding: 0.5rem 1rem;
        }

        form button.logout-btn:hover {
            background: rgba(255,255,255,0.2);
            transform: none;
        }
    </style>
</head>
<body>
    <header>
        <nav>
            <h1>Biblioteca</h1>
            <ul>
                {% if user.is_authenticated %}
                    <li><a href="{% url 'catalog:book_list' %}">Livros</a></li>
                    <li><a href="{% url 'catalog:my_loans' %}">Meus empréstimos</a></li>
                    
                    {% if user.is_staff %}
                        <li><a href="{% url 'catalog:admin_overdue_loans' %}">Atrasados</a></li>
                        <li><a href="{% url 'admin:index' %}">Admin</a></li>
                    {% endif %}
                    
                    <li>
                        <button id="theme-toggle" type="button">☀️</button>
                    </li>
                    
                    <li>
                        <form method="post" action="{% url 'logout' %}">
                            {% csrf_token %}
                            <button type="submit" class="logout-btn">Sair</button>
                        </form>
                    </li>
                {% endif %}
            </ul>
        </nav>
    </header>

    <main>
        <!-- Mensagens de feedback (success, error, warning) -->
        {% if messages %}
            <div class="messages">
                {% for message in messages %}
                    <div class="message {{ message.tags }}">{{ message }}</div>
                {% endfor %}
            </div>
        {% endif %}

        <!-- Conteúdo da página -->
        {% block content %}{% endblock %}
    </main>

    <script>
        // Sistema de tema claro/escuro
        (function() {
            const root = document.documentElement;
            const toggleBtn = document.getElementById('theme-toggle');
            
            // Função para aplicar tema
            function apply(theme) {
                if (theme === 'dark') {
                    root.classList.add('theme-dark');
                    toggleBtn.textContent = '🌙';
                } else {
                    root.classList.remove('theme-dark');
                    toggleBtn.textContent = '☀️';
                }
                localStorage.setItem('theme', theme);
            }
            
            // Carrega tema salvo ou detecta preferência do sistema
            const saved = localStorage.getItem('theme');
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            apply(saved || (prefersDark ? 'dark' : 'light'));
            
            // Toggle ao clicar
            toggleBtn.addEventListener('click', function() {
                const current = root.classList.contains('theme-dark') ? 'dark' : 'light';
                apply(current === 'dark' ? 'light' : 'dark');
            });
        })();
    </script>
</body>
</html>
```

**Recursos implementados:**
- Sistema de tema claro/escuro com CSS variables
- Persistência com localStorage
- Detecção de preferência do sistema
- Menu responsivo
- Sistema de mensagens
- Estilos para tabelas e botões

### Passo 9.2: Criar Template de Listagem de Livros

Crie a pasta e arquivo:

```powershell
mkdir templates\catalog
```

Crie `templates/catalog/book_list.html`:

```html
{% extends 'base.html' %}
{% block title %}Livros · Biblioteca{% endblock %}
{% block content %}
  <h1>Livros disponíveis</h1>
  {% if books %}
    <table>
      <thead>
        <tr>
          <th>Capa</th>
          <th>Título</th>
          <th>Autor</th>
          <th>ISBN</th>
          <th>Disponíveis</th>
          <th>Ação</th>
        </tr>
      </thead>
      <tbody>
      {% for book in books %}
        <tr>
          <td>
            {% if book.image %}
              <img src="{{ book.image.url }}" alt="Capa de {{ book.title }}" 
                   style="width: 60px; height: 90px; object-fit: cover; border-radius: 4px;">
            {% else %}
              <div style="width: 60px; height: 90px; background: var(--accent); 
                          border-radius: 4px; display: flex; align-items: center; 
                          justify-content: center; color: var(--bg); font-size: 12px; 
                          text-align: center;">Sem capa</div>
            {% endif %}
          </td>
          <td>{{ book.title }}</td>
          <td>{{ book.author }}</td>
          <td class="muted">{{ book.isbn }}</td>
          <td>{{ book.copies_available }}</td>
          <td>
            {% if book.copies_available > 0 %}
              <form method="post" action="{% url 'catalog:borrow_book' book.id %}">
                {% csrf_token %}
                <button class="btn" type="submit">Emprestar</button>
              </form>
            {% else %}
              <button class="btn" disabled>Indisponível</button>
            {% endif %}
          </td>
        </tr>
      {% endfor %}
      </tbody>
    </table>
  {% else %}
    <p class="muted">Nenhum livro cadastrado.</p>
  {% endif %}
{% endblock %}
```

### Passo 9.3: Criar Template de Meus Empréstimos

Crie `templates/catalog/my_loans.html`:

```html
{% extends 'base.html' %}
{% block title %}Meus empréstimos · Biblioteca{% endblock %}
{% block content %}
  <h1>Meus empréstimos</h1>
  {% if loans %}
    <table>
      <thead>
        <tr>
          <th>Capa</th>
          <th>Livro</th>
          <th>Emprestado em</th>
          <th>Devolver até</th>
          <th>Status</th>
          <th>Ação</th>
        </tr>
      </thead>
      <tbody>
      {% for loan in loans %}
        <tr>
          <td>
            {% if loan.book.image %}
              <img src="{{ loan.book.image.url }}" alt="Capa de {{ loan.book.title }}" 
                   style="width: 50px; height: 75px; object-fit: cover; border-radius: 4px;">
            {% else %}
              <div style="width: 50px; height: 75px; background: var(--accent); 
                          border-radius: 4px; display: flex; align-items: center; 
                          justify-content: center; color: var(--bg); font-size: 10px; 
                          text-align: center;">Sem capa</div>
            {% endif %}
          </td>
          <td>{{ loan.book.title }}</td>
          <td>{{ loan.borrowed_at|date:'d/m/Y H:i' }}</td>
          <td>{{ loan.due_date|date:'d/m/Y' }}</td>
          <td>
            {% if loan.returned_at %}
              <span class="muted">Devolvido em {{ loan.returned_at|date:'d/m/Y H:i' }}</span>
            {% elif loan.is_overdue %}
              <strong class="danger">Atrasado</strong>
            {% else %}
              <span>Ativo</span>
            {% endif %}
          </td>
          <td>
            {% if not loan.returned_at %}
              <form method="post" action="{% url 'catalog:return_book' loan.id %}">
                {% csrf_token %}
                <button class="btn" type="submit">Devolver</button>
              </form>
            {% endif %}
          </td>
        </tr>
      {% endfor %}
      </tbody>
    </table>
  {% else %}
    <p class="muted">Você ainda não possui empréstimos.</p>
  {% endif %}
{% endblock %}
```

### Passo 9.4: Criar Templates Admin

Crie `templates/catalog/admin_overdue.html`:

```html
{% extends 'base.html' %}
{% block title %}Atrasados · Biblioteca{% endblock %}
{% block content %}
  <h1>Empréstimos atrasados</h1>
  {% if loans %}
    <table>
      <thead>
        <tr>
          <th>Livro</th>
          <th>Usuário</th>
          <th>Devolver até</th>
          <th>Emprestado em</th>
          <th>Ação</th>
        </tr>
      </thead>
      <tbody>
      {% for loan in loans %}
        <tr>
          <td>{{ loan.book.title }}</td>
          <td>{{ loan.user.get_username }}</td>
          <td class="danger">{{ loan.due_date|date:'d/m/Y' }}</td>
          <td>{{ loan.borrowed_at|date:'d/m/Y H:i' }}</td>
          <td>
            <form method="post" action="{% url 'catalog:admin_mark_returned' loan.id %}">
              {% csrf_token %}
              <button class="btn" type="submit">Marcar devolvido</button>
            </form>
          </td>
        </tr>
      {% endfor %}
      </tbody>
    </table>
  {% else %}
    <p class="muted">Sem empréstimos atrasados.</p>
  {% endif %}
{% endblock %}
```

Crie `templates/catalog/admin_book_borrowers.html`:

```html
{% extends 'base.html' %}
{% block title %}Quem emprestou · Biblioteca{% endblock %}
{% block content %}
  <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
    {% if book.image %}
      <img src="{{ book.image.url }}" alt="Capa de {{ book.title }}" 
           style="width: 100px; height: 150px; object-fit: cover; border-radius: 8px; 
                  box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
    {% else %}
      <div style="width: 100px; height: 150px; background: var(--accent); 
                  border-radius: 8px; display: flex; align-items: center; 
                  justify-content: center; color: var(--bg); font-size: 12px; 
                  text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">Sem capa</div>
    {% endif %}
    <div>
      <h1 style="margin: 0 0 10px 0;">Quem emprestou: {{ book.title }}</h1>
      <p style="margin: 0; color: var(--muted);">{{ book.author }}</p>
    </div>
  </div>
  
  {% if active_loans %}
    <ul>
      {% for loan in active_loans %}
        <li>{{ loan.user.get_username }} — desde {{ loan.borrowed_at|date:'d/m/Y H:i' }}, 
            devolução {{ loan.due_date|date:'d/m/Y' }}</li>
      {% endfor %}
    </ul>
  {% else %}
    <p class="muted">Nenhum empréstimo ativo para este livro.</p>
  {% endif %}
{% endblock %}
```

---

## 10. Adicionando Temas (Claro/Escuro)

O tema já está implementado no `base.html`! Funciona assim:

### Como Funciona:

1. **CSS Variables:** Define cores em `:root` e `.theme-dark`
2. **JavaScript:** Toggle entre classes
3. **localStorage:** Salva preferência do usuário
4. **matchMedia:** Detecta preferência do sistema operacional

**Já implementado no Passo 9.1!**

---

## 11. Implementando Upload de Imagens

### Passo 11.1: Verificar Campo Image

O campo `image` já foi adicionado no modelo Book (Passo 4.2).

### Passo 11.2: Criar e Aplicar Migração

Se ainda não criou:

```powershell
python manage.py makemigrations
python manage.py migrate
```

### Passo 11.3: Testar Upload

1. Acesse `/admin/catalog/book/`
2. Adicione ou edite um livro
3. No campo "Capa", clique em "Choose File"
4. Selecione uma imagem
5. Salve

A imagem será salva em `media/book_covers/`.

---

## 12. Testes Unitários

### Passo 12.1: Criar Testes

Abra `catalog/tests.py` e substitua todo o conteúdo:

```python
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Book, Loan

User = get_user_model()


class LoanModelTests(TestCase):
    """Testes para o modelo Loan."""

    def setUp(self):
        """Prepara dados para os testes."""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.book = Book.objects.create(
            title='Livro Teste',
            author='Autor Teste',
            isbn='1234567890123',
            copies_total=1
        )

    def test_overdue_logic(self):
        """Testa se empréstimo atrasado é detectado corretamente."""
        # Cria empréstimo com data passada
        loan = Loan.objects.create(
            book=self.book,
            user=self.user,
            due_date=timezone.localdate() - timedelta(days=1)
        )
        self.assertTrue(loan.is_overdue)
        self.assertTrue(loan.is_active)

    def test_mark_returned_sets_timestamp(self):
        """Testa se marcar como devolvido define timestamp."""
        loan = Loan.objects.create(
            book=self.book,
            user=self.user,
            due_date=timezone.localdate() + timedelta(days=7)
        )
        
        self.assertIsNone(loan.returned_at)
        loan.mark_returned()
        self.assertIsNotNone(loan.returned_at)
        self.assertFalse(loan.is_active)

    def test_copies_available_counts_active_loans(self):
        """Testa cálculo de cópias disponíveis."""
        # Inicialmente tem 1 cópia disponível
        self.assertEqual(self.book.copies_available, 1)
        
        # Empresta o livro
        Loan.objects.create(
            book=self.book,
            user=self.user,
            due_date=timezone.localdate() + timedelta(days=7)
        )
        
        # Agora tem 0 cópias disponíveis
        self.assertEqual(self.book.copies_available, 0)


class AuthViewsTests(TestCase):
    """Testes para views de autenticação."""

    def test_logout_requires_post_and_redirects(self):
        """Testa se logout requer POST e redireciona."""
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        
        # POST deve funcionar
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # GET não deve funcionar (Django 5.x)
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
```

### Passo 12.2: Executar Testes

```powershell
python manage.py test
```

**Saída esperada:**
```
Ran 4 tests in 0.123s

OK
```

---

## 13. Dados de Exemplo

### Passo 13.1: Criar Livros de Exemplo

Abra o shell do Django:

```powershell
python manage.py shell
```

Execute:

```python
from catalog.models import Book

Book.objects.create(
    title="1984",
    author="George Orwell",
    isbn="9780451524935",
    copies_total=3
)

Book.objects.create(
    title="O Senhor dos Anéis",
    author="J.R.R. Tolkien",
    isbn="9788533613379",
    copies_total=2
)

Book.objects.create(
    title="Harry Potter e a Pedra Filosofal",
    author="J.K. Rowling",
    isbn="9788532530787",
    copies_total=5
)

print("3 livros criados com sucesso!")
exit()
```

### Passo 13.2: Criar Usuário de Teste

Se ainda não criou superusuário, crie agora:

```powershell
python manage.py createsuperuser
```

Preencha:
- Username: `admin`
- Password: `admin123`

---

## 14. Executando o Projeto

### Passo 14.1: Ativar Ambiente Virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

### Passo 14.2: Iniciar Servidor

```powershell
python manage.py runserver
```

### Passo 14.3: Acessar o Sistema

**Página de Login:**
http://127.0.0.1:8000/login/

**Django Admin:**
http://127.0.0.1:8000/admin/

**Página Principal (após login):**
http://127.0.0.1:8000/

### Passo 14.4: Testar Funcionalidades

1. **Login** com `admin` / `admin123`
2. **Ver livros** na página inicial
3. **Emprestar** um livro
4. **Ver empréstimos** em "Meus empréstimos"
5. **Devolver** o livro
6. **Adicionar capa** pelo admin (`/admin/catalog/book/`)
7. **Testar tema** clicando no botão ☀️/🌙

---

## Parabéns!

Você construiu um sistema web de biblioteca com Django!

### O Que Você Aprendeu:

Estrutura de projetos Django  
Models, Views e Templates (MTV)  
Sistema de autenticação  
Django Admin  
Relacionamentos (ForeignKey)  
Queries com ORM  
Upload de arquivos (ImageField)  
Templates com herança  
Sistema de mensagens  
CSS Variables e temas  
Testes unitários  
Migrações de banco  


---

## Recursos Adicionais

**Documentação Oficial:**
- Django: https://docs.djangoproject.com/
- Pillow: https://pillow.readthedocs.io/

**Tutoriais:**
- Django Girls: https://tutorial.djangogirls.org/pt/
- MDN Django Tutorial: https://developer.mozilla.org/pt-BR/docs/Learn/Server-side/Django

**Comunidade:**
- Django Brasil (Telegram): https://t.me/django_br
- Stack Overflow: https://stackoverflow.com/questions/tagged/django

---

**Criado por:** Sistema de Biblioteca v1.0  
**Data:** Outubro 2025  
**Licença:** Educacional
