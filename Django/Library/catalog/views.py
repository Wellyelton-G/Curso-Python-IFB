"""Views (controladores) da aplicação de biblioteca.

Cada função abaixo recebe um `request` e retorna uma `HttpResponse`.
Os comentários explicam passo a passo o que cada view faz.
"""

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, F, Q, Value
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Book, Loan, Category, SearchQuery


def _is_staff(user):
	"""Função auxiliar usada pelo decorator `user_passes_test`.

	Só permite acesso se o usuário estiver autenticado e for staff (is_staff).
	"""
	return user.is_authenticated and user.is_staff


@login_required
def book_list(request: HttpRequest) -> HttpResponse:
	"""Lista livros com busca, filtros, ordenação, paginação e exportação.

	Recursos suportados via parâmetros GET:
	- q: termo de busca (título, autor ou ISBN) – destaque no template.
	- disponivel=1: somente livros com cópias disponíveis.
	- categoria: id da categoria.
	- idioma: filtra campo language.
	- ano_min / ano_max: faixa de ano de edição.
	- ordenar: campo de ordenação (title|author|disponibilidade); sempre crescente.
	- mostrar: '20' (padrão) ou 'todos'.
	- export=csv: retorna CSV em vez de HTML.

	Também grava histórico da busca (SearchQuery) e provê endpoint de
	sugestões (se chamado como /?suggest=1&q=prefixo).
	"""

	# Queryset base com anotação de empréstimos ativos
	qs = Book.objects.all().annotate(
		active_loans=Count("loans", filter=Q(loans__returned_at__isnull=True))
	)

	# Termo de busca livre (campo único) OU campos individuais vindos da busca avançada
	q = request.GET.get("q", "").strip()
	title_param = request.GET.get("title", "").strip()
	author_param = request.GET.get("author", "").strip()
	isbn_param = request.GET.get("isbn", "").strip()
	if q:
		qs = qs.filter(
			Q(title__icontains=q) | Q(author__icontains=q) | Q(isbn__icontains=q)
		)
	else:
		# Se a busca avançada forneceu campos específicos, aplicamos cada filtro separadamente
		if title_param:
			qs = qs.filter(title__icontains=title_param)
		if author_param:
			qs = qs.filter(author__icontains=author_param)
		if isbn_param:
			qs = qs.filter(isbn__icontains=isbn_param)

	# Filtro disponibilidade
	show_only_available = request.GET.get("disponivel") == "1"
	if show_only_available:
		qs = qs.filter(active_loans__lt=F("copies_total"))

	# Filtro por categoria
	categoria_id = request.GET.get("categoria")
	if categoria_id and categoria_id.isdigit():
		qs = qs.filter(category_id=categoria_id)

	# Filtro por idioma
	idioma = request.GET.get("idioma", "").strip()
	if idioma:
		qs = qs.filter(language__iexact=idioma)

	# Faixa de ano
	ano_min = request.GET.get("ano_min")
	ano_max = request.GET.get("ano_max")
	if ano_min and ano_min.isdigit():
		qs = qs.filter(edition_year__gte=int(ano_min))
	if ano_max and ano_max.isdigit():
		qs = qs.filter(edition_year__lte=int(ano_max))

	# Ordenação dinâmica (sempre crescente)
	ordenar = request.GET.get("ordenar", "title")
	if ordenar == "author":
		qs = qs.order_by(Lower("author"), "title")
	elif ordenar == "disponibilidade":
		# ordenar por cópias disponíveis calculadas: (copies_total - active_loans)
		qs = qs.annotate(disponiveis=F("copies_total") - F("active_loans")).order_by("disponiveis", "title")
	else:  # default título
		qs = qs.order_by(Lower("title"))

	# Sugestões (autocomplete) modo simples: retorna JSON
	if request.GET.get("suggest") == "1" and q:
		limite = 8
		titulos = list(qs.values_list("title", flat=True)[:limite])
		autores = list(qs.values_list("author", flat=True)[:limite])
		isbns = list(qs.values_list("isbn", flat=True)[:limite])
		return JsonResponse({"titles": titulos, "authors": autores, "isbns": isbns})

	# Exportação CSV
	if request.GET.get("export") == "csv":
		import csv
		from io import StringIO
		buffer = StringIO()
		writer = csv.writer(buffer)
		writer.writerow(["Título", "Autor", "ISBN", "Disponíveis", "Categoria", "Idioma", "Ano"])
		for b in qs:
			writer.writerow([
				b.title,
				b.author,
				b.isbn,
				max(b.copies_total - b.active_loans, 0),
				b.category.name if b.category else "",
				b.language,
				b.edition_year or "",
			])
		response = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
		response["Content-Disposition"] = "attachment; filename=livros.csv"
		return response

	# Exportação Excel (XLSX) – requer openpyxl instalado
	if request.GET.get("export") == "xlsx":
		try:
			from openpyxl import Workbook
		except ImportError:
			return HttpResponse("Biblioteca 'openpyxl' não instalada. Execute 'pip install openpyxl'.", status=500)
		wb = Workbook()
		ws = wb.active
		ws.title = "Livros"
		ws.append(["Título", "Autor", "ISBN", "Disponíveis", "Categoria", "Idioma", "Ano"])
		for b in qs:
			ws.append([
				b.title,
				b.author,
				b.isbn,
				max(b.copies_total - b.active_loans, 0),
				b.category.name if b.category else "",
				b.language,
				b.edition_year or "",
			])
		from io import BytesIO
		buff = BytesIO()
		wb.save(buff)
		response = HttpResponse(buff.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
		response["Content-Disposition"] = "attachment; filename=livros.xlsx"
		return response

	# Paginação
	mostrar_param = request.GET.get("mostrar", "20")
	if mostrar_param == "todos":
		page_obj = None
		books = qs
	else:
		paginator = Paginator(qs, 20)
		page_number = request.GET.get("page")
		page_obj = paginator.get_page(page_number)
		books = page_obj.object_list

	# Salva histórico da busca (apenas se algum filtro ou termo usado)
	if any([q, title_param, author_param, isbn_param, show_only_available, categoria_id, idioma, ano_min, ano_max]):
		session_key = request.session.session_key or ""
		if not session_key:
			request.session.create()
			session_key = request.session.session_key
		try:
			SearchQuery.objects.create(
				user=request.user if request.user.is_authenticated else None,
				session_key=session_key,
				q=q,
				params={
					"disponivel": show_only_available,
					"categoria": categoria_id,
					"idioma": idioma,
					"ano_min": ano_min,
					"ano_max": ano_max,
					"ordenar": ordenar,
					"title": title_param,
					"author": author_param,
					"isbn": isbn_param,
				},
			)
		except Exception:  # pragma: no cover - não falha a página por erro no histórico
			pass

	context = {
		"books": books,
		"page_obj": page_obj,
		"q": q,
		"show_only_available": show_only_available,
		"mostrar": mostrar_param,
		"total_count": qs.count(),
		"ordenar": ordenar,
		"categorias": Category.objects.all(),
		"categoria_selecionada": categoria_id,
		"idioma": idioma,
		"ano_min": ano_min or "",
		"ano_max": ano_max or "",
		"title_param": title_param,
		"author_param": author_param,
		"isbn_param": isbn_param,
	}
	return render(request, "catalog/book_list.html", context)


@login_required
def search_history(request: HttpRequest) -> HttpResponse:
	"""Lista últimas buscas do usuário (ou sessão se anônimo) com opção de exportar.

	Parâmetro GET:
	- export=csv|xlsx para baixar histórico.
	"""
	if request.user.is_authenticated:
		qs = SearchQuery.objects.filter(user=request.user)[:100]
	else:
		session_key = request.session.session_key
		if not session_key:
			qs = []
		else:
			qs = SearchQuery.objects.filter(session_key=session_key)[:100]

	export_format = request.GET.get("export")
	if export_format == "csv":
		import csv
		from io import StringIO
		buf = StringIO()
		w = csv.writer(buf)
		w.writerow(["Data/Hora", "Termo livre (q)", "Parâmetros JSON"])
		for s in qs:
			w.writerow([s.created_at.strftime("%Y-%m-%d %H:%M"), s.q, s.params])
		resp = HttpResponse(buf.getvalue(), content_type="text/csv; charset=utf-8")
		resp["Content-Disposition"] = "attachment; filename=historico_buscas.csv"
		return resp
	elif export_format == "xlsx":
		try:
			from openpyxl import Workbook
		except ImportError:
			return HttpResponse("Biblioteca 'openpyxl' não instalada. Execute 'pip install openpyxl'.", status=500)
		wb = Workbook()
		ws = wb.active
		ws.title = "Buscas"
		ws.append(["Data/Hora", "Termo livre (q)", "Parâmetros JSON"])
		for s in qs:
			ws.append([s.created_at.strftime("%Y-%m-%d %H:%M"), s.q, str(s.params)])
		from io import BytesIO
		buff = BytesIO()
		wb.save(buff)
		resp = HttpResponse(buff.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
		resp["Content-Disposition"] = "attachment; filename=historico_buscas.xlsx"
		return resp

	return render(request, "catalog/search_history.html", {"searches": qs})


@login_required
def advanced_search(request: HttpRequest) -> HttpResponse:
	"""Página de busca avançada que oferece múltiplos campos dedicados.

	O formulário envia GET diretamente para a view `book_list` reutilizando
	a lógica existente de filtros. Campos individuais (title, author, isbn)
	são tratados em `book_list`.
	"""
	languages = (
		Book.objects.exclude(language="")
		.values_list("language", flat=True)
		.distinct()
		.order_by("language")
	)
	return render(
		request,
		"catalog/advanced_search.html",
		{"categorias": Category.objects.all(), "languages": languages},
	)


def signup(request: HttpRequest) -> HttpResponse:
	"""Cadastro (autoatendimento) de novos usuários.

	Usa o formulário padrão de criação de usuário do Django. Após criar,
	redireciona para a tela de login.
	"""
	from django.contrib.auth.forms import UserCreationForm
	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, "Conta criada com sucesso. Faça login para continuar.")
			return redirect("login")
	else:
		form = UserCreationForm()
	return render(request, "registration/signup.html", {"form": form})


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
