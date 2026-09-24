from urllib.parse import urlencode  # transforma um dicionário em texto de URL: {"q": "x"} -> "q=x"

from django.conf import settings  # dá acesso às configurações do projeto (settings.py)
from django.db import models  # classes base para criar models e campos
from django.utils import timezone  # datas e horas respeitando o TIME_ZONE do projeto


class Category(models.Model):
    """Gênero ou assunto de um livro (Romance, Tecnologia, História...)."""

    name = models.CharField("Nome", max_length=100, unique=True)  # não pode haver duas categorias iguais
    description = models.TextField("Descrição", blank=True)  # texto longo e opcional

    class Meta:
        ordering = ["name"]
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.name


class Book(models.Model):
    """Um título do acervo da biblioteca. Cada objeto vira uma linha da tabela catalog_book."""

    # Cada atributo abaixo vira uma coluna da tabela.
    # O primeiro texto de cada campo é o nome que aparece no Admin e nos formulários.
    title = models.CharField("Título", max_length=255)  # texto curto, até 255 caracteres
    author = models.CharField("Autor(a)", max_length=255)
    isbn = models.CharField("ISBN", max_length=13, unique=True)  # unique: o banco não aceita ISBN repetido
    copies_total = models.PositiveIntegerField("Cópias totais", default=1)  # inteiro >= 0; vale 1 se ninguém informar
    # Capa opcional: o arquivo é salvo em media/book_covers/ e o banco guarda só o caminho
    image = models.ImageField("Capa", upload_to="book_covers/", blank=True, null=True)

    # Campos da Aula 4. Todos são opcionais para não quebrar os livros que já estavam cadastrados.
    # SET_NULL: se a categoria for apagada, o livro continua existindo, só que sem categoria.
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="books",  # permite fazer categoria.books.all()
        verbose_name="Categoria",
    )
    language = models.CharField("Idioma", max_length=50, blank=True)
    publisher = models.CharField("Editora", max_length=150, blank=True)
    edition_year = models.PositiveSmallIntegerField("Ano de edição", null=True, blank=True)

    created_at = models.DateTimeField("Cadastrado em", auto_now_add=True)  # preenchido sozinho na criação

    class Meta:
        ordering = ["title"]  # ordem padrão das consultas: alfabética pelo título
        verbose_name = "Livro"  # nome no singular, usado pelo Admin
        verbose_name_plural = "Livros"  # nome no plural, usado pelo Admin

    def __str__(self):
        # Texto que representa o livro no Admin, no shell e nas listas
        return f"{self.title} — {self.author}"

    @property
    def copies_available(self):
        """Cópias que podem ser emprestadas agora (calculado, não é coluna do banco)."""
        # self.loans existe por causa do related_name="loans" definido no model Loan.
        # returned_at__isnull=True seleciona os empréstimos que ainda não foram devolvidos.
        active_loans = self.loans.filter(returned_at__isnull=True).count()
        # max(..., 0) garante que o resultado nunca seja negativo
        return max(self.copies_total - active_loans, 0)

    def was_borrowed_by(self, user):
        """Esta pessoa já pegou este livro emprestado alguma vez?"""
        # exists() só pergunta ao banco se há algum registro, sem trazer os dados
        return self.loans.filter(user=user).exists()


class Loan(models.Model):
    """O empréstimo de um livro para um usuário. Um empréstimo nunca é apagado: ele é o histórico."""

    # ForeignKey liga cada empréstimo a UM livro (no banco, fica guardado o id do livro).
    # on_delete=CASCADE: se o livro for apagado, os empréstimos dele também são.
    # related_name="loans": permite fazer book.loans.all() para ver os empréstimos de um livro.
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="loans", verbose_name="Livro"
    )
    # O usuário vem do sistema de contas do próprio Django (settings.AUTH_USER_MODEL)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loans",  # permite fazer user.loans.all()
        verbose_name="Usuário",
    )
    borrowed_at = models.DateTimeField("Emprestado em", auto_now_add=True)  # data e hora do empréstimo
    due_date = models.DateField("Devolver até")  # só a data do prazo, sem hora
    # Vazio (NULL) enquanto o livro não voltar; preenchido na devolução
    returned_at = models.DateTimeField("Devolvido em", null=True, blank=True)

    class Meta:
        ordering = ["-borrowed_at"]  # o sinal de menos inverte a ordem: mais recentes primeiro
        verbose_name = "Empréstimo"
        verbose_name_plural = "Empréstimos"

    def __str__(self):
        status = "devolvido" if self.returned_at else "emprestado"
        return f"{self.book.title} para {self.user} ({status})"

    @property
    def is_active(self):
        """Verdadeiro enquanto o livro não foi devolvido."""
        return self.returned_at is None

    @property
    def is_overdue(self):
        """Verdadeiro se o livro ainda não voltou e o prazo já passou."""
        # localdate() devolve a data de hoje no fuso horário configurado no projeto
        return self.is_active and timezone.localdate() > self.due_date

    def mark_returned(self):
        """Registra a devolução (só na primeira vez)."""
        if self.returned_at is None:
            self.returned_at = timezone.now()  # data e hora atuais
            # update_fields grava só esta coluna, sem regravar o registro inteiro
            self.save(update_fields=["returned_at"])


class SearchQuery(models.Model):
    """Uma busca feita por um usuário, guardada para o histórico."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="searches",  # permite fazer user.searches.all()
        verbose_name="Usuário",
    )
    q = models.CharField("Texto buscado", max_length=255, blank=True)
    # JSONField guarda um dicionário inteiro, ex.: {"q": "python", "categoria": "3"}.
    # default=dict (sem parênteses): cada busca nova recebe o seu próprio dicionário vazio.
    params = models.JSONField("Filtros usados", default=dict, blank=True)
    created_at = models.DateTimeField("Feita em", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # buscas mais recentes primeiro
        verbose_name = "Busca"
        verbose_name_plural = "Buscas"

    def __str__(self):
        return f"{self.user} buscou “{self.q or '(só filtros)'}”"

    def as_querystring(self):
        """Transforma os filtros guardados de volta em texto de URL ('q=...&categoria=...')."""
        return urlencode(self.params)


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
