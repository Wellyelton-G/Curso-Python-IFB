# Guia Passo a Passo – Implementação de Melhorias na Biblioteca Django

**Data:** 13/11/2025

Este guia detalha, passo a passo, como implementar as principais melhorias no sistema de biblioteca Django. O objetivo é ajudar estudantes a aprender fazendo, indicando exatamente onde e como modificar cada arquivo.

---

## 1. Fila de Espera para Empréstimo

**Arquivos:**
- `catalog/models.py`
- `catalog/views.py`
- `catalog/templates/catalog/book_detail.html`

**Passos:**
1. **Modelagem:**
   - Adicione o modelo `Waitlist` em `models.py` relacionando usuários e livros.
2. **View:**
   - Implemente funções para adicionar/remover usuários da fila em `views.py`.
3. **Template:**
   - Exiba a posição do usuário e a fila completa no template do livro.

---

## 2. Avaliação e Comentários de Livros

**Arquivos:**
- `catalog/models.py`
- `catalog/views.py`
- `catalog/templates/catalog/book_detail.html`

**Passos:**
1. **Modelagem:**
   - Crie o modelo `BookRating` em `models.py`.
2. **View:**
   - Implemente a lógica para salvar avaliações e comentários em `views.py`.
3. **Template:**
   - Mostre média de avaliações e comentários no template do livro.

---

## 3. Histórico de Pesquisas

**Arquivos:**
- `catalog/models.py`
- `catalog/views.py`
- `catalog/templates/catalog/search_history.html`

**Passos:**
1. **Modelagem:**
   - Adicione o modelo `SearchQuery` em `models.py`.
2. **View:**
   - Salve cada busca realizada pelo usuário em `views.py`.
3. **Template:**
   - Crie uma página para exibir o histórico de buscas.

---

## 4. Busca Avançada de Livros

**Arquivos:**
- `catalog/views.py`
- `catalog/templates/catalog/book_list.html`

**Passos:**
1. **View:**
   - Implemente filtros avançados na view de listagem de livros.
2. **Template:**
   - Adicione campos de filtro (autor, categoria, ano, idioma, disponibilidade) no template.

---

## 5. Controle de Multas por Atraso

**Arquivos:**
- `catalog/models.py`
- `catalog/views.py`
- `catalog/templates/catalog/loan_history.html`

**Passos:**
1. **Modelagem:**
   - Adicione campo de multa ao modelo de empréstimo.
2. **View:**
   - Calcule multas e registre pagamentos em `views.py`.
3. **Template:**
   - Exiba multas e status de pagamento no histórico de empréstimos.

---

## Exemplos de Código para Implementação

### 1. Fila de Espera para Empréstimo

**catalog/models.py**
```python
class Waitlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)
    class Meta:
        unique_together = ('user', 'book')
```

**catalog/views.py**
```python
@login_required
def join_waitlist(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    Waitlist.objects.get_or_create(user=request.user, book=book)
    messages.success(request, "Você entrou na fila de espera!")
    return redirect('catalog:book_detail', book_id=book.id)
```

**templates/catalog/book_detail.html**
```html
<!-- Exibir posição na fila -->
{% if waitlist_position %}
  <p>Sua posição na fila: {{ waitlist_position }}</p>
{% endif %}
<!-- Botão para entrar na fila -->
<form method="post" action="{% url 'catalog:join_waitlist' book.id %}">
  {% csrf_token %}
  <button type="submit">Entrar na fila de espera</button>
</form>
```

---

### 2. Avaliação e Comentários de Livros

**catalog/models.py**
```python
class BookRating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'book')
```

**catalog/views.py**
```python
@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    ratings = book.ratings.all()
    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
    # ... lógica para salvar avaliação ...
    return render(request, "catalog/book_detail.html", {
        "book": book,
        "ratings": ratings,
        "avg_rating": avg_rating,
        # outros contextos
    })
```

**templates/catalog/book_detail.html**
```html
<h4>Média de avaliação: {% if avg_rating %}{{ avg_rating|floatformat:1 }}{% else %}-{% endif %} / 5</h4>
<div>
  {% for r in ratings %}
    <strong>{{ r.user.username }}</strong> — {{ r.rating }} estrela(s)
    <br><small>{{ r.created_at|date:'d/m/Y H:i' }}</small>
    {% if r.comment %}<em>{{ r.comment }}</em>{% endif %}
  {% empty %}
    <p>Nenhuma avaliação ainda.</p>
  {% endfor %}
</div>
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Enviar avaliação</button>
</form>
```

---

### 3. Histórico de Pesquisas

**catalog/models.py**
```python
class SearchQuery(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)
```

**catalog/views.py**
```python
@login_required
def search_books(request):
    query = request.GET.get('q')
    if query:
        SearchQuery.objects.create(user=request.user, query=query)
    # ... lógica de busca ...
```

**templates/catalog/search_history.html**
```html
<h3>Seu histórico de buscas</h3>
<ul>
  {% for s in search_history %}
    <li>{{ s.query }} — {{ s.searched_at|date:'d/m/Y H:i' }}</li>
  {% empty %}
    <li>Nenhuma busca registrada.</li>
  {% endfor %}
</ul>
```

---

## Dicas Gerais
- Sempre coloque os imports no topo dos arquivos Python.
- Após modificar modelos, rode `python manage.py makemigrations` e `python manage.py migrate`.
- Teste cada funcionalidade acessando as páginas correspondentes no navegador.
- Use mensagens de erro e o terminal para identificar e corrigir problemas.

---

**Este guia pode ser expandido conforme novas funcionalidades forem implementadas.**
