# Guia de Implementação de Melhorias (Usabilidade da Lista de Livros)

Este guia explica, passo a passo, as melhorias implementadas na experiência de navegação  e uso do sistema, na lista de livros: busca, filtro de disponibilidade e paginação.

---

## Objetivo

Tornar a descoberta de livros mais rápida e intuitiva, especialmente quando o acervo cresce, permitindo:
- Pesquisar por título, autor ou ISBN.
- Filtrar apenas livros com cópias disponíveis.
- Navegar por páginas em listas longas.

---

## Resumo das melhorias

- Busca textual (GET `?q=`) aplicando filtro em título, autor e ISBN.
- Filtro de disponibilidade (GET `?disponivel=1`) para mostrar somente livros com cópias disponíveis.
- Paginação (10 itens por página) com preservação dos filtros ao navegar (GET `?page=`).

---

## Arquivos alterados

- `catalog/views.py`
  - View `book_list`: adicionada lógica de busca, filtro e paginação.
  - Novos imports: `Paginator`, `F`.
- `templates/catalog/book_list.html`
  - Formulário de busca/filtro via método GET.
  - Controles de paginação (Anterior/Próxima) preservando parâmetros.
  - Mensagens de estado (contagem, página atual).

---

## Passo a passo da implementação (com explicações)

### 1) Atualização da view `book_list` (`catalog/views.py`)

Principais ideias:
- Anotar a queryset com o número de empréstimos ativos por livro.
- Aplicar filtros a partir dos parâmetros da URL (request.GET).
- Paginar o resultado antes de enviar ao template.

Trechos relevantes (já implementados):

```python
from django.db.models import Count, Q, F
from django.core.paginator import Paginator

# ...

# Base queryset: conta empréstimos ativos por livro e ordena por título
qs = (
    Book.objects.all()
    .annotate(active_loans=Count("loans", filter=Q(loans__returned_at__isnull=True)))
    .order_by("title")
)

# Busca textual (?q=)
q = request.GET.get("q", "").strip()
if q:
    qs = qs.filter(
        Q(title__icontains=q) | Q(author__icontains=q) | Q(isbn__icontains=q)
    )

# Filtro de disponibilidade (?disponivel=1)
disponivel_param = request.GET.get("disponivel")
show_only_available = disponivel_param == "1"
if show_only_available:
    # Somente livros onde empréstimos ativos < cópias totais
    qs = qs.filter(active_loans__lt=F("copies_total"))

# Paginação (10 itens por página)
paginator = Paginator(qs, 10)
page_number = request.GET.get("page")
page_obj = paginator.get_page(page_number)

# Contexto enviado ao template
context = {
    "books": page_obj.object_list,  # lista da página atual
    "page_obj": page_obj,           # objeto de paginação (tem has_next, number, etc.)
    "q": q,                         # termo de busca (para manter no formulário)
    "show_only_available": show_only_available,  # estado do checkbox
}
```

Comentários didáticos:
- `annotate(active_loans=...)`: cria um “campo calculado” com a quantidade de empréstimos ativos (returned_at nulo). Isso permite comparar com `copies_total` sem consultas extras.
- `Q(...)`: permite filtros com OR entre título, autor e ISBN.
- `F("copies_total")`: referencia o valor da própria coluna no banco (sem trazer para memória), útil para comparar no banco.
- `Paginator(qs, 10)`: faz o split da queryset em páginas de 10 itens; `get_page()` lida com números inválidos de página.

### 2) Atualização do template `book_list.html` (`templates/catalog/book_list.html`)

Adições visíveis para o estudante:
- Campo de busca e checkbox “Somente disponíveis”.
- Botões “Filtrar” e “Limpar”.
- Navegação de páginas preservando os filtros.

Trechos relevantes (já implementados):

```html
<form method="get" style="margin-bottom: 1rem; display: flex; gap: .75rem; flex-wrap: wrap; align-items: flex-end;">
  <div style="flex:1; min-width:240px;">
    <label for="q">Buscar (título, autor ou ISBN)</label>
    <input id="q" type="text" name="q" value="{{ q }}" placeholder="Ex.: Python" style="width:100%;">
  </div>
  <div style="display:flex; align-items:center; gap:.35rem;">
    <input id="disp" type="checkbox" name="disponivel" value="1" {% if show_only_available %}checked{% endif %}>
    <label for="disp">Somente disponíveis</label>
  </div>
  <div>
    <button class="btn" type="submit">Filtrar</button>
    <a class="btn" href="{% url 'catalog:book_list' %}">Limpar</a>
  </div>
</form>
```

- O formulário usa método GET para que a busca possa ser compartilhada por URL.
- `value="{{ q }}"` e `checked` condicional preservam o estado após enviar.

Controles de paginação (preservando os filtros atuais):

```html
{% if page_obj.paginator.num_pages > 1 %}
  <nav style="margin-top:1rem; display:flex; gap:.5rem; flex-wrap:wrap; align-items:center;">
    {% if page_obj.has_previous %}
      <a class="btn" href="?q={{ q }}{% if show_only_available %}&disponivel=1{% endif %}&page={{ page_obj.previous_page_number }}">« Anterior</a>
    {% else %}
      <button class="btn" disabled>« Anterior</button>
    {% endif %}

    <span style="font-size:.8rem;">Página {{ page_obj.number }} de {{ page_obj.paginator.num_pages }}</span>

    {% if page_obj.has_next %}
      <a class="btn" href="?q={{ q }}{% if show_only_available %}&disponivel=1{% endif %}&page={{ page_obj.next_page_number }}">Próxima »</a>
    {% else %}
      <button class="btn" disabled>Próxima »</button>
    {% endif %}
  </nav>
{% endif %}
```

---

## Como testar

1) Inicie o servidor (em PowerShell, na pasta do projeto):

```powershell
# Se necessário, ative seu ambiente virtual antes
# .venv\Scripts\Activate.ps1
# pip install django pillow

python manage.py runserver
```

2) Abra no navegador e use filtros:
- Página inicial: `http://localhost:8000/`
- Exemplos de URLs:
  - `/?q=python`
  - `/?disponivel=1`
  - `/?q=algoritmos&disponivel=1&page=2`

3) Verifique:
- O campo de busca mantém o termo digitado após enviar.
- A caixa “Somente disponíveis” permanece marcada quando aplicada.
- Os botões Anterior/Próxima preservam os filtros.

4) Validação rápida do Django (opcional):

```powershell
python manage.py check
```

Se aparecer erro de que o Django não está instalado, ative seu ambiente virtual e instale as dependências:

```powershell
# Exemplo
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install django pillow
```

---

## Entendendo o porquê (didático)

- Busca melhora a “descoberta” (findability); estudantes chegam mais rápido ao que querem.
- Filtro de disponibilidade reduz frustração (evita clicar em itens indisponíveis).
- Paginação mantém a página leve e rápida (evita lista enorme de uma vez).

---

## Próximos passos sugeridos

- Ordenação dinâmica (por título, autor, disponibilidade).
- Destaque do termo buscado no resultado.
- Thumbnails otimizados (biblioteca de miniaturas) para melhorar performance.
- Exportação CSV da lista filtrada (útil para atividades acadêmicas).

---

## Rollback (caso precise desfazer)

- Reverter `catalog/views.py` para a versão anterior à introdução de `Paginator` e filtros.
- Remover o formulário GET, checkbox e paginação do `templates/catalog/book_list.html`.
- Rodar `python manage.py check` para confirmar que tudo segue íntegro.
