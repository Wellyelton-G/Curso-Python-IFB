# Resoluções — Aula 5

[Voltar à lista de resoluções](README.md) · [Guia da Aula 5](../Aula_05_Contas_Detalhes_e_Avaliacoes.md)

Ponto de partida: projeto ao final da Aula 5 (`gabarito/aula_05`).

---

## Exercício 1 — Nota média no acervo

> Mostre no acervo a média de estrelas de cada livro, acrescentando `average=Avg("reviews__rating")` ao `annotate` da `filter_books`. Depois rode os testes: algum número mudou? Pesquise "Django annotate multiple aggregations" para entender o que aconteceu.

### O problema

Acrescentar só o `average` parece funcionar, e os testes da aula continuam passando, mas **as cópias disponíveis ficam erradas** para livros que têm avaliações. Um exemplo real, conferido no shell:

| Situação | Disponíveis (esperado) | Disponíveis (sem correção) |
|---|:---:|:---:|
| 3 cópias, 1 empréstimo ativo, 2 avaliações | 2 | **1** |

Os testes não pegaram o erro porque nenhum teste da aula cria avaliações e empréstimos para o mesmo livro. Vale discutir isso em sala: **teste passando não significa código correto**, só que os casos testados estão corretos.

### Por que acontece

Para calcular as duas coisas numa consulta só, o banco junta três tabelas: livro, empréstimos e avaliações. Nessa junção, **cada empréstimo aparece uma vez para cada avaliação** do livro:

```
livro        empréstimo        avaliação
Dom Casmurro empréstimo #1     nota 5
Dom Casmurro empréstimo #1     nota 4     <- o mesmo empréstimo, contado de novo
```

O `Count("loans")` conta 2 empréstimos ativos em vez de 1. A média não é afetada neste caso, porque cada avaliação se repete o mesmo número de vezes.

### A resolução

**Arquivo:** `catalog/views.py` · **Ação:** substituir o `annotate` do início da `filter_books`

```python
    books = Book.objects.select_related("category").annotate(
        # Exercício 1: com dois annotate que fazem junção (loans e reviews), cada empréstimo
        # apareceria uma vez para cada avaliação. distinct=True faz cada empréstimo contar uma vez só.
        available=F("copies_total") - Count("loans", filter=Q(loans__returned_at__isnull=True), distinct=True),
        average=Avg("reviews__rating"),  # média das notas (None se o livro não tiver avaliações)
    )
```

**Arquivo:** `templates/catalog/book_list.html` · **Ação:** acrescentar a coluna "Nota" depois de "Ano"

```html
            <th>Ano</th>
            <th>Nota</th>
```

```html
              <td>{{ book.edition_year|default:"—" }}</td>
              {# Exercício 1: average vem do annotate; floatformat:1 deixa uma casa decimal #}
              <td>{% if book.average %}★ {{ book.average|floatformat:1 }}{% else %}—{% endif %}</td>
```

### O teste que faltava

```python
    def test_disponibilidade_nao_muda_com_avaliacoes(self):
        # 3 cópias, 1 empréstimo ativo e 2 avaliações: devem aparecer 2 disponíveis
        make_loan(self.book, self.maria)
        Review.objects.create(book=self.book, user=self.maria, rating=5)
        Review.objects.create(book=self.book, user=self.joao, rating=4)
        self.client.force_login(self.maria)
        response = self.client.get(reverse("catalog:book_list"))
        livro = response.context["page_obj"][0]
        self.assertEqual(livro.available, 2)
        self.assertEqual(livro.average, 4.5)
```

Sem o `distinct=True`, este teste falha com `AssertionError: 1 != 2`.

---

## Exercício 2 — Marcar avaliações editadas

> Na página do livro, mostre "(editada)" ao lado das avaliações em que `updated_at` é diferente de `created_at`.

### A armadilha

A comparação direta `updated_at != created_at` marca **todas** as avaliações como editadas. Na criação, o Django preenche os dois campos em momentos ligeiramente diferentes (com diferença de microssegundos), então eles nunca são exatamente iguais.

### A resolução

**Arquivo:** `catalog/models.py` · **Ação:** acrescentar o import no topo e uma property ao `Review`

No topo do arquivo:

```python
from datetime import timedelta
from urllib.parse import urlencode
```

Na classe `Review`, logo depois do `__str__`:

```python
    @property
    def was_edited(self):
        """Exercício 2: a avaliação foi alterada depois de criada?

        Na criação, created_at e updated_at são preenchidos com uma diferença de
        milissegundos. Por isso usamos uma folga de 1 segundo em vez de comparar com ==.
        """
        return self.updated_at - self.created_at > timedelta(seconds=1)
```

**Arquivo:** `templates/catalog/book_detail.html` · **Ação:** trocar a linha com o nome e a data da avaliação

```html
      <span class="muted">— {{ review.user.username }}, {{ review.created_at|date:"d/m/Y" }}{% if review.was_edited %} (editada){% endif %}</span>
```

**Teste:**

```python
    def test_avaliacao_editada(self):
        review = Review.objects.create(book=self.book, user=self.maria, rating=3)
        self.assertFalse(review.was_edited)
        # Simula uma edição feita um minuto depois da criação
        Review.objects.filter(pk=review.pk).update(updated_at=review.created_at + timedelta(minutes=1))
        review.refresh_from_db()
        self.assertTrue(review.was_edited)
```

O teste usa `update()` no QuerySet porque ele grava direto no banco sem passar pelo `save()`. Assim o `auto_now` não sobrescreve a data que queremos simular.

---

## Exercício 3 — Primeiro nome no cadastro

> Acrescente o campo "Primeiro nome" (`first_name`) ao `SignUpForm`.

**Arquivo:** `catalog/forms.py` · **Ação:** trocar a linha `fields` do `Meta` do `SignUpForm`

```python
        # Exercício 3: first_name já existe no model User do Django; basta incluí-lo aqui
        fields = ("username", "first_name", "email")  # as senhas já são tratadas pelo UserCreationForm
```

O `User` do Django já tem `first_name` (e `last_name`), então não é preciso criar nenhum campo nem migração. O campo aparece como opcional, porque no model ele tem `blank=True`.

**Teste:**

```python
    def test_cadastro_guarda_primeiro_nome(self):
        self.client.post(reverse("catalog:signup"), {
            "username": "ana", "first_name": "Ana", "email": "ana@exemplo.com",
            "password1": "uma-senha-bem-forte-42", "password2": "uma-senha-bem-forte-42",
        })
        self.assertEqual(User.objects.get(username="ana").first_name, "Ana")
```

---

## Exercício 4 (desafio) — Página "Minha conta"

> Crie a página "Minha conta", onde a pessoa troca o próprio e-mail. Cuidado: ao editar, o e-mail da própria pessoa já existe no banco.

### O formulário

**Arquivo:** `catalog/forms.py` · **Ação:** acrescentar no final

```python
class AccountForm(forms.ModelForm):
    """Exercício 4: formulário da página "Minha conta" (troca do e-mail)."""

    # Declarado à mão para ser obrigatório (no model User o e-mail é opcional)
    email = forms.EmailField(label="E-mail")

    class Meta:
        model = User
        fields = ["email"]

    def clean_email(self):
        """Mesmo cuidado do cadastro, mas ignorando a própria pessoa."""
        email = self.cleaned_data["email"]
        # exclude(pk=self.instance.pk): manter o próprio e-mail não conta como "repetido"
        repetido = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists()
        if repetido:
            raise forms.ValidationError("Já existe uma conta com este e-mail.")
        return email
```

O detalhe do enunciado está no `exclude(pk=self.instance.pk)`. Sem ele, quem salvasse a página sem mudar nada receberia "Já existe uma conta com este e-mail", porque o próprio e-mail já está no banco.

### A view, a rota e o template

**Arquivo:** `catalog/views.py` · **Ação:** incluir `AccountForm` no import dos formulários e acrescentar a view (por exemplo, logo depois da `signup`)

```python
from .forms import AccountForm, ReviewForm, SignUpForm
```

```python
@login_required
def my_account(request):
    """Exercício 4: a pessoa altera o próprio e-mail."""
    if request.method == "POST":
        # instance=request.user: o formulário edita o usuário logado, e não cria outro
        form = AccountForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Dados atualizados.")
            return redirect("catalog:my_account")
    else:
        form = AccountForm(instance=request.user)
    return render(request, "catalog/my_account.html", {"form": form})
```

**Arquivo:** `catalog/urls.py` · **Ação:** acrescentar a rota logo abaixo do cadastro

```python
    path("cadastro/", views.signup, name="signup"),
    path("minha-conta/", views.my_account, name="my_account"),
```

**Arquivo:** `templates/catalog/my_account.html` · **Ação:** criar

```html
{% extends "base.html" %}
{% block title %}Minha conta · Biblioteca{% endblock %}
{% block content %}
  <div class="card" style="max-width: 480px;">
    <h1>Minha conta</h1>
    <p class="muted">Usuário: {{ user.username }}</p>
    <form method="post">
      {% csrf_token %}
      {{ form.as_p }}
      <button class="btn btn-primary" type="submit">Salvar</button>
    </form>
    {# A troca de senha já vem pronta no Django (rota password_change) #}
    <p><a href="{% url 'password_change' %}">Trocar a senha</a></p>
  </div>
{% endblock %}
```

**Arquivo:** `templates/base.html` · **Ação:** transformar o "Olá, usuário" do menu em link

```html
        {# Exercício 4: o nome do usuário vira link para a página "Minha conta" #}
        <a class="user" href="{% url 'catalog:my_account' %}">Olá, {{ user.username }}</a>
```

A página de troca de senha (`password_change`) aparece com o visual do Admin, porque não criamos um template próprio para ela. Um bom exercício extra é criar `templates/registration/password_change_form.html` e `password_change_done.html`, no mesmo estilo das páginas de recuperação de senha.

### Testes

```python
    def test_minha_conta_troca_email(self):
        self.client.force_login(self.maria)
        self.client.post(reverse("catalog:my_account"), {"email": "nova@exemplo.com"})
        self.maria.refresh_from_db()
        self.assertEqual(self.maria.email, "nova@exemplo.com")

    def test_minha_conta_aceita_o_proprio_email(self):
        self.client.force_login(self.maria)
        response = self.client.post(reverse("catalog:my_account"), {"email": "maria@exemplo.com"})
        self.assertRedirects(response, reverse("catalog:my_account"))

    def test_minha_conta_recusa_email_de_outra_pessoa(self):
        self.client.force_login(self.maria)
        response = self.client.post(reverse("catalog:my_account"), {"email": "joao@exemplo.com"})
        self.assertContains(response, "Já existe uma conta com este e-mail.")
```

---

## A classe de testes completa

Os testes acima ficam juntos numa classe, no final de `catalog/tests.py`:

```python
class Aula5ExerciseTests(TestCase):
    """Testes das resoluções dos exercícios da Aula 5."""

    def setUp(self):
        self.maria = User.objects.create_user("maria", email="maria@exemplo.com", password="senha-forte-123")
        self.joao = User.objects.create_user("joao", email="joao@exemplo.com", password="senha-forte-123")
        self.book = Book.objects.create(title="Dom Casmurro", author="Machado de Assis",
                                        isbn="9788535910663", copies_total=3)
```

**Resultado esperado de `python manage.py test`:** 36 testes OK (os 30 da aula mais os 6 destas resoluções).
