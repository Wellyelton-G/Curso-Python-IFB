# Guia Passo a Passo de Implementação de Melhorias - Sistema de Biblioteca


> Este guia explica detalhadamente cada passo para implementar busca, filtros e paginação em um sistema Django.

---

##  Índice

1. [Resumo das Melhorias](#resumo-das-melhorias)
2. [Pré-requisitos](#pré-requisitos)
3. [Passo a Passo Detalhado](#passo-a-passo-detalhado)
4. [Entendendo o Código](#entendendo-o-código)
5. [Como Testar](#como-testar)
6. [Troubleshooting](#troubleshooting)
7. [Referências](#referências)

---

##  Resumo das Melhorias

Vamos implementar 3 funcionalidades principais na página de listagem de livros:

| Funcionalidade | O que faz | Por que é útil |
|----------------|-----------|----------------|
| **Busca Textual** | Pesquisar por título, autor ou ISBN | Encontrar livros rapidamente em acervos grandes |
| **Filtro de Disponibilidade** | Mostrar apenas livros disponíveis | Evitar frustração de ver livros que não podem ser emprestados |
| **Paginação Personalizável** | Escolher entre 20 itens ou mostrar todos | Controlar quantos livros ver por vez |

---

## Pré-requisitos

Antes de começar, certifique-se de ter:

- [ ] Python 3.10+ instalado
- [ ] Django 4.2+ instalado
- [ ] Projeto Django funcionando
- [ ] Ambiente virtual ativado
- [ ] Conhecimento básico de:
  - Views do Django
  - Templates Django
  - QuerySets
  - URLs e parâmetros GET

---

## Passo a Passo Detalhado

### **PASSO 1: Preparar o Ambiente**

#### 1.1. Ativar o Ambiente Virtual

No PowerShell, navegue até a pasta do projeto e ative o ambiente virtual:

```powershell
cd C:\Users\SeuUsuario\Desktop\Django
.\.venv\Scripts\Activate.ps1
```

**Como saber se funcionou?**  
O prompt deve mostrar `(.venv)` no início da linha.

#### 1.2. Verificar Instalação do Django

```powershell
python -m django --version
```

**Resultado esperado:** `5.2.7` (ou similar)

#### 1.3. Fazer Backup dos Arquivos (Recomendado)

Antes de modificar, faça backup:

```powershell
# Criar pasta de backup
mkdir backup

# Copiar arquivos que vamos modificar
copy catalog\views.py backup\views.py.bak
copy templates\catalog\book_list.html backup\book_list.html.bak
```

---

### **PASSO 2: Modificar o arquivo `catalog/views.py`**

Este é o arquivo que controla a lógica da aplicação.

#### 2.1. Adicionar Novos Imports

**Localização:** Início do arquivo `catalog/views.py`

**O que estava antes:**
```python
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Book, Loan
```

**O que adicionar:**

Adicione `Paginator` e `F` aos imports existentes. A linha fica assim:

```python
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator  # ← NOVO: para dividir resultados em páginas
from django.db.models import Count, F, Q      # ← MODIFICADO: adicionado F
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Book, Loan
```

**Explicação:**
- `Paginator`: classe do Django para dividir listas em páginas
- `F`: permite comparar campos do banco de dados sem trazer dados para a memória (otimização)

---

#### 2.2. Substituir a Função `book_list`

**Localização:** Procure a função `book_list` no arquivo (geralmente por volta da linha 25)

**Código ANTIGO (o que você vai substituir):**

```python
@login_required
def book_list(request: HttpRequest) -> HttpResponse:
	"""Lista todos os livros e quantas cópias estão disponíveis.

	- annotate(active_loans=...): cria um campo calculado na consulta
	  para saber quantos empréstimos estão ativos por livro.
	- O template mostra o botão de emprestar quando há disponibilidade.
	"""
	books = (
		Book.objects.all()
		.annotate(active_loans=Count("loans", filter=Q(loans__returned_at__isnull=True)))
		.order_by("title")
	)
	return render(request, "catalog/book_list.html", {"books": books})
```

**Código NOVO (copie e cole isto):**

```python
@login_required
def book_list(request: HttpRequest) -> HttpResponse:
	"""Lista todos os livros e quantas cópias estão disponíveis.

	Funcionalidades:
	- annotate(active_loans=...): cria um campo calculado na consulta
	  para saber quantos empréstimos estão ativos por livro.
	- Busca textual por título, autor ou ISBN (parâmetro ?q=)
	- Filtro de disponibilidade (parâmetro ?disponivel=1)
	- Paginação personalizável: 20 itens por página ou todos (?mostrar=todos)
	"""
	# Base queryset: conta empréstimos ativos por livro e ordena por título
	qs = (
		Book.objects.all()
		.annotate(active_loans=Count("loans", filter=Q(loans__returned_at__isnull=True)))
		.order_by("title")
	)

	# 1) Busca textual (?q=termo)
	# Permite pesquisar por título, autor ou ISBN
	q = request.GET.get("q", "").strip()
	if q:
		qs = qs.filter(
			Q(title__icontains=q) | Q(author__icontains=q) | Q(isbn__icontains=q)
		)

	# 2) Filtro de disponibilidade (?disponivel=1)
	# Mostra apenas livros que têm cópias disponíveis
	disponivel_param = request.GET.get("disponivel")
	show_only_available = disponivel_param == "1"
	if show_only_available:
		# Filtra livros onde empréstimos ativos < cópias totais
		# F() permite comparar campos no banco sem trazer dados para memória
		qs = qs.filter(active_loans__lt=F("copies_total"))

	# 3) Paginação personalizável (?mostrar=todos ou ?mostrar=20)
	mostrar_param = request.GET.get("mostrar", "20")  # padrão: 20 itens
	
	if mostrar_param == "todos":
		# Mostrar todos os itens em uma única página
		page_obj = None
		books = qs
	else:
		# Paginação com 20 itens por página
		paginator = Paginator(qs, 20)
		page_number = request.GET.get("page")
		page_obj = paginator.get_page(page_number)
		books = page_obj.object_list

	# Contexto enviado ao template
	context = {
		"books": books,                              # lista de livros (da página atual ou todos)
		"page_obj": page_obj,                        # objeto de paginação (None se mostrar=todos)
		"q": q,                                      # termo de busca (para manter no formulário)
		"show_only_available": show_only_available,  # estado do checkbox
		"mostrar": mostrar_param,                    # opção de visualização selecionada
		"total_count": qs.count(),                   # total de resultados após filtros
	}
	
	return render(request, "catalog/book_list.html", context)
```

**ATENÇÃO:**
- Mantenha a indentação correta (use TAB ou 4 espaços)
- Não altere as outras funções do arquivo (borrow_book, return_book, etc.)
- Salve o arquivo: `Ctrl + S`

---

### **PASSO 3: Modificar o Template `templates/catalog/book_list.html`**

Este é o arquivo HTML que o usuário vê no navegador.

#### 3.1. Localizar o Arquivo

Navegue até: `templates/catalog/book_list.html`

#### 3.2. Substituir TODO o Conteúdo

**Código ANTIGO (delete tudo):**

```html
{% extends 'base.html' %}
{% block title %}Livros · Biblioteca{% endblock %}
{% block content %}
  <h1>Livros disponíveis</h1>
  {% if books %}
    <table>
      <!-- ... resto do código ... -->
    </table>
  {% else %}
    <p class="muted">Nenhum livro cadastrado.</p>
  {% endif %}
{% endblock %}
```

**Código NOVO (copie TODO este código):**

```html
{% extends 'base.html' %}
{% block title %}Livros · Biblioteca{% endblock %}
{% block content %}
  <h1>Livros disponíveis</h1>

  {# ========================================= #}
  {# BLOCO 1: FORMULÁRIO DE BUSCA E FILTROS   #}
  {# ========================================= #}
  
  <form method="get" style="margin-bottom: 1.5rem; padding: 1rem; background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 8px;">
    
    {# Linha 1: Campo de busca e seletor de paginação #}
    <div style="display: grid; grid-template-columns: 1fr auto; gap: 1rem; margin-bottom: 1rem;">
      
      {# Campo de busca #}
      <div>
        <label for="q" style="display: block; margin-bottom: 0.3rem; font-weight: 500;">
          Buscar por título, autor ou ISBN
        </label>
        <input 
          id="q" 
          type="text" 
          name="q" 
          value="{{ q }}" 
          placeholder="Ex.: Python, Machado de Assis, 9788544001196" 
          style="width: 100%; padding: 0.5rem; border: 1px solid var(--btn-border); border-radius: 4px; background: var(--bg); color: var(--text);"
        >
      </div>

      {# Seletor de paginação #}
      <div>
        <label for="mostrar" style="display: block; margin-bottom: 0.3rem; font-weight: 500;">
          Itens por página
        </label>
        <select 
          id="mostrar" 
          name="mostrar" 
          style="width: 100%; padding: 0.5rem; border: 1px solid var(--btn-border); border-radius: 4px; background: var(--bg); color: var(--text);"
        >
          <option value="20" {% if mostrar == "20" %}selected{% endif %}>20 itens</option>
          <option value="todos" {% if mostrar == "todos" %}selected{% endif %}>Mostrar todos</option>
        </select>
      </div>
    </div>

    {# Linha 2: Checkbox e botões #}
    <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
      
      {# Checkbox de disponibilidade #}
      <div style="display: flex; align-items: center; gap: 0.4rem;">
        <input 
          id="disp" 
          type="checkbox" 
          name="disponivel" 
          value="1" 
          {% if show_only_available %}checked{% endif %}
          style="cursor: pointer;"
        >
        <label for="disp" style="cursor: pointer; user-select: none;">
          Somente com cópias disponíveis
        </label>
      </div>

      {# Botões de ação #}
      <div style="margin-left: auto; display: flex; gap: 0.5rem;">
        <button class="btn" type="submit" style="background: var(--accent); color: var(--primary); font-weight: 600;">
          🔍 Filtrar
        </button>
        <a class="btn" href="{% url 'catalog:book_list' %}">
          ✖ Limpar
        </a>
      </div>
    </div>
  </form>

  {# ========================================= #}
  {# BLOCO 2: INFORMAÇÕES SOBRE OS RESULTADOS #}
  {# ========================================= #}
  
  {% if q or show_only_available %}
    <p class="muted" style="margin-bottom: 1rem;">
      {% if total_count == 0 %}
        Nenhum livro encontrado com os filtros aplicados.
      {% elif total_count == 1 %}
        1 livro encontrado.
      {% else %}
        {{ total_count }} livros encontrados.
      {% endif %}
    </p>
  {% endif %}

  {# ========================================= #}
  {# BLOCO 3: TABELA DE LIVROS                #}
  {# ========================================= #}
  
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
            {# Exibe a capa do livro se houver imagem cadastrada #}
            {% if book.image %}
              <img src="{{ book.image.url }}" alt="Capa de {{ book.title }}" style="width: 60px; height: 90px; object-fit: cover; border-radius: 4px;">
            {% else %}
              <div style="width: 60px; height: 90px; background: var(--accent); border-radius: 4px; display: flex; align-items: center; justify-content: center; color: var(--bg); font-size: 12px; text-align: center;">Sem capa</div>
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

    {# ========================================= #}
    {# BLOCO 4: CONTROLES DE PAGINAÇÃO          #}
    {# ========================================= #}
    
    {% if page_obj and page_obj.paginator.num_pages > 1 %}
      <nav style="margin-top: 1.5rem; display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: center; justify-content: center; padding: 1rem; background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 8px;">
        
        {# Botão Anterior #}
        {% if page_obj.has_previous %}
          <a class="btn" href="?q={{ q }}{% if show_only_available %}&disponivel=1{% endif %}&mostrar={{ mostrar }}&page={{ page_obj.previous_page_number }}">
            « Anterior
          </a>
        {% else %}
          <button class="btn" disabled>« Anterior</button>
        {% endif %}

        {# Informação da página atual #}
        <span style="font-size: 0.9rem; padding: 0 1rem;">
          Página <strong>{{ page_obj.number }}</strong> de <strong>{{ page_obj.paginator.num_pages }}</strong>
        </span>

        {# Botão Próxima #}
        {% if page_obj.has_next %}
          <a class="btn" href="?q={{ q }}{% if show_only_available %}&disponivel=1{% endif %}&mostrar={{ mostrar }}&page={{ page_obj.next_page_number }}">
            Próxima »
          </a>
        {% else %}
          <button class="btn" disabled>Próxima »</button>
        {% endif %}
      </nav>
    {% endif %}

    {# Mensagem quando está mostrando todos #}
    {% if mostrar == "todos" and total_count > 20 %}
      <p class="muted" style="margin-top: 1rem; text-align: center;">
        Mostrando todos os {{ total_count }} livros em uma única página.
      </p>
    {% endif %}

  {% else %}
    <p class="muted">Nenhum livro cadastrado.</p>
  {% endif %}
{% endblock %}
```

**⚠️ IMPORTANTE:**
- Copie TUDO, desde `{% extends` até `{% endblock %}`
- Substitua TODO o conteúdo anterior
- Salve o arquivo: `Ctrl + S`

---

### **PASSO 4: Verificar se Não Há Erros**

#### 4.1. Executar o Check do Django

No terminal (com ambiente virtual ativado):

```powershell
python manage.py check
```

**Resultado esperado:**
```
System check identified no issues (0 silenced).
```

**Se aparecer erro:**
- Verifique se copiou todo o código corretamente
- Confira a indentação (deve usar espaços, não TABs misturados)
- Certifique-se de que salvou os arquivos

#### 4.2. Verificar Sintaxe Python

```powershell
python -m py_compile catalog\views.py
```

**Resultado esperado:** Nenhuma saída (sem erros)

---

### **PASSO 5: Testar a Aplicação**

#### 5.1. Iniciar o Servidor

```powershell
python manage.py runserver
```

**Resultado esperado:**
```
Starting development server at http://127.0.0.1:8000/
```

#### 5.2. Abrir no Navegador

Acesse: http://127.0.0.1:8000/

**O que você deve ver:**
- Um formulário de busca no topo
- Um dropdown "Itens por página"
- Um checkbox "Somente com cópias disponíveis"
- Botões "Filtrar" e "Limpar"
- A tabela de livros abaixo

---

## 🧠 Entendendo o Código

### **Como Funciona a Busca Textual**

#### O que acontece nos bastidores:

1. **Usuário digita "Python" e clica em Filtrar**

2. **O navegador envia:** `GET /?q=Python`

3. **Django captura o parâmetro:**
```python
q = request.GET.get("q", "").strip()  # q = "Python"
```

4. **Django filtra o banco de dados:**
```python
if q:  # Se q não estiver vazio
    qs = qs.filter(
        Q(title__icontains=q) |      # Busca no título
        Q(author__icontains=q) |     # OU busca no autor
        Q(isbn__icontains=q)         # OU busca no ISBN
    )
```

5. **Resultado:** Apenas livros que contêm "Python" em algum dos 3 campos

#### Explicação dos operadores:

| Operador | Significado | Exemplo |
|----------|-------------|---------|
| `__icontains` | Contém (ignora maiúsculas) | `title__icontains="py"` encontra "Python" |
| `Q(...)` | Permite usar OR (OU) | `Q(a=1) \| Q(b=2)` significa "a=1 OU b=2" |
| `\|` | Operador OR entre Q objects | Combina múltiplas condições |
| `.strip()` | Remove espaços no início/fim | `"  Python  ".strip()` vira `"Python"` |

---

### **Como Funciona o Filtro de Disponibilidade**

#### Passo a passo:

1. **Usuário marca o checkbox "Somente com cópias disponíveis"**

2. **O navegador envia:** `GET /?disponivel=1`

3. **Django captura:**
```python
disponivel_param = request.GET.get("disponivel")  # "1"
show_only_available = disponivel_param == "1"     # True
```

4. **Django filtra:**
```python
if show_only_available:
    qs = qs.filter(active_loans__lt=F("copies_total"))
```

**O que significa `active_loans__lt=F("copies_total")`?**

- `active_loans`: campo calculado (número de empréstimos ativos)
- `__lt`: "less than" (menor que)
- `F("copies_total")`: valor do campo `copies_total` no banco
- **Tradução:** "Mostre apenas livros onde empréstimos ativos < cópias totais"

**Exemplo:**
- Livro tem 3 cópias totais
- 2 empréstimos ativos
- 2 < 3 → ✅ Livro aparece na lista
- Se tivesse 3 ou mais empréstimos → ❌ Livro NÃO aparece

#### Por que usar `F()`?

```python
# ❌ RUIM (traz dados para memória Python)
for book in books:
    if book.active_loans < book.copies_total:
        # faz algo

# ✅ BOM (comparação no banco de dados)
qs.filter(active_loans__lt=F("copies_total"))
```

**Vantagens do F():**
- Mais rápido (banco faz a comparação)
- Usa menos memória
- Aproveita índices do banco
- Só traz resultados filtrados

---

### **Como Funciona a Paginação**

#### Cenário: 45 livros cadastrados

**1. Usuário acessa a página (sem parâmetros):**

```python
mostrar_param = request.GET.get("mostrar", "20")  # padrão = "20"

# mostrar_param = "20", então vai para o else:
else:
    paginator = Paginator(qs, 20)      # Divide em páginas de 20
    page_number = request.GET.get("page")  # None (primeira vez)
    page_obj = paginator.get_page(page_number)  # Pega página 1
    books = page_obj.object_list       # Primeiros 20 livros
```

**Resultado:**
- Página 1: livros 1-20
- Página 2: livros 21-40
- Página 3: livros 41-45

**2. Usuário clica em "Próxima":**

URL vira: `/?page=2`

```python
page_number = request.GET.get("page")  # "2"
page_obj = paginator.get_page(page_number)  # Pega página 2
books = page_obj.object_list  # Livros 21-40
```

**3. Usuário seleciona "Mostrar todos":**

URL vira: `/?mostrar=todos`

```python
mostrar_param = request.GET.get("mostrar", "20")  # "todos"

if mostrar_param == "todos":
    page_obj = None   # Sem paginação
    books = qs        # TODOS os 45 livros
```

---

### **Preservação de Filtros na Navegação**

**Problema:** Usuário busca "Python" e vai para página 2. Como manter a busca?

**Solução:** Incluir todos os parâmetros nos links de navegação

```html
<a href="?q={{ q }}{% if show_only_available %}&disponivel=1{% endif %}&mostrar={{ mostrar }}&page={{ page_obj.next_page_number }}">
  Próxima »
</a>
```

**Exemplo prático:**

1. Usuário está em: `/?q=Django&disponivel=1&mostrar=20&page=1`
2. Clica em "Próxima"
3. Vai para: `/?q=Django&disponivel=1&mostrar=20&page=2`

**Breakdown do link:**
- `?q={{ q }}` → `?q=Django` (mantém a busca)
- `{% if show_only_available %}&disponivel=1{% endif %}` → `&disponivel=1` (mantém o filtro)
- `&mostrar={{ mostrar }}` → `&mostrar=20` (mantém a opção de paginação)
- `&page={{ page_obj.next_page_number }}` → `&page=2` (próxima página)

---

## 🧪 Como Testar (Passo a Passo)


### **Teste 1: Busca por Título** 🔍

**Objetivo:** Verificar se a busca encontra livros pelo título

1. Acesse: http://127.0.0.1:8000/
2. No campo "Buscar por título, autor ou ISBN", digite: `Dom`
3. Clique no botão **🔍 Filtrar**

**Resultado esperado:**
- Deve aparecer "Dom Casmurro" (se estiver cadastrado)
- Contador deve mostrar: "1 livro encontrado"
- O campo de busca deve manter o texto "Dom"

**Se não funcionar:**
- Verifique se há livros cadastrados com "Dom" no título
- Abra o console do navegador (F12) e veja se há erros JavaScript

---

### **Teste 2: Busca por Autor** 👤

1. Limpe os filtros clicando em **✖ Limpar**
2. Digite no campo de busca: `Machado`
3. Clique em **🔍 Filtrar**

**Resultado esperado:**
- Aparecem livros de Machado de Assis
- Contador mostra o número correto

---

### **Teste 3: Filtro de Disponibilidade** ✅

1. Limpe os filtros
2. Marque o checkbox **☑ Somente com cópias disponíveis**
3. Clique em **🔍 Filtrar**

**Resultado esperado:**
- Aparecem APENAS livros com cópias disponíveis (número > 0)
- Livros esgotados NÃO aparecem
- Checkbox permanece marcado

**Como criar um cenário de teste:**
```powershell
# No shell do Django
python manage.py shell
```

```python
from catalog.models import Book, Loan
from django.contrib.auth.models import User

# Ver livros e suas disponibilidades
for book in Book.objects.all():
    print(f"{book.title}: {book.copies_available} disponíveis")

# Emprestar todas as cópias de um livro para testar
book = Book.objects.first()
user = User.objects.first()
# ... criar empréstimos até esgotar
```

---

### **Teste 4: Paginação (20 itens)** 📄

**Pré-requisito:** Ter mais de 20 livros cadastrados

1. Certifique-se de que "Itens por página" está em **20 itens**
2. Clique em **🔍 Filtrar** (ou simplesmente acesse a página)

**Resultado esperado:**
- Aparecem no máximo 20 livros
- Aparecem botões de navegação embaixo: **« Anterior** | **Página 1 de X** | **Próxima »**
- Botão "Anterior" está desabilitado (primeira página)
- Botão "Próxima" está ativo (se houver mais páginas)

3. Clique em **Próxima »**

**Resultado esperado:**
- URL muda para `/?page=2`
- Aparecem os próximos 20 livros
- Indicador mostra "Página 2 de X"
- Botão "Anterior" agora está ativo

---

### **Teste 5: Mostrar Todos** 📋

1. No dropdown "Itens por página", selecione **Mostrar todos**
2. Clique em **🔍 Filtrar**

**Resultado esperado:**
- URL muda para `/?mostrar=todos`
- TODOS os livros aparecem em uma única página
- NÃO aparecem botões de navegação (Anterior/Próxima)
- Se houver mais de 20 livros, aparece mensagem: "Mostrando todos os X livros em uma única página"

---

### **Teste 6: Combinação de Filtros** 🎯

**Teste completo:** Busca + Disponibilidade + Paginação

1. Digite no campo de busca: `Python`
2. Marque ☑ **Somente com cópias disponíveis**
3. Selecione **20 itens** no dropdown
4. Clique em **🔍 Filtrar**

**Resultado esperado:**
- URL: `/?q=Python&disponivel=1&mostrar=20`
- Aparecem apenas livros Python disponíveis
- Máximo 20 por página
- Contador mostra total de resultados

5. Se houver mais de 20 resultados, clique em **Próxima »**

**Resultado esperado:**
- URL: `/?q=Python&disponivel=1&mostrar=20&page=2`
- ✅ A busca "Python" é mantida
- ✅ O filtro de disponibilidade é mantido
- ✅ A opção "20 itens" é mantida
- Mostra a segunda página de resultados

---

### **Teste 7: Limpar Filtros** ✖

1. Aplique vários filtros (busca, disponibilidade, etc.)
2. Clique no botão **✖ Limpar**

**Resultado esperado:**
- URL volta para `/` (sem parâmetros)
- Campo de busca fica vazio
- Checkbox de disponibilidade desmarcado
- Mostra todos os livros (primeira página)

---

### **Teste 8: Validação de URLs Diretas** 🔗

Digite estas URLs diretamente no navegador:

**URL 1:** `http://127.0.0.1:8000/?q=algoritmos`
- Deve buscar "algoritmos"

**URL 2:** `http://127.0.0.1:8000/?disponivel=1`
- Deve mostrar apenas disponíveis

**URL 3:** `http://127.0.0.1:8000/?mostrar=todos`
- Deve mostrar todos em uma página

**URL 4:** `http://127.0.0.1:8000/?q=django&disponivel=1&mostrar=todos`
- Deve combinar todos os filtros

**URL 5:** `http://127.0.0.1:8000/?page=999`
- Deve mostrar a última página (Django trata páginas inválidas automaticamente)

---

## 🔧 Troubleshooting (Resolução de Problemas)

### **Problema 1: "Paginator is not defined"**

**Erro:**
```
NameError: name 'Paginator' is not defined
```

**Causa:** Esqueceu de importar `Paginator`

**Solução:**
```python
# Adicione no topo de catalog/views.py
from django.core.paginator import Paginator
```

---

### **Problema 2: "F is not defined"**

**Erro:**
```
NameError: name 'F' is not defined
```

**Causa:** Esqueceu de adicionar `F` aos imports

**Solução:**
```python
# Modifique a linha de imports
from django.db.models import Count, F, Q  # ← adicione F aqui
```

---

### **Problema 3: Formulário não filtra nada**

**Sintomas:**
- Digita algo no campo de busca
- Clica em Filtrar
- Nada acontece

**Possíveis causas:**

1. **Método do formulário errado:**
```html
<!-- ❌ ERRADO -->
<form method="post">

<!-- ✅ CORRETO -->
<form method="get">
```

2. **Nome dos campos errado:**
```html
<!-- Os nomes devem ser exatamente estes: -->
<input name="q">           <!-- busca -->
<input name="disponivel">  <!-- filtro -->
<select name="mostrar">    <!-- paginação -->
```

3. **View não está capturando os parâmetros:**
```python
# Verifique se está assim:
q = request.GET.get("q", "").strip()  # não POST!
```

---

### **Problema 4: Paginação não funciona**

**Sintomas:**
- Clica em "Próxima"
- Nada muda ou dá erro

**Verificar:**

1. **Template está usando page_obj corretamente?**
```html
{% if page_obj and page_obj.paginator.num_pages > 1 %}
```

2. **Links preservam os parâmetros?**
```html
<a href="?q={{ q }}{% if show_only_available %}&disponivel=1{% endif %}&mostrar={{ mostrar }}&page={{ page_obj.next_page_number }}">
```

3. **View está passando page_obj no contexto?**
```python
context = {
    "page_obj": page_obj,  # ← deve estar aqui
    # ...
}
```

---

### **Problema 5: "TemplateSyntaxError"**

**Erro:**
```
TemplateSyntaxError at /
Invalid block tag on line X: 'elif'
```

**Causa:** Sintaxe incorreta no template

**Verificar:**
```html
<!-- ✅ CORRETO -->
{% if total_count == 0 %}
  ...
{% elif total_count == 1 %}
  ...
{% else %}
  ...
{% endif %}

<!-- ❌ ERRADO (falta endif, elif mal escrito, etc.) -->
```

---

### **Problema 6: Filtros não são preservados entre páginas**

**Sintomas:**
- Busca "Python"
- Vai para página 2
- Perde a busca

**Solução:** Verificar se os links incluem TODOS os parâmetros:

```html
<!-- ✅ CORRETO -->
<a href="?q={{ q }}{% if show_only_available %}&disponivel=1{% endif %}&mostrar={{ mostrar }}&page=2">

<!-- ❌ ERRADO (só tem page) -->
<a href="?page=2">
```

---

### **Problema 7: IndentationError**

**Erro:**
```
IndentationError: expected an indented block
```

**Causa:** Indentação incorreta no Python

**Solução:**
- Use SEMPRE 4 espaços (ou 1 TAB, mas seja consistente)
- Não misture espaços e TABs
- Configure seu editor:
  - VS Code: "Editor: Tab Size" = 4
  - Notepad++: Configurações → Linguagem → Python → TAB = 4 espaços

**Verificar indentação:**
```python
def book_list(request):  # ← sem indentação (início da função)
    qs = Book.objects.all()  # ← 4 espaços (dentro da função)
    if q:  # ← 4 espaços (mesmo nível)
        qs = qs.filter(...)  # ← 8 espaços (dentro do if)
```

---

### **Problema 8: Checkbox não marca/desmarca**

**Verificar:**

1. **Atributo `checked` está correto?**
```html
<input type="checkbox" name="disponivel" value="1" 
       {% if show_only_available %}checked{% endif %}>
```

2. **View está passando a variável?**
```python
context = {
    "show_only_available": show_only_available,  # ← deve estar aqui
}
```

3. **Nome e valor estão corretos?**
```html
<!-- O name deve ser "disponivel" e value deve ser "1" -->
<input name="disponivel" value="1">
```

---

## 📚 Conceitos Importantes para Estudantes

### **1. Parâmetros GET vs POST**

| GET | POST |
|-----|------|
| Dados na URL (`?q=Python`) | Dados no corpo da requisição |
| Visível no navegador | Oculto |
| Pode ser compartilhado | Não pode ser compartilhado |
| Usado para **busca/filtros** | Usado para **criar/modificar** dados |
| Limitado (~2000 caracteres) | Sem limite prático |

**Quando usar GET:**
- ✅ Busca
- ✅ Filtros
- ✅ Paginação
- ✅ Ordenação

**Quando usar POST:**
- ✅ Login
- ✅ Cadastro
- ✅ Emprestar livro
- ✅ Deletar registro

---

### **2. QuerySets do Django**

QuerySet é uma "consulta preparada" ao banco de dados. Ela é **lazy** (preguiçosa).

```python
# ❌ INEFICIENTE (3 consultas ao banco)
books = Book.objects.all()          # Consulta 1
filtered = books.filter(title="X")  # Consulta 2
result = list(filtered)             # Consulta 3

# ✅ EFICIENTE (1 consulta ao banco)
qs = Book.objects.all()              # Sem consulta ainda
qs = qs.filter(title="X")            # Sem consulta ainda
qs = qs.annotate(...)                # Sem consulta ainda
books = list(qs)                     # AGORA faz 1 consulta otimizada
```

**Métodos que NÃO executam a consulta:**
- `.filter()`, `.exclude()`, `.annotate()`, `.order_by()`

**Métodos que EXECUTAM a consulta:**
- `list()`, `.count()`, `for x in qs:`, `qs[0]`

---

### **3. Q Objects (Consultas Complexas)**

```python
# AND simples (E)
qs.filter(title="X", author="Y")  # título é X E autor é Y

# OR (OU) precisa de Q
from django.db.models import Q
qs.filter(Q(title="X") | Q(author="Y"))  # título é X OU autor é Y

# NOT (NÃO)
qs.filter(~Q(title="X"))  # título NÃO é X

# Combinações complexas
qs.filter(
    (Q(title="X") | Q(author="Y")) &  # (título X OU autor Y) E
    Q(copies_total__gt=0)             # cópias > 0
)
```

---

### **4. F Expressions (Comparações de Campos)**

```python
from django.db.models import F

# ❌ RUIM (Python faz a comparação)
books = Book.objects.all()
available = [b for b in books if b.active_loans < b.copies_total]

# ✅ BOM (Banco faz a comparação)
available = Book.objects.filter(active_loans__lt=F("copies_total"))
```

**Vantagens:**
- 🚀 Mais rápido
- 💾 Menos memória
- 🔒 Evita race conditions
- 📊 Aproveita índices do banco

---

### **5. Paginador do Django**

```python
from django.core.paginator import Paginator

# Criar paginador
items = [1, 2, 3, ... 100]  # 100 itens
paginator = Paginator(items, 20)  # 20 por página

# Informações
paginator.num_pages  # 5 (100 ÷ 20)
paginator.count      # 100 (total de itens)

# Pegar uma página
page1 = paginator.get_page(1)
page1.object_list    # [1, 2, 3, ... 20]
page1.has_next()     # True
page1.has_previous() # False
page1.next_page_number()  # 2

page2 = paginator.get_page(2)
page2.object_list    # [21, 22, ... 40]
```

---

## 🎓 Exercícios para Praticar

### **Exercício 1: Adicionar Busca por Editora**

**Desafio:** Adicionar campo `publisher` ao modelo Book e incluir na busca

**Dica:**
```python
# models.py
class Book(models.Model):
    publisher = models.CharField(max_length=200, blank=True)
    # ...

# views.py
qs = qs.filter(
    Q(title__icontains=q) | 
    Q(author__icontains=q) | 
    Q(isbn__icontains=q) |
    Q(publisher__icontains=q)  # ← adicione esta linha
)
```

---

### **Exercício 2: Mudar de 20 para 50 itens**

**Desafio:** Alterar a paginação para 50 itens por página

**Onde modificar:**
```python
# views.py
paginator = Paginator(qs, 50)  # mude de 20 para 50

# book_list.html
<option value="50" {% if mostrar == "50" %}selected{% endif %}>50 itens</option>
```

---

### **Exercício 3: Adicionar Ordenação**

**Desafio:** Permitir ordenar por título, autor ou data

**Dica:**
```python
# views.py
ordem = request.GET.get("ordem", "title")
if ordem == "title":
    qs = qs.order_by("title")
elif ordem == "author":
    qs = qs.order_by("author")
elif ordem == "created_at":
    qs = qs.order_by("-created_at")  # mais recentes primeiro

# template
<select name="ordem">
    <option value="title">Título</option>
    <option value="author">Autor</option>
    <option value="created_at">Data</option>
</select>
```

---

### **Exercício 4: Destacar Termo Buscado**

**Desafio:** Destacar o termo buscado em amarelo nos resultados

**Dica (JavaScript):**
```html
<script>
const q = "{{ q }}";
if (q) {
    document.querySelectorAll('td').forEach(td => {
        const regex = new RegExp(`(${q})`, 'gi');
        td.innerHTML = td.innerHTML.replace(regex, '<mark>$1</mark>');
    });
}
</script>
```

---

## 📖 Referências e Documentação

### **Documentação Oficial do Django**

1. **Pagination:**  
   https://docs.djangoproject.com/en/stable/topics/pagination/

2. **QuerySet API:**  
   https://docs.djangoproject.com/en/stable/ref/models/querysets/

3. **Q objects:**  
   https://docs.djangoproject.com/en/stable/topics/db/queries/#complex-lookups-with-q-objects

4. **F expressions:**  
   https://docs.djangoproject.com/en/stable/ref/models/expressions/#f-expressions

5. **Templates:**  
   https://docs.djangoproject.com/en/stable/topics/templates/

### **Tutoriais Recomendados**

- Django Girls Tutorial: https://tutorial.djangogirls.org/
- MDN Django Tutorial: https://developer.mozilla.org/pt-BR/docs/Learn/Server-side/Django
- Real Python Django: https://realpython.com/tutorials/django/

---

## ✅ Checklist Final

Antes de considerar a implementação completa, verifique:

### **Funcionalidades:**
- [ ] Campo de busca funciona para título
- [ ] Campo de busca funciona para autor
- [ ] Campo de busca funciona para ISBN
- [ ] Busca é case-insensitive
- [ ] Checkbox de disponibilidade filtra corretamente
- [ ] Seletor "20 itens" funciona
- [ ] Seletor "Mostrar todos" funciona
- [ ] Navegação entre páginas funciona
- [ ] Filtros são preservados ao navegar
- [ ] Contador de resultados aparece
- [ ] Contador mostra número correto
- [ ] Botão "Limpar" remove todos os filtros
- [ ] Botão "Anterior" desabilita na primeira página
- [ ] Botão "Próxima" desabilita na última página

### **Código:**
- [ ] `python manage.py check` passa sem erros
- [ ] Sem erros no console do navegador (F12)
- [ ] Indentação está correta
- [ ] Imports estão completos
- [ ] Nomes de variáveis estão corretos

### **Interface:**
- [ ] Formulário aparece no topo
- [ ] Estilo se adapta ao tema claro/escuro
- [ ] Responsivo em mobile
- [ ] Botões têm cursor pointer
- [ ] Labels estão associados aos inputs

---

##  Parabéns!

Se chegou até aqui e todos os testes passaram, você implementou com sucesso:

Sistema de busca textual  
Filtro de disponibilidade  
Paginação personalizável  
Preservação de filtros  
Interface intuitiva  

**Próximos passos sugeridos:**
1. Implementar ordenação dinâmica
2. Adicionar mais filtros (gênero, ano, etc.)
3. Criar busca com autocomplete
4. Exportar resultados para CSV
5. Adicionar gráficos de estatísticas

---

**Desenvolvido em:** Novembro de 2025  
**Sistema:** Django 5.2.7 + Python 3.13  
**Autor:** Guia para estudantes iniciantes  

 **Bons estudos e bom código!** 
