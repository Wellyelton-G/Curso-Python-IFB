"""Views (controladores) da aplicação de biblioteca.

Cada função abaixo recebe um `request` e retorna uma `HttpResponse`.
Os comentários explicam passo a passo o que cada view faz.
"""

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q, F
from django.core.paginator import Paginator
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Book, Loan


def _is_staff(user):
	"""Função auxiliar usada pelo decorator `user_passes_test`.

	Só permite acesso se o usuário estiver autenticado e for staff (is_staff).
	"""
	return user.is_authenticated and user.is_staff


@login_required
def book_list(request: HttpRequest) -> HttpResponse:
	"""Lista todos os livros e quantas cópias estão disponíveis.

	- annotate(active_loans=...): cria um campo calculado na consulta
	  para saber quantos empréstimos estão ativos por livro.
	- O template mostra o botão de emprestar quando há disponibilidade.
	- Melhorias de usabilidade adicionadas:
	  * Busca textual (título, autor ou ISBN) via parâmetro GET `q`.
	  * Filtro de disponibilidade (mostrar só livros que ainda têm cópias) com `disponivel=1`.
	  * Paginação (10 itens por página) com parâmetro `page`.
	"""

	# 1) Base queryset com contagem de empréstimos ativos
	qs = (
		Book.objects.all()
		.annotate(active_loans=Count("loans", filter=Q(loans__returned_at__isnull=True)))
		.order_by("title")
	)

	# 2) Busca (parâmetro GET ?q=...)
	q = request.GET.get("q", "").strip()
	if q:
		qs = qs.filter(
			Q(title__icontains=q)
			| Q(author__icontains=q)
			| Q(isbn__icontains=q)
		)

	# 3) Filtro de disponibilidade (?disponivel=1)
	disponivel_param = request.GET.get("disponivel")
	show_only_available = disponivel_param == "1"
	if show_only_available:
		# active_loans < copies_total
		qs = qs.filter(active_loans__lt=F("copies_total"))

	# 4) Paginação
	paginator = Paginator(qs, 10)  # 10 livros por página
	page_number = request.GET.get("page")
	page_obj = paginator.get_page(page_number)

	context = {
		"books": page_obj.object_list,
		"page_obj": page_obj,
		"q": q,
		"show_only_available": show_only_available,
	}
	return render(request, "catalog/book_list.html", context)


@login_required
def borrow_book(request: HttpRequest, book_id: int) -> HttpResponse:
	"""Realiza um empréstimo (deve ser chamado por POST).

	- Buscamos o livro; se não existir, 404.
	- Garantimos que a ação é POST (boas práticas REST para mudar estado).
	- Verificamos disponibilidade: se não houver cópias, mostramos mensagem.
	- Criamos o Loan com data de devolução padrão de 14 dias a partir de hoje.
	"""
	book = get_object_or_404(Book, id=book_id)
	# Bloqueia GET; somente POST pode criar empréstimo
	if request.method != "POST":
		raise Http404()

	# Conta quantos empréstimos do livro ainda estão ativos
	active_loans = Loan.objects.filter(book=book, returned_at__isnull=True).count()
	if active_loans >= book.copies_total:
		messages.error(request, "Não há cópias disponíveis para empréstimo.")
		return redirect("catalog:book_list")

	# Padrão: 14 dias para devolver
	due_date = timezone.localdate() + timedelta(days=14)
	Loan.objects.create(book=book, user=request.user, due_date=due_date)
	messages.success(request, f"Você emprestou '{book.title}'. Devolução até {due_date:%d/%m/%Y}.")
	return redirect("catalog:book_list")


@login_required
def return_book(request: HttpRequest, loan_id: int) -> HttpResponse:
	"""Registra a devolução do livro (POST)."""
	loan = get_object_or_404(Loan, id=loan_id, user=request.user)
	if request.method != "POST":
		raise Http404()
	if loan.returned_at:
		messages.info(request, "Este empréstimo já foi devolvido.")
	else:
		loan.mark_returned()
		messages.success(request, f"'{loan.book.title}' devolvido com sucesso.")
	return redirect("catalog:my_loans")


@login_required
def my_loans(request: HttpRequest) -> HttpResponse:
	"""Lista todos os empréstimos do usuário logado."""
	loans = Loan.objects.filter(user=request.user).select_related("book")
	return render(request, "catalog/my_loans.html", {"loans": loans})


@user_passes_test(_is_staff)
def admin_book_borrowers(request: HttpRequest, book_id: int) -> HttpResponse:
	"""Mostra quem está com o livro (empréstimos ativos)."""
	book = get_object_or_404(Book, id=book_id)
	active_loans = Loan.objects.filter(book=book, returned_at__isnull=True).select_related("user")
	return render(request, "catalog/admin_book_borrowers.html", {"book": book, "active_loans": active_loans})


@user_passes_test(_is_staff)
def admin_overdue_loans(request: HttpRequest) -> HttpResponse:
	"""Lista empréstimos atrasados (para staff)."""
	today = timezone.localdate()
	overdue = Loan.objects.filter(returned_at__isnull=True, due_date__lt=today).select_related("book", "user")
	return render(request, "catalog/admin_overdue.html", {"loans": overdue})


@user_passes_test(_is_staff)
def admin_mark_returned(request: HttpRequest, loan_id: int) -> HttpResponse:
	"""Ação de staff para marcar um empréstimo como devolvido (POST)."""
	loan = get_object_or_404(Loan, id=loan_id)
	if request.method != "POST":
		raise Http404()
	if not loan.returned_at:
		loan.mark_returned()
		messages.success(request, f"Empréstimo de '{loan.book.title}' marcado como devolvido.")
	return redirect("catalog:admin_overdue_loans")
