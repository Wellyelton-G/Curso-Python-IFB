import csv  # módulo do Python para escrever arquivos CSV
from datetime import timedelta  # representa um intervalo de tempo (ex.: 14 dias)
from functools import wraps  # ajuda a escrever decorators

from django.contrib import messages  # mensagens de retorno ("Empréstimo feito!")
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied  # gera a resposta 403 (proibido)
from django.core.paginator import Paginator  # divide listas em páginas
from django.db.models import Count, F, Q  # ferramentas para montar consultas
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Book, Category, Loan, SearchQuery

LOAN_DAYS = 14  # prazo padrão de empréstimo, em dias
BOOKS_PER_PAGE = 10  # quantos livros aparecem por página

# Opções de ordenação: valor que vai na URL -> (texto exibido, campos do order_by).
# O sinal de menos em "-edition_year" significa ordem decrescente.
ORDER_OPTIONS = {
    "title": ("Título (A–Z)", ["title"]),
    "author": ("Autor(a) (A–Z)", ["author", "title"]),
    "recent": ("Edição mais recente", ["-edition_year", "title"]),
    "available": ("Mais cópias disponíveis", ["-available", "title"]),
}

# Filtros que, se preenchidos, fazem a busca entrar no histórico
SEARCH_FIELDS = ["q", "title", "author", "publisher", "categoria", "idioma", "ano_min", "ano_max", "disponivel"]


def staff_required(view):
    """Decorator: só deixa passar quem está logado E faz parte da equipe."""

    @wraps(view)  # mantém o nome e a documentação da view original
    @login_required  # primeiro exige login
    def wrapper(request, *args, **kwargs):
        # Logado, mas não é da equipe: resposta 403 ("proibido")
        if not request.user.is_staff:
            raise PermissionDenied
        # Tudo certo: executa a view original com os mesmos argumentos
        return view(request, *args, **kwargs)

    return wrapper  # a função "embrulhada" passa a ocupar o lugar da view


def filter_books(params):
    """Aplica busca, filtros e ordenação.

    Recebe os parâmetros da URL (request.GET) e devolve um queryset de livros,
    já com o campo calculado `available` (cópias disponíveis).
    É usada pela listagem E pela exportação, para as duas mostrarem o mesmo resultado.
    """
    # Consulta base: traz a categoria junto (select_related) e calcula as cópias disponíveis
    books = Book.objects.select_related("category").annotate(
        available=F("copies_total") - Count("loans", filter=Q(loans__returned_at__isnull=True))
    )

    # Busca simples: um texto procurado em vários campos ao mesmo tempo (OU)
    q = params.get("q", "").strip()
    if q:
        books = books.filter(
            Q(title__icontains=q) | Q(author__icontains=q) | Q(isbn__icontains=q)
        )

    # Busca avançada: cada campo filtra só a sua coluna.
    # **{...} transforma o dicionário em argumento nomeado: {"author__icontains": "x"} -> author__icontains="x"
    for field in ["title", "author", "publisher"]:
        value = params.get(field, "").strip()
        if value:
            books = books.filter(**{f"{field}__icontains": value})

    # isdigit() ignora valores que não são números (ex.: ?categoria=abc)
    categoria = params.get("categoria", "")
    if categoria.isdigit():
        books = books.filter(category_id=int(categoria))

    # __iexact: igual, sem diferenciar maiúsculas de minúsculas
    idioma = params.get("idioma", "").strip()
    if idioma:
        books = books.filter(language__iexact=idioma)

    # __gte: maior ou igual; __lte: menor ou igual
    ano_min = params.get("ano_min", "")
    if ano_min.isdigit():
        books = books.filter(edition_year__gte=int(ano_min))

    ano_max = params.get("ano_max", "")
    if ano_max.isdigit():
        books = books.filter(edition_year__lte=int(ano_max))

    if params.get("disponivel") == "1":
        books = books.filter(available__gt=0)

    # Ordenação: só aceitamos valores do dicionário ORDER_OPTIONS; qualquer outro vira "title"
    order_key = params.get("ordenar", "title")
    if order_key not in ORDER_OPTIONS:
        order_key = "title"
    _, order_fields = ORDER_OPTIONS[order_key]  # pega só a lista de campos (ignora o texto)
    return books.order_by(*order_fields)  # o * espalha a lista em vários argumentos


def filter_choices():
    """Dados usados para montar os <select> dos formulários de busca."""
    return {
        "categories": Category.objects.all(),
        # values_list(..., flat=True) devolve uma lista simples; distinct() remove repetidos
        "languages": Book.objects.exclude(language="").values_list("language", flat=True)
                                 .distinct().order_by("language"),
        # Lista de pares (valor, texto) para as opções de ordenação
        "order_options": [(key, label) for key, (label, _) in ORDER_OPTIONS.items()],
    }


@login_required
def book_list(request):
    """Lista o acervo com busca, filtros, ordenação e paginação."""
    books = filter_books(request.GET)

    # Guarda no histórico, mas só na 1ª página e só se algum filtro foi usado
    used = {key: request.GET[key] for key in SEARCH_FIELDS if request.GET.get(key)}
    if used and "page" not in request.GET:
        params = request.GET.dict()  # todos os parâmetros da URL como dicionário comum
        SearchQuery.objects.create(user=request.user, q=used.get("q", ""), params=params)

    paginator = Paginator(books, BOOKS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "params": request.GET,  # para os campos do formulário "lembrarem" o que foi digitado
        **filter_choices(),  # espalha categories, languages e order_options no contexto
    }
    return render(request, "catalog/book_list.html", context)


@login_required
def advanced_search(request):
    """Formulário completo de busca. Ele envia os dados (GET) para a book_list."""
    return render(request, "catalog/advanced_search.html", filter_choices())


@login_required
def search_history(request):
    """As últimas 50 buscas do usuário logado."""
    # searches existe por causa do related_name do SearchQuery; [:50] limita a 50 resultados
    searches = request.user.searches.all()[:50]
    return render(request, "catalog/search_history.html", {"searches": searches})


@login_required
def export_books(request, file_format):
    """Baixa o resultado da busca atual em CSV ou Excel (mesmos filtros da listagem)."""
    books = filter_books(request.GET)
    header = ["Título", "Autor(a)", "ISBN", "Categoria", "Idioma", "Ano", "Disponíveis", "Total"]
    # Uma lista por livro, na mesma ordem do cabeçalho
    rows = [
        [b.title, b.author, b.isbn, b.category.name if b.category else "",
         b.language, b.edition_year or "", b.available, b.copies_total]
        for b in books
    ]

    if file_format == "csv":
        # content_type diz ao navegador o tipo do arquivo;
        # Content-Disposition "attachment" manda baixar em vez de abrir na tela
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="livros.csv"'
        response.write("\ufeff")  # "BOM": faz o Excel reconhecer os acentos
        writer = csv.writer(response, delimiter=";")  # ; é o separador que o Excel em português espera
        writer.writerow(header)
        writer.writerows(rows)
        return response

    if file_format == "xlsx":
        from openpyxl import Workbook  # importado aqui: só é necessário nesta parte

        workbook = Workbook()  # planilha nova
        sheet = workbook.active  # a primeira aba
        sheet.title = "Livros"
        sheet.append(header)  # append adiciona uma linha
        for row in rows:
            sheet.append(row)
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="livros.xlsx"'
        workbook.save(response)  # grava a planilha direto na resposta
        return response

    # Qualquer outro formato na URL: página não encontrada
    raise Http404("Formato desconhecido.")


@login_required
def book_suggestions(request):
    """API para o autocompletar: /api/sugestoes/?q=mach -> {"suggestions": [...]}"""
    q = request.GET.get("q", "").strip()
    suggestions = []
    if len(q) >= 2:  # só sugere a partir de 2 letras
        titles = Book.objects.filter(title__icontains=q).values_list("title", flat=True)[:5]
        authors = Book.objects.filter(author__icontains=q).values_list("author", flat=True).distinct()[:5]
        # dict.fromkeys junta as duas listas e remove repetidos mantendo a ordem
        suggestions = list(dict.fromkeys([*titles, *authors]))
    # JsonResponse devolve dados (JSON) em vez de uma página HTML
    return JsonResponse({"suggestions": suggestions})


@login_required
@require_POST  # recusa pedidos GET com erro 405: emprestar só por formulário
def borrow_book(request, book_id):
    """Cria um empréstimo do livro para o usuário logado."""
    # Busca o livro pelo id; se não existir, responde 404 (página não encontrada)
    book = get_object_or_404(Book, pk=book_id)

    # Regra 1: precisa haver cópia disponível
    if book.copies_available == 0:
        messages.error(request, f"Não há cópias disponíveis de “{book.title}”.")
        return redirect("catalog:book_list")

    # Regra 2: a pessoa não pode estar com este mesmo livro ainda sem devolver
    already_has = book.loans.filter(user=request.user, returned_at__isnull=True).exists()
    if already_has:
        messages.warning(request, f"Você já está com “{book.title}”.")
        return redirect("catalog:book_list")

    # Tudo certo: calcula o prazo e cria o empréstimo
    due_date = timezone.localdate() + timedelta(days=LOAN_DAYS)
    Loan.objects.create(book=book, user=request.user, due_date=due_date)
    messages.success(request, f"Empréstimo feito! Devolva “{book.title}” até {due_date:%d/%m/%Y}.")
    # Depois de um POST, sempre redirecionamos (padrão Post/Redirect/Get)
    return redirect("catalog:my_loans")


@login_required
def my_loans(request):
    """Lista os empréstimos do usuário logado (ativos e devolvidos)."""
    # select_related("book") traz o livro na mesma consulta, evitando uma consulta extra por empréstimo
    loans = Loan.objects.filter(user=request.user).select_related("book")
    return render(request, "catalog/my_loans.html", {"loans": loans})


@login_required
@require_POST
def return_book(request, loan_id):
    """Registra a devolução de um empréstimo do próprio usuário."""
    # user=request.user impede devolver o empréstimo de outra pessoa trocando o número na URL
    loan = get_object_or_404(Loan, pk=loan_id, user=request.user)

    if loan.returned_at:
        messages.info(request, "Este livro já tinha sido devolvido.")
    else:
        loan.mark_returned()  # regra de negócio que fica no model
        messages.success(request, f"“{loan.book.title}” devolvido. Obrigado!")
    return redirect("catalog:my_loans")


# ---------- Área da equipe (staff) ----------


@staff_required
def overdue_loans(request):
    """Empréstimos ativos cujo prazo já venceu, do mais antigo para o mais novo."""
    # Duas condições separadas por vírgula valem juntas (E):
    # ainda não devolvido E prazo menor que hoje (__lt significa "menor que")
    loans = (
        Loan.objects.filter(returned_at__isnull=True, due_date__lt=timezone.localdate())
        .select_related("book", "user")  # traz livro e usuário na mesma consulta
        .order_by("due_date")
    )
    return render(request, "catalog/overdue_loans.html", {"loans": loans})


@staff_required
def book_borrowers(request, book_id):
    """Quem está com um determinado livro neste momento."""
    book = get_object_or_404(Book, pk=book_id)
    loans = book.loans.filter(returned_at__isnull=True).select_related("user")
    return render(request, "catalog/book_borrowers.html", {"book": book, "loans": loans})


@staff_required
@require_POST
def staff_mark_returned(request, loan_id):
    """A equipe registra a devolução de qualquer empréstimo."""
    # Aqui não filtramos por usuário: a equipe pode devolver o empréstimo de qualquer leitor
    loan = get_object_or_404(Loan, pk=loan_id)
    if loan.is_active:
        loan.mark_returned()
        messages.success(request, f"Devolução de “{loan.book.title}” ({loan.user}) registrada.")
    return redirect("catalog:overdue_loans")
