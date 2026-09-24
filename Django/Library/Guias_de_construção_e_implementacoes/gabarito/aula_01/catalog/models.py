from django.conf import settings  # dá acesso às configurações do projeto (settings.py)
from django.db import models  # classes base para criar models e campos
from django.utils import timezone  # datas e horas respeitando o TIME_ZONE do projeto


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
