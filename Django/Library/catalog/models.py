"""Modelos principais da aplicação de catálogo.

Este arquivo define duas entidades:
- Book: representa um livro no acervo (com título, autor, ISBN e número de cópias).
- Loan: representa um empréstimo de um livro para um usuário.

Os comentários visa apresentar de forma didática o que cada parte do código faz, facilitando o entendimento.
"""

# ATENÇÃO (localização PT-BR):
# Este módulo foi localizado para português do Brasil. Os rótulos exibidos no
# Django Admin foram traduzidos adicionando:
# - verbose_name nos campos dos models;
# - verbose_name e verbose_name_plural em Meta de cada model.
# Isso afeta apenas metadados mostrados no Admin (não muda a lógica).

from django.conf import settings
from django.db import models
from django.db.models import F, Q, Avg  # PT-BR: agregado para calcular média das notas
from django.db.models.functions import Cast
from django.core.validators import MinValueValidator, MaxValueValidator  # PT-BR: validadores 1–5 estrelas
from django.utils import timezone


class Category(models.Model):
	"""Categoria/Gênero do livro.

	Mantemos simples com um nome único e uma descrição opcional. Esta
	classe permite filtrar o acervo por gênero (ex.: Romance, Didático,
	Tecnologia). Também é usada na busca avançada.
	"""

	name = models.CharField(max_length=100, unique=True, verbose_name="Nome")  # PT-BR: rótulo exibido no Admin
	description = models.TextField(blank=True, verbose_name="Descrição")  # PT-BR: rótulo exibido no Admin

	class Meta:
		ordering = ["name"]
		verbose_name = "Categoria"  # PT-BR: nome do modelo no Admin
		verbose_name_plural = "Categorias"  # PT-BR: plural do modelo no Admin

	def __str__(self) -> str:  # pragma: no cover - representação no admin
		return self.name


class Book(models.Model):
	"""Livro do acervo.

	- title/author: textos simples.
	- isbn: código de 13 caracteres e único (não deixa cadastrar repetido).
	- copies_total: quantas cópias existem deste título.
	- image: campo para upload da capa do livro (opcional).
	- created_at: preenchido automaticamente quando o registro é criado.
	"""

	title = models.CharField(max_length=255, verbose_name="Título")  # PT-BR: rótulo exibido no Admin
	author = models.CharField(max_length=255, verbose_name="Autor(a)")  # PT-BR: rótulo exibido no Admin
	isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")  # PT-BR: rótulo exibido no Admin
	copies_total = models.PositiveIntegerField(default=1, verbose_name="Cópias totais")  # PT-BR: rótulo exibido no Admin
	
	# ImageField: campo para upload de imagens (requer biblioteca Pillow)
	# - upload_to: subpasta dentro de MEDIA_ROOT onde as imagens serão salvas
	# - blank=True: permite deixar vazio no formulário do admin
	# - null=True: permite valor NULL no banco (livros sem capa ainda funcionam)
	# Acesso à imagem no template: {{ book.image.url }} retorna a URL completa
	image = models.ImageField(upload_to='book_covers/', blank=True, null=True, verbose_name="Capa")  # PT-BR: rótulo exibido no Admin

	# Campos extras para filtros avançados (todos opcionais)
	category = models.ForeignKey(
		Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="books", verbose_name="Categoria"  # PT-BR: rótulo exibido no Admin
	)
	language = models.CharField(max_length=50, blank=True, verbose_name="Idioma")  # PT-BR: rótulo exibido no Admin
	publisher = models.CharField(max_length=150, blank=True, verbose_name="Editora")  # PT-BR: rótulo exibido no Admin
	edition_year = models.IntegerField(null=True, blank=True, verbose_name="Ano de edição")  # PT-BR: rótulo exibido no Admin
	series = models.CharField(max_length=150, blank=True, verbose_name="Série")  # PT-BR: rótulo exibido no Admin
	subject = models.CharField(max_length=150, blank=True, verbose_name="Assunto")  # PT-BR: rótulo exibido no Admin
	material = models.CharField(max_length=100, blank=True, verbose_name="Material")  # PT-BR: rótulo exibido no Admin
	
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")  # PT-BR: rótulo exibido no Admin

	class Meta:
		ordering = ["title"]
		verbose_name = "Livro"  # PT-BR: nome do modelo no Admin
		verbose_name_plural = "Livros"  # PT-BR: plural do modelo no Admin

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

	@property
	def average_rating(self):
		"""Média das avaliações (1–5). Retorna None se o livro ainda não foi avaliado."""
		aggr = self.reviews.aggregate(avg=Avg("rating"))
		return aggr["avg"]  # PT-BR: média calculada no banco

	@property
	def reviews_count(self) -> int:
		"""Quantidade de avaliações recebidas."""
		return self.reviews.count()

	def user_can_review(self, user):
		"""Verifica se o usuário pode avaliar este livro.
		
		PT-BR: apenas usuários que pegaram este livro emprestado (histórico)
		podem deixar avaliações.
		"""
		if not user.is_authenticated:
			return False
		# PT-BR: verifica se existe algum empréstimo deste livro para este usuário
		return self.loans.filter(user=user).exists()

	def user_review(self, user):
		"""Retorna a avaliação do usuário para este livro, se existir.
		
		PT-BR: útil para exibir se o usuário já avaliou e permitir edição.
		"""
		if not user.is_authenticated:
			return None
		return self.reviews.filter(user=user).first()


class Loan(models.Model):
	"""Empréstimo de um livro para um usuário.

	- book/user: relacionamentos com o livro e o usuário (ForeignKey).
		related_name permite acessar `book.loans` e `user.loans` de forma fácil.
	- borrowed_at: instante em que o empréstimo foi criado.
	- due_date: data limite de devolução (apenas data, sem hora).
	- returned_at: quando o livro foi devolvido (nulo se ainda está com o usuário).
	"""

	book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="loans", verbose_name="Livro")  # PT-BR: rótulo exibido no Admin
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="loans", verbose_name="Usuário")  # PT-BR: rótulo exibido no Admin
	borrowed_at = models.DateTimeField(auto_now_add=True, verbose_name="Emprestado em")  # PT-BR: rótulo exibido no Admin
	due_date = models.DateField(verbose_name="Devolver até")  # PT-BR: rótulo exibido no Admin
	returned_at = models.DateTimeField(null=True, blank=True, verbose_name="Devolvido em")  # PT-BR: rótulo exibido no Admin

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
		verbose_name = "Empréstimo"  # PT-BR: nome do modelo no Admin
		verbose_name_plural = "Empréstimos"  # PT-BR: plural do modelo no Admin

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


class SearchQuery(models.Model):
	"""Histórico de buscas realizadas.

	Armazenamos tanto buscas de usuários autenticados quanto de sessões
	(anônimos), permitindo mostrar pesquisas recentes por usuário e
	coletar métricas. O campo `params` guarda os filtros aplicados para
	reproduzir a consulta depois.
	"""

	user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Usuário")  # PT-BR: rótulo exibido no Admin
	session_key = models.CharField(max_length=40, blank=True, verbose_name="Chave da sessão", help_text="Chave da sessão quando o usuário não está logado")  # PT-BR: rótulo/ajuda no Admin
	q = models.CharField(max_length=255, blank=True, verbose_name="Texto da busca")  # PT-BR: rótulo exibido no Admin
	params = models.JSONField(default=dict, blank=True, verbose_name="Parâmetros")  # PT-BR: rótulo exibido no Admin
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")  # PT-BR: rótulo exibido no Admin

	class Meta:
		ordering = ["-created_at"]
		verbose_name = "Consulta de busca"  # PT-BR: nome do modelo no Admin
		verbose_name_plural = "Consultas de busca"  # PT-BR: plural do modelo no Admin

	def __str__(self) -> str:  # pragma: no cover
		usuario = self.user or self.session_key or "anon"
		return f"{usuario}: {self.q} ({self.created_at:%d/%m %H:%M})"


class Review(models.Model):
	"""Avaliação e comentário de um livro por um usuário.

	PT-BR: usuários podem dar uma nota (estrelas) e comentar para ajudar outros leitores.
	"""

	book = models.ForeignKey(
		Book, on_delete=models.CASCADE, related_name="reviews", verbose_name="Livro"
	)  # PT-BR: vínculo com o livro avaliado
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews", verbose_name="Usuário"
	)  # PT-BR: quem avaliou
	rating = models.PositiveSmallIntegerField(
		"Nota",
		validators=[MinValueValidator(1), MaxValueValidator(5)],
		help_text="De 1 a 5 estrelas",
	)  # PT-BR: nota de 1–5
	comment = models.TextField("Comentário", blank=True)  # PT-BR: texto opcional
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

	class Meta:
		ordering = ["-created_at"]
		verbose_name = "Avaliação"  # PT-BR: nome do modelo no Admin
		verbose_name_plural = "Avaliações"  # PT-BR: plural no Admin
		constraints = [
			models.UniqueConstraint(
				fields=["book", "user"],
				name="unique_review_per_user_book",
			)  # PT-BR: impede avaliar o mesmo livro mais de uma vez por usuário
		]

	def __str__(self) -> str:  # pragma: no cover
		return f"{self.book.title} — {self.user} ({self.rating}★)"
