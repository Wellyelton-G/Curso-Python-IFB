# Resoluções — Aula 4

[Voltar à lista de resoluções](README.md) · [Guia da Aula 4](../Aula_04_Categorias_Busca_Avancada_e_Exportacao.md)

Ponto de partida: projeto ao final da Aula 4 (`gabarito/aula_04`).

---

## Exercício 1 — Ordenação "Título (Z–A)"

> Acrescente a ordenação "Título (Z–A)" ao `ORDER_OPTIONS`. Quantas linhas do template precisaram mudar? Por quê?

**Arquivo:** `catalog/views.py` · **Ação:** acrescentar uma linha ao dicionário `ORDER_OPTIONS`

```python
    "title": ("Título (A–Z)", ["title"]),
    "title_desc": ("Título (Z–A)", ["-title"]),  # Exercício 1: basta esta linha
```

**Resposta:** **nenhuma** linha do template. Os `<select>` de ordenação são montados com um `for` sobre `order_options`, que a view gera a partir do próprio `ORDER_OPTIONS`. A opção nova aparece sozinha no acervo e na busca avançada, e a `filter_books` já sabe aplicá-la. É a vantagem de guardar as opções num dicionário, em vez de espalhá-las em `if/elif` e no HTML.

---

## Exercício 2 — Descrição da categoria como dica

> Cadastre uma descrição para cada categoria no Admin e mostre-a como dica (`title`) nas opções do `<select>`.

**Arquivo:** `templates/catalog/book_list.html` · **Ação:** acrescentar o atributo `title` ao `<option>` de categoria

```html
            {# Exercício 2: o atributo title mostra a descrição ao passar o mouse #}
            <option value="{{ category.id }}" title="{{ category.description }}" {% if params.categoria == category.id|stringformat:"s" %}selected{% endif %}>
```

**Como conferir:** no Admin, em **Categorias**, preencha a descrição de "Romance". No acervo, abra a lista de categorias e pare o mouse sobre "Romance". Alguns navegadores não mostram dicas dentro de listas suspensas; no Firefox e no Chrome para computador elas aparecem.

---

## Exercício 3 — Apagar o histórico

> Na página de histórico, crie um botão para apagar todo o histórico do usuário. Use POST.

**Arquivo:** `catalog/views.py` · **Ação:** acrescentar a view (por exemplo, logo antes da `export_books`)

```python
@login_required
@require_POST  # apagar altera dados: só por formulário POST
def clear_search_history(request):
    """Exercício 3: apaga todo o histórico de buscas do usuário logado."""
    # delete() num QuerySet apaga todos os registros de uma vez; devolve (total, detalhes)
    total, _ = request.user.searches.all().delete()
    messages.success(request, f"{total} busca(s) removida(s) do histórico.")
    return redirect("catalog:search_history")
```

**Arquivo:** `catalog/urls.py` · **Ação:** acrescentar a rota logo abaixo da rota do histórico

```python
    path("historico/", views.search_history, name="search_history"),
    path("historico/limpar/", views.clear_search_history, name="clear_search_history"),
```

**Arquivo:** `templates/catalog/search_history.html` · **Ação:** acrescentar o formulário logo depois de `{% if searches %}`

```html
  {% if searches %}
    {# Exercício 3: formulário POST com csrf_token, porque apaga dados #}
    <form method="post" action="{% url 'catalog:clear_search_history' %}">
      {% csrf_token %}
      <button class="btn" type="submit">Apagar todo o histórico</button>
    </form>
    <div class="table-wrap">
```

O ponto de segurança é o mesmo da devolução: `request.user.searches` só alcança as buscas do usuário logado, então ninguém apaga o histórico de outra pessoa.

**Testes** (em `catalog/tests.py`, dentro de uma classe de testes com `self.user` logado):

```python
    def test_apagar_historico(self):
        self.client.get(reverse("catalog:book_list"), {"q": "duna"})
        self.client.post(reverse("catalog:clear_search_history"))
        self.assertEqual(self.user.searches.count(), 0)

    def test_apagar_historico_exige_post(self):
        response = self.client.get(reverse("catalog:clear_search_history"))
        self.assertEqual(response.status_code, 405)
```

---

## Exercício 4 (desafio) — Filtro "até N páginas"

> Acrescente ao `Book` o campo `pages` e um filtro "até N páginas" na busca avançada. Percorra todo o caminho: model → migração → `filter_books` → template → teste.

**1. Model** — `catalog/models.py`, na classe `Book`, logo abaixo de `edition_year`:

```python
    edition_year = models.PositiveSmallIntegerField("Ano de edição", null=True, blank=True)
    # Exercício 4: número de páginas (opcional, para não exigir valor dos livros antigos)
    pages = models.PositiveIntegerField("Páginas", null=True, blank=True)
```

**2. Migração:**

```powershell
python manage.py makemigrations
python manage.py migrate
```

**3. Admin** (opcional, para cadastrar as páginas) — em `catalog/admin.py`, acrescente `"pages"` ao `list_display` do `BookAdmin`:

```python
    list_display = ("title", "author", "category", "language", "edition_year", "pages",
                    "copies_total", "copies_available")
```

**4. Filtro** — `catalog/views.py`. Acrescente `"paginas_max"` a `SEARCH_FIELDS`, para que a busca entre no histórico:

```python
SEARCH_FIELDS = ["q", "title", "author", "publisher", "categoria", "idioma", "ano_min", "ano_max", "disponivel",
                 "paginas_max"]
```

E, dentro de `filter_books`, logo depois do filtro de disponibilidade:

```python
    if params.get("disponivel") == "1":
        books = books.filter(available__gt=0)

    # Exercício 4: livros com até N páginas (livros sem o número de páginas ficam de fora)
    paginas_max = params.get("paginas_max", "")
    if paginas_max.isdigit():
        books = books.filter(pages__lte=int(paginas_max))
```

**5. Template** — `templates/catalog/advanced_search.html`, antes do campo "Ordenar por":

```html
      <div>
        {# Exercício 4: o name precisa ser igual ao parâmetro lido em filter_books #}
        <label for="paginas_max">Até quantas páginas</label>
        <input id="paginas_max" type="number" name="paginas_max" placeholder="Ex.: 300">
      </div>
```

**6. Teste** — `catalog/tests.py`, numa classe com três livros (um de 680 páginas, um de 150 e um sem o número de páginas):

```python
    def test_filtro_ate_n_paginas(self):
        response = self.client.get(reverse("catalog:book_list"), {"paginas_max": "300"})
        self.assertEqual(self.titles(response), ["Iracema"])
```

A classe de testes completa usada para conferir estas resoluções:

```python
class Aula4ExerciseTests(TestCase):
    """Testes das resoluções dos exercícios da Aula 4."""

    def setUp(self):
        self.user = User.objects.create_user("maria", password="senha-forte-123")
        self.client.force_login(self.user)
        Book.objects.create(title="Duna", author="Frank Herbert", isbn="1111111111111", pages=680)
        Book.objects.create(title="Iracema", author="José de Alencar", isbn="2222222222222", pages=150)
        Book.objects.create(title="Sapiens", author="Yuval Noah Harari", isbn="3333333333333")  # sem páginas

    def titles(self, response):
        return [book.title for book in response.context["page_obj"]]

    def test_ordenar_titulo_z_a(self):
        response = self.client.get(reverse("catalog:book_list"), {"ordenar": "title_desc"})
        self.assertEqual(self.titles(response), ["Sapiens", "Iracema", "Duna"])

    def test_filtro_ate_n_paginas(self):
        response = self.client.get(reverse("catalog:book_list"), {"paginas_max": "300"})
        self.assertEqual(self.titles(response), ["Iracema"])

    def test_apagar_historico(self):
        self.client.get(reverse("catalog:book_list"), {"q": "duna"})
        self.client.post(reverse("catalog:clear_search_history"))
        self.assertEqual(self.user.searches.count(), 0)

    def test_apagar_historico_exige_post(self):
        response = self.client.get(reverse("catalog:clear_search_history"))
        self.assertEqual(response.status_code, 405)
```

**Resultado esperado de `python manage.py test`:** 26 testes OK (os 22 da aula mais os 4 destas resoluções).
