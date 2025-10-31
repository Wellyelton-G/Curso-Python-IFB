"""Modelos principais da aplicação de catálogo.

Este arquivo define duas entidades:
- Book: representa um livro no acervo (com título, autor, ISBN e número de cópias).
- Loan: representa um empréstimo de um livro para um usuário.

Os comentários visa apresentar de forma didática o que cada parte do código faz, facilitando o entendimento.
"""

from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Cast
from django.utils import timezone


class Book(models.Model):
	"""Livro do acervo.

	- title/author: textos simples.
	- isbn: código de 13 caracteres e único (não deixa cadastrar repetido).
	- copies_total: quantas cópias existem deste título.
	- image: campo para upload da capa do livro (opcional).
	- created_at: preenchido automaticamente quando o registro é criado.
	"""

	title = models.CharField(max_length=255)
	author = models.CharField(max_length=255)
	isbn = models.CharField(max_length=13, unique=True)
	copies_total = models.PositiveIntegerField(default=1)
	
	# ImageField: campo para upload de imagens (requer biblioteca Pillow)
	# - upload_to: subpasta dentro de MEDIA_ROOT onde as imagens serão salvas
	# - blank=True: permite deixar vazio no formulário do admin
	# - null=True: permite valor NULL no banco (livros sem capa ainda funcionam)
	# Acesso à imagem no template: {{ book.image.url }} retorna a URL completa
	image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
	
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["title"]

	def __str__(self) -> str:
		# Representação amigável no admin e no shell
		return f"{self.title} — {self.author}"

	@property
	def copies_available(self) -> int:
		"""Quantidade de cópias disponíveis agora.

		Contamos quantos empréstimos estão ativos (returned_at nulo) e
		subtraímos de copies_total. Nunca retornamos número negativo.
		"""
		active_loans = self.loans.filter(returned_at__isnull=True).count()
		return max(self.copies_total - active_loans, 0)


class Loan(models.Model):
	"""Empréstimo de um livro para um usuário.

	- book/user: relacionamentos com o livro e o usuário (ForeignKey).
		related_name permite acessar `book.loans` e `user.loans` de forma fácil.
	- borrowed_at: instante em que o empréstimo foi criado.
	- due_date: data limite de devolução (apenas data, sem hora).
	- returned_at: quando o livro foi devolvido (nulo se ainda está com o usuário).
	"""

	book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="loans")
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="loans")
	borrowed_at = models.DateTimeField(auto_now_add=True)
	due_date = models.DateField()
	returned_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ["-borrowed_at"]
		constraints = [
			# Regra de negócio no banco: a data de devolução (due_date)
			# não pode ser antes da DATA (parte de data) em que o empréstimo foi feito.
			# Usamos Cast para comparar date (due_date) com a parte de data do datetime borrowed_at.
			models.CheckConstraint(
				check=Q(due_date__gte=Cast(F("borrowed_at"), output_field=models.DateField())),
				name="loan_due_after_borrowed",
			),
		]

	def __str__(self) -> str:
		status = "devolvido" if self.returned_at else "emprestado"
		return f"{self.book.title} para {self.user} ({status})"

	@property
	def is_active(self) -> bool:
		"""Verdadeiro enquanto o livro não foi devolvido."""
		return self.returned_at is None

	@property
	def is_overdue(self) -> bool:
		"""Indica se está atrasado hoje.

		Considera o timezone configurado no projeto e compara a data de hoje
		(timezone.localdate) com due_date. Só faz sentido para empréstimos ativos.
		"""
		return self.is_active and timezone.localdate() > self.due_date

	def mark_returned(self):
		"""Marca a devolução registrando timestamp e salvando apenas esse campo.

		O update_fields=["returned_at"] é uma otimização: diz ao Django para
		atualizar somente essa coluna no banco de dados.
		"""
		if not self.returned_at:
			self.returned_at = timezone.now()
			self.save(update_fields=["returned_at"])
