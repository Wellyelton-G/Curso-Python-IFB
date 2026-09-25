# Resoluções — Aula 6

[Voltar à lista de resoluções](README.md) · [Guia da Aula 6](../Aula_06_Relatorios_Banco_de_Dados_e_Revisao.md)

Ponto de partida: projeto ao final da Aula 6 (`gabarito/aula_06`).

Os exercícios 1 a 3 são curtos. Os exercícios 4 a 7 ("projetos para ir além") são funcionalidades completas; juntos, eles acrescentam uma migração (`renewed` em `Loan` e o model `WaitlistEntry`).

---

## Exercício 1 — Livros nunca emprestados

> Crie o relatório "Livros nunca emprestados" (título, autor e categoria).

**Arquivo:** `catalog/reports.py` · **Ação:** acrescentar a função antes do dicionário `REPORTS` e uma linha nele

```python
def never_borrowed():
    """Exercício 1: livros que nunca foram emprestados."""
    books = (
        Book.objects.filter(loans__isnull=True)  # nenhum empréstimo ligado ao livro
        .select_related("category")
        .order_by("title")
    )
    rows = [[book.title, book.author, book.category.name if book.category else ""] for book in books]
    return {"headers": ["Título", "Autor(a)", "Categoria"], "rows": rows}
```

```python
    "categorias": ("Empréstimos por categoria", loans_by_category),
    "nunca-emprestados": ("Livros nunca emprestados", never_borrowed),  # Exercício 1
```

`loans__isnull=True` atravessa a relação de volta: "livros para os quais não existe nenhum empréstimo". Não é preciso mexer em views, URLs nem templates: o relatório aparece na lista e pode ser baixado nos três formatos. É o formato comum dos relatórios em ação.

---

## Exercício 2 — Avaliações no relatório de leitores

> No relatório de leitores, acrescente uma coluna com a quantidade de avaliações de cada leitor. Atenção ao problema do `distinct`.

**Arquivo:** `catalog/reports.py` · **Ação:** substituir o `annotate` e as duas últimas linhas da função `active_readers`

```python
        User.objects.annotate(
            # Exercício 2: com a junção das avaliações, cada empréstimo se repetiria uma vez por
            # avaliação. distinct=True faz cada empréstimo (e cada avaliação) contar uma vez só.
            total=Count("loans", distinct=True),  # todos os empréstimos da pessoa
            ativos=Count("loans", filter=Q(loans__returned_at__isnull=True), distinct=True),  # só os não devolvidos
            avaliacoes=Count("reviews", distinct=True),
        )
```

```python
    rows = [[user.username, user.total, user.ativos, user.avaliacoes] for user in users]
    return {"headers": ["Leitor(a)", "Empréstimos no total", "Com ele(a) agora", "Avaliações"], "rows": rows}
```

Sem os `distinct=True`, uma leitora com 2 empréstimos e 2 avaliações apareceria com 4 empréstimos e 4 avaliações (2 × 2). É o mesmo problema do Exercício 1 da Aula 5.

---

## Exercício 3 — Teste de `loans_by_category`

> Escreva um teste para o relatório `loans_by_category`.

```python
    def test_relatorio_por_categoria(self):
        from .reports import loans_by_category

        romance = Category.objects.create(name="Romance")
        Category.objects.create(name="Tecnologia")
        self.book.category = romance
        self.book.save()
        Book.objects.create(title="Iracema", author="José de Alencar", isbn="2222222222222", category=romance)
        make_loan(self.book, self.maria)
        make_loan(self.book, self.joao, days=-5).mark_returned()
        rows = loans_by_category()["rows"]
        self.assertEqual(rows[0], ["Romance", 2, 2])  # 2 livros, 2 empréstimos
        self.assertEqual(rows[1], ["Tecnologia", 0, 0])
```

O teste cobre justamente o caso em que o `distinct=True` importa: uma categoria com vários livros e um livro com vários empréstimos. Também confere que uma categoria sem livros aparece com zeros.

---

## Preparação para os exercícios 4 a 7

Os próximos exercícios usam a constante `LOAN_DAYS` também no model. Por isso, ela passa de `views.py` para `models.py`, junto com as constantes novas.

**Arquivo:** `catalog/models.py` · **Ação:** acrescentar os imports no topo e as constantes logo antes de `class Loan`

```python
from datetime import timedelta
from decimal import Decimal  # números decimais exatos, adequados para dinheiro
from urllib.parse import urlencode  # transforma um dicionário em texto de URL: {"q": "x"} -> "q=x"
```

```python
LOAN_DAYS = 14  # prazo padrão de empréstimo, em dias
RENEWAL_DAYS = 7  # Exercício 5: quantos dias a renovação acrescenta
FINE_PER_DAY = Decimal("1.00")  # Exercício 7: multa por dia de atraso, em reais


class Loan(models.Model):
```

**Arquivo:** `catalog/views.py` · **Ação:** trocar o import dos models e a constante do topo

```python
from .models import LOAN_DAYS, Book, Category, Loan, Review, SearchQuery, WaitlistEntry
```

Onde estava `LOAN_DAYS = 14`, fica:

```python
MAX_ACTIVE_LOANS = 3  # Exercício 4: quantos livros cada leitor pode ter ao mesmo tempo
```

O `WaitlistEntry` do import é criado no Exercício 6. Se você for fazer os exercícios um de cada vez, acrescente-o ao import só quando chegar lá.

---

## Exercício 4 — Limite de 3 livros por leitor

**Arquivo:** `catalog/views.py` · **Ação:** na `borrow_book`, logo depois da regra "você já está com este livro"

```python
    # Exercício 4: limite de livros ao mesmo tempo
    active_count = request.user.loans.filter(returned_at__isnull=True).count()
    if active_count >= MAX_ACTIVE_LOANS:
        messages.error(request, f"Você já está com {MAX_ACTIVE_LOANS} livros. Devolva um para pegar outro.")
        return redirect("catalog:my_loans")
```

**Teste:**

```python
    def test_limite_de_tres_livros(self):
        for i in range(3):
            livro = Book.objects.create(title=f"Livro {i}", author="Autor", isbn=f"999000000000{i}")
            make_loan(livro, self.maria)
        self.client.force_login(self.maria)
        self.client.post(reverse("catalog:borrow_book", args=[self.book.id]))
        self.assertFalse(self.book.loans.filter(user=self.maria).exists())
```

---

## Exercício 5 — Renovação

> Um botão "Renovar" que acrescenta 7 dias ao prazo, uma única vez e só se o empréstimo não estiver atrasado.

**1. Model** — `catalog/models.py`, na classe `Loan`. Um campo novo, logo abaixo de `returned_at`:

```python
    # Exercício 5: cada empréstimo pode ser renovado uma única vez
    renewed = models.BooleanField("Renovado?", default=False)
```

E a regra e a ação, logo antes de `mark_returned`:

```python
    @property
    def can_renew(self):
        """Exercício 5: só renova quem está com o livro, dentro do prazo e ainda não renovou."""
        return self.is_active and not self.is_overdue and not self.renewed

    def renew(self):
        """Exercício 5: acrescenta RENEWAL_DAYS ao prazo e marca como renovado."""
        self.due_date = self.due_date + timedelta(days=RENEWAL_DAYS)
        self.renewed = True
        self.save(update_fields=["due_date", "renewed"])
```

**2. View** — `catalog/views.py`, logo depois da `return_book`:

```python
@login_required
@require_POST
def renew_loan(request, loan_id):
    """Exercício 5: renova um empréstimo do próprio usuário (uma única vez)."""
    loan = get_object_or_404(Loan, pk=loan_id, user=request.user)
    if not loan.can_renew:
        messages.error(request, "Este empréstimo não pode ser renovado.")
    elif loan.book.waitlist.exists():
        # Exercício 6: com gente esperando, o livro precisa voltar para a fila andar
        messages.error(request, "Há pessoas na fila de espera deste livro. Não é possível renovar.")
    else:
        loan.renew()
        messages.success(request, f"Renovado! Nova data de devolução: {loan.due_date:%d/%m/%Y}.")
    return redirect("catalog:my_loans")
```

O bloco `elif loan.book.waitlist.exists()` depende da fila de espera do Exercício 6. Se você estiver fazendo o Exercício 5 sozinho, deixe esse bloco de fora.

**3. Rota** — `catalog/urls.py`, logo abaixo da rota de devolução:

```python
    path("emprestimos/<int:loan_id>/renovar/", views.renew_loan, name="renew_loan"),  # Exercício 5
```

**4. Template** — `templates/catalog/my_loans.html`, logo depois do formulário "Devolver":

```html
                {# Exercício 5: renovação (uma vez, só dentro do prazo) #}
                {% if loan.can_renew %}
                  <form class="inline" method="post" action="{% url 'catalog:renew_loan' loan.id %}">
                    {% csrf_token %}
                    <button class="btn" type="submit">Renovar</button>
                  </form>
                {% endif %}
```

**5. Admin** (opcional) — acrescente `"renewed"` ao `list_display` do `LoanAdmin`:

```python
    list_display = ("book", "user", "borrowed_at", "due_date", "returned_at", "renewed", "atrasado")
```

**Testes:**

```python
    def test_renovar_uma_vez(self):
        loan = make_loan(self.book, self.maria, days=2)
        prazo_original = loan.due_date
        self.client.force_login(self.maria)
        self.client.post(reverse("catalog:renew_loan", args=[loan.id]))
        self.client.post(reverse("catalog:renew_loan", args=[loan.id]))  # segunda tentativa
        loan.refresh_from_db()
        self.assertEqual(loan.due_date, prazo_original + timedelta(days=7))  # só 7 dias, uma vez

    def test_nao_renova_atrasado(self):
        loan = make_loan(self.book, self.maria, days=-1)
        self.client.force_login(self.maria)
        self.client.post(reverse("catalog:renew_loan", args=[loan.id]))
        loan.refresh_from_db()
        self.assertFalse(loan.renewed)
```

---

## Exercício 6 — Fila de espera

> Quando um livro está indisponível, o leitor entra numa fila, e a equipe vê a fila na página "Com quem está?".

### As regras

1. Só é possível entrar na fila de um livro **sem cópias disponíveis**.
2. Cada pessoa ocupa **um lugar** na fila de cada livro (`UniqueConstraint`).
3. A posição é dada pela **ordem de chegada**.
4. Quando uma cópia volta, ela fica **reservada para o primeiro da fila**: outra pessoa que tente emprestar é barrada.
5. Quem estava na fila e pegou o livro **sai da fila** automaticamente.
6. Com fila formada, **não é possível renovar** o empréstimo (ver Exercício 5).

### Model

**Arquivo:** `catalog/models.py` · **Ação:** acrescentar no final

```python
class WaitlistEntry(models.Model):
    """Exercício 6: um lugar na fila de espera de um livro."""

    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="waitlist", verbose_name="Livro"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="waitlist_entries",
        verbose_name="Usuário",
    )
    created_at = models.DateTimeField("Entrou na fila em", auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]  # a ordem de chegada define a posição na fila
        verbose_name = "Lugar na fila"
        verbose_name_plural = "Fila de espera"
        constraints = [
            # Cada pessoa ocupa no máximo um lugar na fila de cada livro
            models.UniqueConstraint(fields=["book", "user"], name="um_lugar_na_fila_por_leitor"),
        ]

    def __str__(self):
        return f"{self.user} na fila de “{self.book.title}”"

    @property
    def position(self):
        """Posição na fila: 1 para quem chegou primeiro."""
        ahead = WaitlistEntry.objects.filter(book=self.book, created_at__lt=self.created_at).count()
        return ahead + 1
```

Crie a migração (ela inclui também o campo `renewed` do Exercício 5):

```powershell
python manage.py makemigrations
python manage.py migrate
```

E registre no Admin (`catalog/admin.py`), acrescentando `WaitlistEntry` ao import dos models e, no final do arquivo:

```python
@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(admin.ModelAdmin):
    """Exercício 6: fila de espera no Admin."""

    list_display = ("book", "user", "created_at")
    search_fields = ("book__title", "user__username")
```

### Views

**Arquivo:** `catalog/views.py`

**a)** Na `borrow_book`, logo depois do limite do Exercício 4, a reserva para o primeiro da fila:

```python
    # Exercício 6: se há fila, o livro que voltou fica reservado para quem está em primeiro lugar
    first_in_line = book.waitlist.first()
    if first_in_line and first_in_line.user != request.user:
        messages.error(request, f"“{book.title}” está reservado para quem está na fila de espera.")
        return redirect("catalog:book_detail", book_id=book.id)
```

**b)** Ainda na `borrow_book`, logo depois do `Loan.objects.create(...)`:

```python
    # Exercício 6: quem estava na fila e conseguiu o livro sai da fila
    book.waitlist.filter(user=request.user).delete()
```

**c)** Duas views novas, logo depois da `renew_loan`:

```python
@login_required
@require_POST
def join_waitlist(request, book_id):
    """Coloca o usuário na fila de um livro indisponível."""
    book = get_object_or_404(Book, pk=book_id)
    if book.copies_available > 0 and not book.waitlist.exists():
        messages.info(request, "Há cópias disponíveis: você pode emprestar agora mesmo.")
    elif book.loans.filter(user=request.user, returned_at__isnull=True).exists():
        messages.warning(request, "Você já está com este livro.")
    else:
        # get_or_create evita duplicar o lugar se a pessoa clicar duas vezes
        entry, _ = WaitlistEntry.objects.get_or_create(book=book, user=request.user)
        messages.success(request, f"Você está na fila. Sua posição: {entry.position}.")
    return redirect("catalog:book_detail", book_id=book.id)


@login_required
@require_POST
def leave_waitlist(request, book_id):
    """Tira o usuário da fila de um livro."""
    book = get_object_or_404(Book, pk=book_id)
    book.waitlist.filter(user=request.user).delete()
    messages.info(request, "Você saiu da fila de espera.")
    return redirect("catalog:book_detail", book_id=book.id)
```

**d)** Na `book_detail`, acrescente duas chaves ao `context`:

```python
        "user_review": reviews.filter(user=request.user).first(),
        "can_review": book.was_borrowed_by(request.user),
        # Exercício 6: o lugar do usuário na fila (ou None) e o tamanho da fila
        "waitlist_entry": book.waitlist.filter(user=request.user).first(),
        "waitlist_size": book.waitlist.count(),
    }
```

**e)** Na `book_borrowers`, envie também a fila:

```python
    loans = book.loans.filter(returned_at__isnull=True).select_related("user")
    waitlist = book.waitlist.select_related("user")  # Exercício 6: a equipe vê a fila
    return render(request, "catalog/book_borrowers.html", {"book": book, "loans": loans, "waitlist": waitlist})
```

### Rotas

**Arquivo:** `catalog/urls.py` · **Ação:** acrescentar logo abaixo da rota de renovação

```python
    path("livros/<int:book_id>/fila/entrar/", views.join_waitlist, name="join_waitlist"),  # Exercício 6
    path("livros/<int:book_id>/fila/sair/", views.leave_waitlist, name="leave_waitlist"),  # Exercício 6
```

### Templates

**`templates/catalog/book_detail.html`**: dentro do `<div class="actions">`, logo antes do comentário `{# can_review: ... #}`:

```html
        {# Exercício 6: fila de espera quando não há cópias #}
        {% if waitlist_entry %}
          <span>Você é o número {{ waitlist_entry.position }} na fila.</span>
          <form class="inline" method="post" action="{% url 'catalog:leave_waitlist' book.id %}">
            {% csrf_token %}
            <button class="btn" type="submit">Sair da fila</button>
          </form>
        {% elif book.copies_available == 0 %}
          <form class="inline" method="post" action="{% url 'catalog:join_waitlist' book.id %}">
            {% csrf_token %}
            <button class="btn" type="submit">Entrar na fila ({{ waitlist_size }} pessoa(s) esperando)</button>
          </form>
        {% endif %}
```

**`templates/catalog/book_borrowers.html`**: logo antes do link "Voltar ao acervo":

```html
  {# Exercício 6: fila de espera, na ordem de chegada #}
  <h2>Fila de espera</h2>
  {% if waitlist %}
    <ol>
      {% for entry in waitlist %}
        <li>{{ entry.user.username }} <span class="muted">(desde {{ entry.created_at|date:"d/m/Y H:i" }})</span></li>
      {% endfor %}
    </ol>
  {% else %}
    <p class="muted">Ninguém na fila.</p>
  {% endif %}
```

### Testes

```python
    def test_fila_respeita_a_ordem(self):
        make_loan(self.book, self.maria)  # única cópia com a Maria
        for pessoa in (self.joao, self.ana):
            self.client.force_login(pessoa)
            self.client.post(reverse("catalog:join_waitlist", args=[self.book.id]))
        self.assertEqual([e.user.username for e in self.book.waitlist.all()], ["joao", "ana"])
        self.assertEqual(self.book.waitlist.get(user=self.ana).position, 2)

        self.book.loans.get(user=self.maria).mark_returned()  # o livro voltou
        # Ana (segunda da fila) tenta pegar: bloqueado
        self.client.force_login(self.ana)
        self.client.post(reverse("catalog:borrow_book", args=[self.book.id]))
        self.assertFalse(self.book.loans.filter(user=self.ana).exists())
        # João (primeiro da fila) consegue e sai da fila
        self.client.force_login(self.joao)
        self.client.post(reverse("catalog:borrow_book", args=[self.book.id]))
        self.assertTrue(self.book.loans.filter(user=self.joao, returned_at__isnull=True).exists())
        self.assertFalse(WaitlistEntry.objects.filter(user=self.joao).exists())

    def test_nao_entra_na_fila_com_copia_disponivel(self):
        self.client.force_login(self.joao)
        self.client.post(reverse("catalog:join_waitlist", args=[self.book.id]))
        self.assertEqual(WaitlistEntry.objects.count(), 0)
```

**Limitação para discutir em sala:** na lista do acervo, o botão "Emprestar" aparece para todos quando a cópia volta, mesmo reservada. A view barra quem não é o primeiro da fila e explica o motivo, mas a tela poderia avisar antes. Uma melhoria possível é mostrar "Reservado" no acervo quando houver fila.

---

## Exercício 7 — Multas

> Calcule uma multa de R$ 1,00 por dia de atraso e mostre-a em "Meus empréstimos" e num relatório novo.

### Model

**Arquivo:** `catalog/models.py` · **Ação:** acrescentar à classe `Loan`, logo antes de `can_renew`

```python
    @property
    def late_days(self):
        """Exercício 7: dias de atraso, contando até a devolução (ou até hoje, se não devolveu)."""
        if self.returned_at:
            # localtime converte a data e hora da devolução para o fuso do projeto antes de pegar a data
            end = timezone.localtime(self.returned_at).date()
        else:
            end = timezone.localdate()
        return max((end - self.due_date).days, 0)

    @property
    def fine(self):
        """Exercício 7: valor da multa em reais (Decimal("0.00") quando não há atraso)."""
        return self.late_days * FINE_PER_DAY
```

Dois cuidados:

- A multa continua existindo **depois da devolução**: quem devolveu com 2 dias de atraso deve R$ 2,00. Por isso `late_days` conta até a data de devolução, e não até hoje.
- Valores em dinheiro usam **`Decimal`**, e não `float`. Com `float`, contas como `0.1 + 0.2` dão `0.30000000000000004`.

### "Meus empréstimos"

**Arquivo:** `templates/catalog/my_loans.html` · **Ação:** acrescentar a coluna "Multa" depois de "Situação"

```html
            <th>Situação</th>
            <th>Multa</th>
```

```html
              {# Exercício 7: fine é a @property do model; floatformat:2 mostra duas casas decimais #}
              <td>{% if loan.fine %}<span class="danger">R$ {{ loan.fine|floatformat:2 }}</span>{% else %}—{% endif %}</td>
```

Com o idioma `pt-br`, o `floatformat:2` já usa vírgula: `R$ 3,00`.

### Relatório

**Arquivo:** `catalog/reports.py` · **Ação:** acrescentar a função antes do dicionário `REPORTS` e uma linha nele

```python
def fines():
    """Exercício 7: empréstimos com multa (devolvidos com atraso ou ainda atrasados)."""
    # Candidatos: prazo já vencido. O valor da multa é calculado em Python pela @property fine.
    loans = (
        Loan.objects.filter(due_date__lt=timezone.localdate())
        .select_related("book", "user")
        .order_by("due_date")
    )
    rows = []
    for loan in loans:
        if loan.fine > 0:
            situacao = "Devolvido" if loan.returned_at else "Ainda com o leitor"
            valor = f"R$ {loan.fine:.2f}".replace(".", ",")  # 3.00 -> "R$ 3,00"
            rows.append([loan.book.title, loan.user.username, loan.late_days, valor, situacao])
    return {"headers": ["Livro", "Leitor(a)", "Dias de atraso", "Multa", "Situação"], "rows": rows}
```

```python
    "multas": ("Multas por atraso", fines),  # Exercício 7
```

O relatório filtra no banco só os empréstimos com prazo vencido e calcula a multa em Python. Para um acervo grande, daria para calcular tudo no banco com expressões do ORM, mas a versão em Python é mais fácil de entender e reaproveita a mesma regra do model.

### Testes

```python
    def test_multa_de_emprestimo_atrasado(self):
        loan = make_loan(self.book, self.maria, days=-3)
        self.assertEqual(loan.fine, Decimal("3.00"))

    def test_multa_continua_depois_de_devolver(self):
        loan = make_loan(self.book, self.maria, days=-2)
        loan.mark_returned()
        self.assertEqual(loan.fine, Decimal("2.00"))  # devolveu com 2 dias de atraso

    def test_relatorio_de_multas(self):
        from .reports import fines

        make_loan(self.book, self.maria, days=-4)
        make_loan(self.book, self.joao, days=5)  # em dia: sem multa
        rows = fines()["rows"]
        self.assertEqual(rows, [["Dom Casmurro", "maria", 4, "R$ 4,00", "Ainda com o leitor"]])
```

---

## A classe de testes completa

Os testes deste arquivo ficam juntos numa classe, no final de `catalog/tests.py`. O topo do arquivo ganha dois imports:

```python
from decimal import Decimal

from .models import Book, Category, Loan, Review, SearchQuery, WaitlistEntry
```

E a classe começa assim (os métodos de teste são os mostrados em cada exercício):

```python
class Aula6ExerciseTests(TestCase):
    """Testes das resoluções dos exercícios da Aula 6."""

    def setUp(self):
        self.maria = User.objects.create_user("maria", password="senha-forte-123")
        self.joao = User.objects.create_user("joao", password="senha-forte-123")
        self.ana = User.objects.create_user("ana", password="senha-forte-123")
        self.book = Book.objects.create(title="Dom Casmurro", author="Machado de Assis",
                                        isbn="1111111111111", copies_total=1)
```

O teste do Exercício 2 usa este caso:

```python
    def test_leitores_com_avaliacoes_sem_contagem_inflada(self):
        from .reports import active_readers

        make_loan(self.book, self.maria, days=-3).mark_returned()
        make_loan(self.book, self.maria)
        Review.objects.create(book=self.book, user=self.maria, rating=5)
        outro = Book.objects.create(title="Iracema", author="José de Alencar", isbn="2222222222222")
        Review.objects.create(book=outro, user=self.maria, rating=4)
        # maria: 2 empréstimos, 1 ativo, 2 avaliações
        self.assertEqual(active_readers()["rows"][0], ["maria", 2, 1, 2])
```

E o do Exercício 1:

```python
    def test_relatorio_nunca_emprestados(self):
        from .reports import never_borrowed

        Book.objects.create(title="Iracema", author="José de Alencar", isbn="2222222222222")
        make_loan(self.book, self.maria)
        self.assertEqual([row[0] for row in never_borrowed()["rows"]], ["Iracema"])
```

**Resultado esperado de `python manage.py test`:** 47 testes OK (os 36 da aula mais os 11 destas resoluções).
