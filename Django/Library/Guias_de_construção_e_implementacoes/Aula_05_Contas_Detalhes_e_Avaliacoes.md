# Aula 5 — Contas de usuário, página do livro e avaliações

Sistema de Biblioteca com Django · Aula 5 de 10 · [Roteiro do curso](README.md)

## Objetivos da aula

- Entender os **formulários** do Django (`Form` e `ModelForm`) e a **validação**.
- Permitir que o leitor **crie a própria conta** (cadastro com e-mail).
- Ativar a **recuperação de senha** por e-mail.
- Criar a **página de detalhes** de cada livro.
- Permitir **avaliações com estrelas e comentários**, com duas regras: só avalia quem já pegou o livro emprestado, e cada pessoa avalia um livro uma única vez.
- Calcular a **média das notas** com **agregação** no banco.

Ao final da aula, qualquer pessoa cria a própria conta, recupera a senha esquecida, e os leitores avaliam os livros que leram.

| Aula 1 | Aula 2 | Aula 3 | Aula 4 | Aula 5 | Aula 6 | Aula 7 | Aula 8 | Aula 9 | Aula 10 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Concluída | Concluída | Concluída | Concluída | **Aula atual** | Relatórios e banco | Publicação | API REST | Qualidade de código | Git em equipe |

## Antes de começar

- [ ] Ambiente virtual ativo.
- [ ] `python manage.py test` mostra 22 testes OK (Aula 4).

---

## Parte 1 — Conceitos

### 1.1 Formulários no Django

Até agora nossos formulários eram HTML escrito à mão (a busca) ou já vinham prontos do Django (o login). Para criar e editar dados, o Django oferece classes de formulário que fazem quatro coisas:

1. **Desenham** os campos em HTML (`{{ form.as_p }}`).
2. **Recebem** os dados enviados (`form = MeuForm(request.POST)`).
3. **Validam**: campo obrigatório, e-mail válido, nota entre 1 e 5... (`form.is_valid()`).
4. **Mostram os erros** ao lado de cada campo, sem apagar o que a pessoa digitou.

| Classe | Quando usar |
|---|---|
| `forms.Form` | formulário que não grava num model (um formulário de contato, por exemplo) |
| `forms.ModelForm` | formulário ligado a um model: os campos saem do model e `form.save()` grava no banco |

### 1.2 O roteiro de uma view com formulário

Toda view com formulário segue o mesmo roteiro:

```python
if request.method == "POST":            # a pessoa ENVIOU o formulário
    form = MeuForm(request.POST)        # 1. preenche com o que chegou
    if form.is_valid():                 # 2. valida
        form.save()                     # 3. grava
        return redirect(...)            # 4. Post/Redirect/Get (Aula 2)
    # se for inválido, segue para o render abaixo, MOSTRANDO OS ERROS
else:                                   # a pessoa só ABRIU a página (GET)
    form = MeuForm()                    # formulário vazio
return render(request, "pagina.html", {"form": form})
```

### 1.3 Regras no banco e regras no código

A regra "cada pessoa avalia um livro uma vez só" pode ficar em dois lugares:

- **No código** (na view): funciona, mas se outra parte do sistema passar a criar avaliações, ela pode esquecer de conferir.
- **No banco**, com uma **`UniqueConstraint`**: o próprio banco recusa a segunda avaliação, venha de onde vier.

Vamos usar as duas. O banco é a última linha de defesa, e a view oferece uma experiência melhor: em vez de dar erro, ela **edita** a avaliação existente.

### 1.4 Agregação

Na Aula 3, o `annotate` acrescentou um valor a **cada livro**. Agora queremos um único número para um conjunto de linhas, como a média das notas de um livro. Para isso existe o `aggregate`:

```python
from django.db.models import Avg, Count

# Devolve um dicionário com o resultado do conjunto todo
book.reviews.aggregate(average=Avg("rating"), total=Count("id"))
# {'average': 4.5, 'total': 2}
```

| | Devolve | Exemplo |
|---|---|---|
| `annotate(...)` | um QuerySet, com um valor calculado em cada linha | cópias disponíveis de cada livro |
| `aggregate(...)` | um dicionário com o resultado do conjunto todo | a média das notas de um livro |

---

## Parte 2 — Cadastro e recuperação de senha

### Passo 1 — Envio de e-mails

Na recuperação de senha, o Django envia um e-mail com um link. Em desenvolvimento não vamos configurar um servidor de e-mail: pedimos ao Django para mostrar a mensagem no terminal.

**Arquivo:** `library/settings.py` · **Ação:** adicionar no final do arquivo

```python
# E-mail: em desenvolvimento, as mensagens aparecem no terminal em vez de serem enviadas
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Biblioteca <nao-responda@biblioteca.local>'  # remetente dos e-mails
```

Num servidor de verdade, bastaria trocar o `EMAIL_BACKEND` pelo SMTP de um provedor de e-mail. O resto do código não muda.

### Passo 2 — Os formulários

**Arquivo:** `catalog/forms.py` · **Ação:** criar

```python
from django import forms
from django.contrib.auth.forms import UserCreationForm  # formulário de cadastro que já vem no Django
from django.contrib.auth.models import User

from .models import Review


class SignUpForm(UserCreationForm):
    """Formulário de cadastro: o do Django (usuário + senha duas vezes) com e-mail obrigatório."""

    # Campo novo, acrescentado aos campos que o UserCreationForm já tem
    email = forms.EmailField(label="E-mail", help_text="Usado para recuperar a senha.")

    class Meta(UserCreationForm.Meta):  # herda a configuração do formulário original
        model = User
        fields = ("username", "email")  # as senhas já são tratadas pelo UserCreationForm

    def clean_email(self):
        """Validação extra: não aceitar um e-mail que já tem conta.

        O Django chama sozinho todo método clean_<nome_do_campo> durante o is_valid().
        """
        email = self.cleaned_data["email"]  # valor já validado como e-mail
        # __iexact compara sem diferenciar maiúsculas: ANA@x.com e ana@x.com são o mesmo e-mail
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Já existe uma conta com este e-mail.")
        return email  # o método precisa devolver o valor aprovado


class ReviewForm(forms.ModelForm):
    """Formulário de avaliação: o usuário só preenche nota e comentário."""

    # Declaramos a nota "à mão" para usar botões de rádio sem a opção vazia "---------".
    # coerce=int converte o valor recebido (texto) em número.
    rating = forms.TypedChoiceField(
        label="Nota", choices=Review.RATING_CHOICES, coerce=int, widget=forms.RadioSelect
    )

    class Meta:
        model = Review
        # Livro e usuário ficam de fora de propósito: quem preenche é a view, não o navegador
        fields = ["rating", "comment"]
        widgets = {
            # Textarea é uma caixa de texto com várias linhas
            "comment": forms.Textarea(attrs={"rows": 4, "placeholder": "O que você achou do livro?"}),
        }
```

Este arquivo importa o model `Review`, que só será criado no Passo 6. Até lá o servidor mostra `ImportError`, o que é esperado: siga os passos na ordem.

#### Entendendo o código

**`SignUpForm`.** O Django já traz um formulário de cadastro, o `UserCreationForm`, com nome de usuário, senha e confirmação de senha, incluindo as validações de senha forte. Nós herdamos dele e acrescentamos o e-mail. O `class Meta(UserCreationForm.Meta)` herda a configuração original e só troca a lista de `fields`.

**`clean_email`** é uma validação personalizada. O Django chama automaticamente todo método `clean_<campo>` durante o `is_valid()`. O `raise forms.ValidationError(...)` recusa o valor, e a mensagem aparece ao lado do campo. Exigimos e-mail único porque a recuperação de senha é feita pelo e-mail: duas contas com o mesmo endereço receberiam os links uma da outra.

**`ReviewForm`** é um `ModelForm`: os campos são gerados a partir do model. Livro e usuário ficam de fora **de propósito**. A view preenche os dois, para que ninguém consiga enviar um formulário avaliando em nome de outra pessoa. O campo `rating` foi declarado à mão (campos declarados na classe têm prioridade sobre os gerados) para mostrar botões de rádio sem a opção vazia "---------".

### Passo 3 — A view de cadastro

**Arquivo:** `catalog/views.py` · **Ação:** quatro alterações

**3.1)** Logo abaixo da linha `from django.contrib import messages ...`, acrescente:

```python
from django.contrib.auth import login  # faz o login de um usuário pelo código
```

**3.2)** Troque a linha `from django.db.models import Count, F, Q ...` por (vamos usar o `Avg` no Passo 7):

```python
from django.db.models import Avg, Count, F, Q  # ferramentas para montar consultas (Avg = média)
```

**3.3)** Troque a linha `from .models import Book, Category, Loan, SearchQuery` por:

```python
from .forms import ReviewForm, SignUpForm
from .models import Book, Category, Loan, Review, SearchQuery
```

**3.4)** Localize o comentário `# ---------- Área da equipe (staff) ----------` e cole logo acima dele:

```python
# ---------- Contas de usuário ----------


def signup(request):
    """Cadastro de novos leitores. Depois de criar a conta, a pessoa já entra no sistema."""
    # Quem já está logado não precisa se cadastrar
    if request.user.is_authenticated:
        return redirect("catalog:book_list")

    if request.method == "POST":
        # A pessoa enviou o formulário: preenchemos com os dados recebidos
        form = SignUpForm(request.POST)
        if form.is_valid():  # roda todas as validações (senha forte, e-mail único...)
            user = form.save()  # cria o usuário, com a senha criptografada
            login(request, user)  # já deixa a pessoa logada
            messages.success(request, f"Bem-vindo(a), {user.username}! Sua conta foi criada.")
            return redirect("catalog:book_list")
        # Se for inválido, segue para o render abaixo com o form cheio de mensagens de erro
    else:
        # A pessoa só abriu a página: formulário vazio
        form = SignUpForm()

    return render(request, "registration/signup.html", {"form": form})
```

A view segue o roteiro da seção 1.2. Ela não tem `@login_required`, é claro: quem vai se cadastrar ainda não tem conta. O Django nunca guarda a senha em texto puro: `form.save()` grava a senha criptografada.

### Passo 4 — Templates de cadastro e de recuperação de senha

**4.1) Página de cadastro**

**Arquivo:** `templates/registration/signup.html` · **Ação:** criar

```html
{% extends "base.html" %}
{% block title %}Criar conta · Biblioteca{% endblock %}
{% block content %}
  <div class="card" style="max-width: 480px; margin: 40px auto;">
    <h1>Criar conta</h1>
    <form method="post">
      {% csrf_token %}
      {# as_p desenha cada campo com o rótulo, o texto de ajuda e as mensagens de erro #}
      {{ form.as_p }}
      <button class="btn btn-primary" type="submit">Cadastrar</button>
    </form>
    <p class="muted">Já tem conta? <a href="{% url 'login' %}">Entrar</a></p>
  </div>
{% endblock %}
```

**4.2) Links na tela de login**

**Arquivo:** `templates/registration/login.html` · **Ação:** substituir todo o conteúdo

```html
{% extends "base.html" %}
{# extends precisa ser a primeira linha: esta página herda o layout do base.html #}
{% block title %}Entrar · Biblioteca{% endblock %}
{% block content %}
  <div class="card" style="max-width: 420px; margin: 40px auto;">
    <h1>Entrar</h1>

    {# form é enviado pela view de login do Django; form.errors existe quando a senha está errada #}
    {% if form.errors %}
      <div class="message error">Usuário ou senha incorretos. Tente novamente.</div>
    {% endif %}

    <form method="post">
      {% csrf_token %}
      {# Desenha os campos usuário e senha, um por parágrafo #}
      {{ form.as_p }}
      {# Página que a pessoa tentava abrir antes do login; o Django volta para ela depois #}
      <input type="hidden" name="next" value="{{ next }}">
      <button class="btn btn-primary" type="submit">Entrar</button>
    </form>

    {# Links para recuperar a senha e para criar uma conta nova #}
    <div class="actions">
      <a href="{% url 'password_reset' %}">Esqueci minha senha</a>
      <span class="spacer"></span>
      <a class="btn" href="{% url 'catalog:signup' %}">Criar conta</a>
    </div>
  </div>
{% endblock %}
```

**4.3) As quatro páginas da recuperação de senha**

A recuperação de senha **já funciona** desde a Aula 2, porque incluímos `django.contrib.auth.urls`. Falta só dar às páginas o visual do nosso sistema. O fluxo tem quatro etapas, e cada uma usa um template com nome fixo dentro de `registration/`:

```
1. password_reset_form.html      "Digite seu e-mail"
          │ (o Django envia um e-mail com um link secreto de uso único)
          ▼
2. password_reset_done.html      "Verifique seu e-mail"
          │ (a pessoa clica no link do e-mail)
          ▼
3. password_reset_confirm.html   "Digite a nova senha"
          │
          ▼
4. password_reset_complete.html  "Senha alterada"
```

**Arquivo:** `templates/registration/password_reset_form.html` · **Ação:** criar

```html
{% extends "base.html" %}
{# Etapa 1 da recuperação de senha: a pessoa informa o e-mail #}
{% block title %}Recuperar senha · Biblioteca{% endblock %}
{% block content %}
  <div class="card" style="max-width: 480px; margin: 40px auto;">
    <h1>Recuperar senha</h1>
    <p class="muted">Informe o e-mail da sua conta. Enviaremos um link para criar uma nova senha.</p>
    <form method="post">
      {% csrf_token %}
      {# O formulário (um campo de e-mail) vem pronto da view do Django #}
      {{ form.as_p }}
      <button class="btn btn-primary" type="submit">Enviar link</button>
    </form>
  </div>
{% endblock %}
```

**Arquivo:** `templates/registration/password_reset_done.html` · **Ação:** criar

```html
{% extends "base.html" %}
{# Etapa 2: aviso de que o e-mail foi enviado #}
{# Por segurança, a página não diz se o e-mail existe ou não no sistema #}
{% block title %}Verifique seu e-mail · Biblioteca{% endblock %}
{% block content %}
  <div class="card" style="max-width: 480px; margin: 40px auto;">
    <h1>Verifique seu e-mail</h1>
    <p>Se existir uma conta com esse e-mail, você vai receber um link para criar uma nova senha.</p>
    <p class="muted">Em desenvolvimento, o e-mail aparece no terminal onde o servidor está rodando.</p>
  </div>
{% endblock %}
```

**Arquivo:** `templates/registration/password_reset_confirm.html` · **Ação:** criar

```html
{% extends "base.html" %}
{# Etapa 3: a pessoa abriu o link do e-mail e escolhe a nova senha #}
{% block title %}Nova senha · Biblioteca{% endblock %}
{% block content %}
  <div class="card" style="max-width: 480px; margin: 40px auto;">
    {# validlink vem do Django: é falso se o link já foi usado, expirou ou foi alterado #}
    {% if validlink %}
      <h1>Crie uma nova senha</h1>
      <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button class="btn btn-primary" type="submit">Salvar nova senha</button>
      </form>
    {% else %}
      <h1>Link inválido</h1>
      <p>Este link já foi usado ou expirou. <a href="{% url 'password_reset' %}">Peça um novo</a>.</p>
    {% endif %}
  </div>
{% endblock %}
```

**Arquivo:** `templates/registration/password_reset_complete.html` · **Ação:** criar

```html
{% extends "base.html" %}
{# Etapa 4: senha trocada com sucesso #}
{% block title %}Senha alterada · Biblioteca{% endblock %}
{% block content %}
  <div class="card" style="max-width: 480px; margin: 40px auto;">
    <h1>Senha alterada</h1>
    <p>Pronto. Agora você já pode <a href="{% url 'login' %}">entrar com a nova senha</a>.</p>
  </div>
{% endblock %}
```

A página da etapa 2 nunca diz se o e-mail existe. Se dissesse, qualquer pessoa poderia descobrir quem tem conta na biblioteca testando endereços.

---

## Parte 3 — Página do livro e avaliações

### Passo 5 — Um método novo no `Book`

**Arquivo:** `catalog/models.py` · **Ação:** acrescentar um método à classe `Book`

Logo abaixo da `@property copies_available`, **dentro** da classe `Book` (com a mesma indentação), acrescente:

```python
    def was_borrowed_by(self, user):
        """Esta pessoa já pegou este livro emprestado alguma vez?"""
        # exists() só pergunta ao banco se há algum registro, sem trazer os dados
        return self.loans.filter(user=user).exists()
```

Mais uma regra de negócio no model. Ela será usada na view e no template.

### Passo 6 — O model `Review`

**Arquivo:** `catalog/models.py` · **Ação:** adicionar no final do arquivo

```python
class Review(models.Model):
    """Nota (1 a 5 estrelas) e comentário de um leitor sobre um livro."""

    # Lista de pares (valor guardado no banco, texto exibido): [(1, "★"), (2, "★★"), ...]
    RATING_CHOICES = [(n, "★" * n) for n in range(1, 6)]

    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="reviews", verbose_name="Livro"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Usuário",
    )
    # choices limita os valores aceitos e cria o método get_rating_display()
    rating = models.PositiveSmallIntegerField("Nota", choices=RATING_CHOICES)
    comment = models.TextField("Comentário", blank=True)  # opcional
    created_at = models.DateTimeField("Criada em", auto_now_add=True)  # preenchido só na criação
    updated_at = models.DateTimeField("Atualizada em", auto_now=True)  # atualizado a cada save()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        constraints = [
            # Regra garantida pelo próprio banco: 1 avaliação por pessoa por livro
            models.UniqueConstraint(fields=["book", "user"], name="uma_avaliacao_por_leitor"),
        ]

    def __str__(self):
        return f"{self.user} deu {self.rating} ★ para “{self.book.title}”"
```

#### Entendendo o código

- **`RATING_CHOICES`** é criado com uma *list comprehension*: `[(1, "★"), (2, "★★"), ..., (5, "★★★★★")]`. Cada par é (valor guardado no banco, texto exibido). Com `choices`, só esses valores são aceitos, e o Django cria de brinde o método `review.get_rating_display()`, que devolve as estrelas.
- **`auto_now_add`** preenche a data só na criação; **`auto_now`** atualiza a cada `save()`. É assim que sabemos quando a avaliação foi editada.
- **`UniqueConstraint(fields=["book", "user"])`**: a **combinação** livro + usuário não pode se repetir. A Maria pode avaliar vários livros, e vários leitores podem avaliar o mesmo livro, mas a Maria não avalia o mesmo livro duas vezes.

Crie e aplique a migração:

```powershell
python manage.py makemigrations
python manage.py migrate
```

Registre o model no Admin.

**Arquivo:** `catalog/admin.py` · **Ação:** trocar o import e adicionar no final

Troque a linha de import dos models por:

```python
from .models import Book, Category, Loan, Review, SearchQuery  # o ponto significa "deste mesmo app"
```

E acrescente no final do arquivo:

```python
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("book__title", "user__username", "comment")
```

### Passo 7 — As views do livro e das avaliações

**Arquivo:** `catalog/views.py` · **Ação:** adicionar logo abaixo da view `signup` (e ainda acima do comentário da área da equipe)

```python
# ---------- Detalhes do livro e avaliações ----------


@login_required
def book_detail(request, book_id):
    """Página de um livro: dados, média das notas e todas as avaliações."""
    # get_object_or_404 também aceita uma consulta; aqui ela já traz a categoria junto
    book = get_object_or_404(Book.objects.select_related("category"), pk=book_id)
    reviews = book.reviews.select_related("user")  # avaliações do livro, com o autor de cada uma
    # aggregate devolve um dicionário, ex.: {"average": 4.5, "total": 2}
    stats = reviews.aggregate(average=Avg("rating"), total=Count("id"))

    context = {
        "book": book,
        "reviews": reviews,
        "stats": stats,
        # first() devolve a avaliação da pessoa ou None, sem dar erro
        "user_review": reviews.filter(user=request.user).first(),
        "can_review": book.was_borrowed_by(request.user),
    }
    return render(request, "catalog/book_detail.html", context)


@login_required
def review_book(request, book_id):
    """Cria OU edita a avaliação do usuário para um livro."""
    book = get_object_or_404(Book, pk=book_id)

    # Regra: só avalia quem já pegou o livro emprestado (vale para GET e para POST)
    if not book.was_borrowed_by(request.user):
        messages.error(request, "Só quem já pegou este livro emprestado pode avaliá-lo.")
        return redirect("catalog:book_detail", book_id=book.id)

    # Se a pessoa já avaliou, editamos a avaliação existente; se não, review fica None e criamos uma nova
    review = Review.objects.filter(book=book, user=request.user).first()

    if request.method == "POST":
        # instance=review: com uma avaliação existente o save() atualiza; com None, cria
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)  # monta o objeto sem gravar: faltam livro e usuário
            review.book = book
            review.user = request.user
            review.save()  # agora sim grava no banco
            messages.success(request, "Avaliação salva. Obrigado pela opinião!")
            return redirect("catalog:book_detail", book_id=book.id)
    else:
        # GET: formulário vazio ou preenchido com a avaliação atual
        form = ReviewForm(instance=review)

    return render(request, "catalog/review_form.html", {"form": form, "book": book, "editing": review is not None})


@login_required
def delete_review(request, review_id):
    """GET mostra a confirmação; POST apaga. Só o autor pode apagar a própria avaliação."""
    # user=request.user: a avaliação de outra pessoa "não existe" para quem pede (404)
    review = get_object_or_404(Review, pk=review_id, user=request.user)

    if request.method == "POST":
        book_id = review.book_id  # guardamos o id antes de apagar, para saber para onde voltar
        review.delete()
        messages.success(request, "Avaliação removida.")
        return redirect("catalog:book_detail", book_id=book_id)

    # GET: mostra a página "Tem certeza?"
    return render(request, "catalog/review_confirm_delete.html", {"review": review})
```

#### Entendendo o código

**Criar e editar na mesma view.** O segredo está no parâmetro `instance`:

| `review` | `ReviewForm(..., instance=review)` | Resultado do `save()` |
|---|---|---|
| `None` (ainda não avaliou) | formulário vazio | cria uma avaliação nova |
| uma `Review` existente | formulário preenchido com a nota e o comentário atuais | atualiza essa avaliação |

**`form.save(commit=False)`** monta o objeto `Review` com os dados do formulário **sem gravar**. Isso nos dá a chance de preencher o que não veio do formulário (livro e usuário) antes do `review.save()` final. É um padrão muito comum em Django.

**A regra "só quem já pegou emprestado"** é conferida antes de tudo, tanto no GET quanto no POST. Esconder o botão no template não bastaria, porque alguém poderia enviar o POST diretamente.

**`delete_review` em duas etapas.** O GET mostra "Tem certeza?" e o POST apaga. Apagar direto por um link seria perigoso: um clique acidental, ou um navegador pré-carregando o link, apagaria a avaliação. O filtro `user=request.user` garante que só a própria avaliação pode ser apagada.

### Passo 8 — URLs

**Arquivo:** `catalog/urls.py` · **Ação:** substituir todo o conteúdo

```python
from django.urls import path

from . import views

# Namespace do app: nos templates escrevemos {% url 'catalog:book_list' %}
app_name = "catalog"

urlpatterns = [
    # Página inicial: lista de livros
    path("", views.book_list, name="book_list"),
    path("busca-avancada/", views.advanced_search, name="advanced_search"),
    path("historico/", views.search_history, name="search_history"),
    # <str:file_format> captura um texto: /exportar/csv/ -> file_format="csv"
    path("exportar/<str:file_format>/", views.export_books, name="export_books"),
    # Endereço usado pelo JavaScript do autocompletar
    path("api/sugestoes/", views.book_suggestions, name="book_suggestions"),
    # Cadastro de novos leitores
    path("cadastro/", views.signup, name="signup"),
    # Página de um livro e as avaliações
    path("livros/<int:book_id>/", views.book_detail, name="book_detail"),
    path("livros/<int:book_id>/avaliar/", views.review_book, name="review_book"),
    path("avaliacoes/<int:review_id>/excluir/", views.delete_review, name="delete_review"),
    # <int:book_id> captura um número da URL e entrega para a view como book_id
    path("livros/<int:book_id>/emprestar/", views.borrow_book, name="borrow_book"),
    path("emprestimos/", views.my_loans, name="my_loans"),
    path("emprestimos/<int:loan_id>/devolver/", views.return_book, name="return_book"),
    # Área da equipe (prefixo "equipe/" para não colidir com o "admin/" do Django)
    path("equipe/atrasados/", views.overdue_loans, name="overdue_loans"),
    path("equipe/livros/<int:book_id>/leitores/", views.book_borrowers, name="book_borrowers"),
    path("equipe/emprestimos/<int:loan_id>/devolver/", views.staff_mark_returned, name="staff_mark_returned"),
]
```

### Passo 9 — Templates do livro e das avaliações

**9.1) A página do livro**

**Arquivo:** `templates/catalog/book_detail.html` · **Ação:** criar

```html
{% extends "base.html" %}
{% block title %}{{ book.title }} · Biblioteca{% endblock %}
{% block content %}
  <p><a href="{% url 'catalog:book_list' %}">« Voltar ao acervo</a></p>

  {# Dados do livro: capa à esquerda, informações à direita #}
  <div class="card" style="display: flex; gap: 20px; flex-wrap: wrap;">
    {% if book.image %}
      <img src="{{ book.image.url }}" alt="Capa de {{ book.title }}" style="width: 160px; border-radius: 6px;">
    {% else %}
      <div class="cover" style="width: 160px; height: 240px;">sem capa</div>
    {% endif %}

    <div style="flex: 1; min-width: 240px;">
      <h1 style="margin-top: 0;">{{ book.title }}</h1>
      <p><strong>{{ book.author }}</strong></p>
      <p class="muted">
        {{ book.category.name|default:"Sem categoria" }}
        {% if book.edition_year %} · {{ book.edition_year }}{% endif %}
        {% if book.language %} · {{ book.language }}{% endif %}
        {% if book.publisher %} · {{ book.publisher }}{% endif %}
        · ISBN {{ book.isbn }}
      </p>

      {# stats vem do aggregate da view: {"average": ..., "total": ...} #}
      {% if stats.total %}
        <p style="font-size: 1.3rem;">
          {# floatformat:1 arredonda para uma casa decimal; pluralize escolhe singular ou plural #}
          ★ {{ stats.average|floatformat:1 }} <span class="muted">({{ stats.total }} avalia{{ stats.total|pluralize:"ção,ções" }})</span>
        </p>
      {% else %}
        <p class="muted">Ainda sem avaliações.</p>
      {% endif %}

      <p>{{ book.copies_available }} de {{ book.copies_total }} cópia(s) disponível(is).</p>

      <div class="actions">
        {% if book.copies_available > 0 %}
          <form class="inline" method="post" action="{% url 'catalog:borrow_book' book.id %}">
            {% csrf_token %}
            <button class="btn btn-primary" type="submit">Emprestar</button>
          </form>
        {% endif %}
        {# can_review: a pessoa já pegou este livro emprestado alguma vez #}
        {% if can_review %}
          <a class="btn" href="{% url 'catalog:review_book' book.id %}">
            {% if user_review %}Editar minha avaliação{% else %}Avaliar este livro{% endif %}
          </a>
        {% endif %}
      </div>
    </div>
  </div>

  {# Avaliações dos leitores #}
  <h2>Avaliações</h2>
  {% for review in reviews %}
    <div class="card">
      {# get_rating_display mostra o texto do choices (as estrelas) em vez do número #}
      <strong>{{ review.get_rating_display }}</strong>
      <span class="muted">— {{ review.user.username }}, {{ review.created_at|date:"d/m/Y" }}</span>
      {# Só o autor vê o link de excluir (a proteção de verdade está na view) #}
      {% if review.user == user %}
        <a href="{% url 'catalog:delete_review' review.id %}" class="danger" style="float: right;">excluir</a>
      {% endif %}
      {% if review.comment %}
        {# linebreaksbr mantém as quebras de linha que a pessoa digitou #}
        <p>{{ review.comment|linebreaksbr }}</p>
      {% endif %}
    </div>
  {% empty %}
    {# empty aparece quando a lista do for está vazia #}
    <p class="muted">
      Ninguém avaliou este livro ainda.
      {% if not can_review %}Para avaliar, pegue-o emprestado primeiro.{% endif %}
    </p>
  {% endfor %}
{% endblock %}
```

Filtros novos nesta página:

| Filtro | O que faz | Exemplo |
|---|---|---|
| `\|floatformat:1` | arredonda para uma casa decimal (com vírgula em pt-br) | `4.5` → `4,5` |
| `\|pluralize:"ção,ções"` | escolhe singular ou plural conforme o número | `1 avaliação`, `2 avaliações` |
| `\|linebreaksbr` | mantém as quebras de linha do comentário | |

Nos templates, métodos são chamados **sem parênteses**: `review.get_rating_display`.

**9.2) Formulário de avaliação**

**Arquivo:** `templates/catalog/review_form.html` · **Ação:** criar

```html
{% extends "base.html" %}
{% block title %}Avaliar · Biblioteca{% endblock %}
{% block content %}
  <div class="card" style="max-width: 560px;">
    {# editing vem da view: verdadeiro quando a pessoa já tinha avaliado este livro #}
    <h1>{% if editing %}Editar avaliação{% else %}Avaliar{% endif %}: {{ book.title }}</h1>
    <form method="post">
      {% csrf_token %}
      {# Desenha a nota (botões de rádio) e o comentário, com as mensagens de erro #}
      {{ form.as_p }}
      <div class="actions">
        <button class="btn btn-primary" type="submit">Salvar</button>
        <a class="btn" href="{% url 'catalog:book_detail' book.id %}">Cancelar</a>
      </div>
    </form>
  </div>
{% endblock %}
```

**9.3) Confirmação de exclusão**

**Arquivo:** `templates/catalog/review_confirm_delete.html` · **Ação:** criar

```html
{% extends "base.html" %}
{% block title %}Excluir avaliação · Biblioteca{% endblock %}
{% block content %}
  <div class="card" style="max-width: 560px;">
    <h1>Excluir avaliação?</h1>
    <p>Você deu <strong>{{ review.get_rating_display }}</strong> para “{{ review.book.title }}”. Esta ação não pode ser desfeita.</p>
    {# Apagar altera dados: a confirmação é um formulário POST #}
    <form method="post">
      {% csrf_token %}
      <div class="actions">
        <button class="btn btn-primary" type="submit" style="background: var(--danger); border-color: var(--danger);">Sim, excluir</button>
        <a class="btn" href="{% url 'catalog:book_detail' review.book.id %}">Cancelar</a>
      </div>
    </form>
  </div>
{% endblock %}
```

**9.4) Links para a página do livro**

Nas listas, o título do livro passa a ser um link.

**Arquivo:** `templates/catalog/book_list.html` · **Ação:** alterar uma linha

A célula do título começa com `<td>{{ book.title }}{% if book.language`. Troque esse início por:

```html
<td><a href="{% url 'catalog:book_detail' book.id %}">{{ book.title }}</a>{% if book.language
```

O resto da linha continua igual. A linha completa fica assim:

```html
              <td><a href="{% url 'catalog:book_detail' book.id %}">{{ book.title }}</a>{% if book.language and book.language != "Português" %} <span class="muted">({{ book.language }})</span>{% endif %}</td>
```

**Arquivo:** `templates/catalog/my_loans.html` · **Ação:** alterar uma linha

Troque `<td>{{ loan.book.title }}</td>` por:

```html
<td><a href="{% url 'catalog:book_detail' loan.book.id %}">{{ loan.book.title }}</a></td>
```

---

## Parte 4 — Testando

### Passo 10 — No navegador

Rode `python manage.py runserver` e siga o roteiro:

1. Saia do sistema e, na tela de login, clique em **Criar conta**. Tente cadastrar com senhas diferentes, com uma senha fraca como `123` e com o e-mail de alguém que já tem conta. Cada caso mostra um erro.
2. Faça um cadastro válido. Você já entra logado, com a mensagem de boas-vindas.
3. Clique no título de um livro: abre a página de detalhes, com "Ainda sem avaliações".
4. Empreste o livro e volte à página dele: apareceu o botão **Avaliar este livro**.
5. Avalie com 4 estrelas. Depois clique em **Editar minha avaliação** e mude para 5. Continua existindo uma avaliação só.
6. Clique em **excluir** e depois em **Cancelar**. Clique em **excluir** de novo e confirme.
7. **Recuperação de senha:** saia do sistema, clique em **Esqueci minha senha** e informe o e-mail da conta criada. No terminal do `runserver` aparece o e-mail com um link `http://127.0.0.1:8000/contas/reset/...`. Abra o link, defina uma nova senha e entre com ela. Abra o mesmo link de novo: aparece "Link inválido", porque ele é de uso único.

### Passo 11 — Testes automatizados

**Arquivo:** `catalog/tests.py` · **Ação:** três alterações

**11.1)** Logo abaixo da linha `from django.contrib.auth.models import User`, acrescente:

```python
from django.core import mail  # caixa de saída de e-mails usada nos testes
```

**11.2)** Troque a linha de import dos models por:

```python
from .models import Book, Category, Loan, Review, SearchQuery
```

**11.3)** Acrescente no final do arquivo:

```python
class AccountTests(TestCase):
    """Testes da Aula 5: cadastro e recuperação de senha."""

    def test_cadastro_cria_usuario_e_ja_entra(self):
        # Os nomes password1 e password2 são os campos de senha do UserCreationForm
        response = self.client.post(reverse("catalog:signup"), {
            "username": "ana",
            "email": "ana@exemplo.com",
            "password1": "uma-senha-bem-forte-42",
            "password2": "uma-senha-bem-forte-42",
        })
        self.assertRedirects(response, reverse("catalog:book_list"))
        self.assertTrue(User.objects.filter(username="ana").exists())
        # Já está logada: a lista de livros abre direto (200) em vez de mandar para o login
        self.assertEqual(self.client.get(reverse("catalog:book_list")).status_code, 200)

    def test_cadastro_recusa_email_repetido(self):
        User.objects.create_user("ana", email="ana@exemplo.com", password="x")
        response = self.client.post(reverse("catalog:signup"), {
            "username": "ana2",
            "email": "ANA@exemplo.com",  # mesmo e-mail, com letras maiúsculas
            "password1": "uma-senha-bem-forte-42",
            "password2": "uma-senha-bem-forte-42",
        })
        self.assertContains(response, "Já existe uma conta com este e-mail.")

    def test_recuperar_senha_envia_email(self):
        User.objects.create_user("ana", email="ana@exemplo.com", password="x")
        self.client.post(reverse("password_reset"), {"email": "ana@exemplo.com"})
        # Nos testes o Django não envia e-mails de verdade: eles ficam guardados em mail.outbox
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("ana@exemplo.com", mail.outbox[0].to)


class ReviewTests(TestCase):
    """Testes da Aula 5: página do livro e avaliações."""

    def setUp(self):
        self.maria = User.objects.create_user("maria", password="senha-forte-123")
        self.joao = User.objects.create_user("joao", password="senha-forte-123")
        self.book = Book.objects.create(title="Dom Casmurro", author="Machado de Assis", isbn="9788535910663")
        self.url = reverse("catalog:review_book", args=[self.book.id])

    def test_so_avalia_quem_ja_pegou_emprestado(self):
        self.client.force_login(self.maria)  # Maria nunca pegou o livro
        self.client.post(self.url, {"rating": 5, "comment": "Ótimo"})
        self.assertEqual(Review.objects.count(), 0)

    def test_avaliar_e_depois_editar_mantem_uma_avaliacao(self):
        make_loan(self.book, self.maria)
        self.client.force_login(self.maria)
        self.client.post(self.url, {"rating": 3, "comment": "Bom"})
        self.client.post(self.url, {"rating": 5, "comment": "Mudei de ideia: ótimo!"})
        review = Review.objects.get()  # get() sem filtro: falha se houver mais de uma avaliação
        self.assertEqual(review.rating, 5)

    def test_nota_fora_de_1_a_5_e_recusada(self):
        make_loan(self.book, self.maria)
        self.client.force_login(self.maria)
        response = self.client.post(self.url, {"rating": 9})
        self.assertEqual(response.status_code, 200)  # a página volta mostrando o erro
        self.assertEqual(Review.objects.count(), 0)

    def test_pagina_do_livro_mostra_a_media(self):
        Review.objects.create(book=self.book, user=self.maria, rating=5)
        Review.objects.create(book=self.book, user=self.joao, rating=4)
        self.client.force_login(self.maria)
        response = self.client.get(reverse("catalog:book_detail", args=[self.book.id]))
        self.assertContains(response, "4,5")  # média de 5 e 4, com vírgula (pt-br)
        self.assertContains(response, "2 avaliações")

    def test_nao_apaga_avaliacao_de_outra_pessoa(self):
        review = Review.objects.create(book=self.book, user=self.joao, rating=4)
        self.client.force_login(self.maria)
        response = self.client.post(reverse("catalog:delete_review", args=[review.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Review.objects.filter(pk=review.pk).exists())  # continua lá
```

```powershell
python manage.py test
```

O resultado esperado é `Ran 30 tests ... OK`. Os testes podem ficar alguns segundos mais lentos: criar usuários com senha é propositalmente demorado, porque o Django usa um algoritmo de senha feito para dificultar ataques.

---

## Checkpoint

- [ ] A tela de login tem os links **Criar conta** e **Esqueci minha senha**.
- [ ] O cadastro valida as senhas e recusa e-mail repetido; depois do cadastro a pessoa já entra logada.
- [ ] O fluxo completo de recuperação de senha funciona, com o e-mail aparecendo no terminal.
- [ ] Os títulos no acervo e em "Meus empréstimos" levam à página do livro.
- [ ] Só quem já pegou o livro vê o botão **Avaliar**, e editar não duplica a avaliação.
- [ ] A página do livro mostra a média (ex.: `★ 4,5 (2 avaliações)`).
- [ ] O Admin tem o menu **Avaliações**.
- [ ] `python manage.py test` mostra 30 testes OK.

---

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ImportError: cannot import name 'Review'` | `forms.py` criado antes do model | Faça o Passo 6 e rode `makemigrations` |
| `NoReverseMatch: 'signup'` no login | A rota de cadastro ainda não existe | Confira o Passo 8 |
| O e-mail de recuperação não aparece no terminal | E-mail digitado não pertence a nenhum usuário, ou falta o `EMAIL_BACKEND` | Confira o e-mail do usuário no Admin e o Passo 1 |
| Páginas de recuperação com o visual do Admin | Templates com nome errado ou fora de `templates/registration/` | Os nomes precisam ser exatamente os do Passo 4.3 |
| `IntegrityError ... uma_avaliacao_por_leitor` | Segunda avaliação criada sem passar pela view | É o banco protegendo a regra; a view usa `instance=` para editar |
| `NOT NULL constraint failed: catalog_review.book_id` | `form.save()` sem `commit=False` | Use `commit=False`, preencha `book` e `user` e depois `review.save()` |
| A média aparece como `4.5` | `LANGUAGE_CODE` diferente de `'pt-br'` | Confira o `settings.py` (Aula 1) |

---

## Resumo

Criamos o cadastro de leitores, a recuperação de senha, a página de cada livro e as avaliações com estrelas, comentário, edição e exclusão.

O que ficou de ideia principal:

- **Formulários do Django**: herdamos do `UserCreationForm` e criamos um `ModelForm`, sempre com o roteiro `POST → is_valid → save → redirect`.
- **Validação personalizada** com `clean_<campo>` e `ValidationError`.
- **Recuperação de senha pronta** no Django: só escrevemos os templates, e o e-mail aparece no console.
- **Uma view para criar e editar**, com `instance=` e `save(commit=False)` para preencher os campos que não vêm do formulário.
- **Regras no banco**: "uma avaliação por pessoa" com `UniqueConstraint` e notas limitadas com `choices`.
- **Média e total** calculados com `aggregate` (`Avg`, `Count`) e formatados com `floatformat`, `pluralize` e `linebreaksbr`.

---

## Exercícios

1. Mostre no acervo a média de estrelas de cada livro, acrescentando `average=Avg("reviews__rating")` ao `annotate` da `filter_books`. Depois rode os testes: algum número mudou? Pesquise "Django annotate multiple aggregations" para entender o que aconteceu.
2. Na página do livro, mostre "(editada)" ao lado das avaliações em que `updated_at` é diferente de `created_at`.
3. Acrescente o campo "Primeiro nome" (`first_name`) ao `SignUpForm`.
4. (Desafio) Crie a página "Minha conta", onde a pessoa troca o próprio e-mail. Use um `ModelForm` do `User` com `fields = ["email"]` e reaproveite a validação de e-mail único. Cuidado: ao editar, o e-mail da própria pessoa já existe no banco.

---

## Perguntas para revisar

<details>
<summary>1. Qual a diferença entre <code>forms.Form</code> e <code>forms.ModelForm</code>?</summary>

O `Form` tem os campos definidos à mão e não grava em lugar nenhum. O `ModelForm` gera os campos a partir de um model e grava no banco com `form.save()`.
</details>

<details>
<summary>2. O que acontece quando <code>form.is_valid()</code> é falso?</summary>

A view não grava nada e mostra a página de novo com o mesmo `form`, que agora tem as mensagens de erro de cada campo e os valores digitados. A pessoa corrige só o que estava errado.
</details>

<details>
<summary>3. Para que serve o <code>save(commit=False)</code>?</summary>

Para montar o objeto a partir do formulário sem gravar ainda. Assim podemos preencher campos que não fazem parte do formulário (livro e usuário, que não podem vir do navegador por segurança) e só depois chamar `save()`.
</details>

<details>
<summary>4. Se a view já evita avaliações duplicadas, por que usar a <code>UniqueConstraint</code>?</summary>

Ela é a última linha de defesa. Qualquer outro caminho que crie avaliações (Admin, shell, um script, uma view nova) também é barrado pelo banco.
</details>

<details>
<summary>5. Qual a diferença entre <code>annotate</code> e <code>aggregate</code>?</summary>

O `annotate` acrescenta um valor a cada linha e devolve um QuerySet. O `aggregate` calcula um resultado para o conjunto todo e devolve um dicionário.
</details>

<details>
<summary>6. Por que a página "Verifique seu e-mail" não diz se o e-mail está cadastrado?</summary>

Para não revelar quem tem conta no sistema. Se ela dissesse "e-mail não encontrado", qualquer pessoa poderia testar endereços e descobrir quem usa a biblioteca.
</details>

---

Próxima aula: [Aula 6 — Relatórios, banco de dados e revisão](Aula_06_Relatorios_Banco_de_Dados_e_Revisao.md).
