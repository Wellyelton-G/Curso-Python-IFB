from functools import wraps  # ajuda a escrever decorators

from django.contrib import messages  # mensagens de retorno ("Empréstimo feito!")
from django.contrib.auth import login  # faz o login de um usuário pelo código
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied  # gera a resposta 403 (proibido)
from django.core.paginator import Paginator  # divide listas em páginas
from django.db.models import Avg, Count, F, Q  # ferramentas para montar consultas (Avg = média)
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import services  # regras de empréstimo, compartilhadas com a API (Aula 8)
from .exporters import EXPORTERS  # funções que geram CSV, Excel e PDF
from .forms import ReviewForm, SignUpForm
from .models import Book, Category, Loan, Review, SearchQuery
from .reports import REPORTS  # os relatórios da equipe

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
        books = books.filter(Q(title__icontains=q) | Q(author__icontains=q) | Q(isbn__icontains=q))

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
        "languages": Book.objects.exclude(language="")
        .values_list("language", flat=True)
        .distinct()
        .order_by("language"),
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
    """Baixa o resultado da busca atual em CSV, Excel ou PDF (mesmos filtros da listagem)."""
    # Só aceitamos os formatos que existem no dicionário EXPORTERS
    if file_format not in EXPORTERS:
        raise Http404("Formato desconhecido.")

    books = filter_books(request.GET)
    headers = ["Título", "Autor(a)", "ISBN", "Categoria", "Idioma", "Ano", "Disponíveis", "Total"]
    # Uma lista por livro, na mesma ordem do cabeçalho
    rows = [
        [
            b.title,
            b.author,
            b.isbn,
            b.category.name if b.category else "",
            b.language,
            b.edition_year or "",
            b.available,
            b.copies_total,
        ]
        for b in books
    ]
    export = EXPORTERS[file_format]  # escolhe a função certa (csv_response, xlsx_response...)
    return export("livros", "Acervo da biblioteca", headers, rows)


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

    # As regras ficam em services.py (Aula 8): a API usa exatamente as mesmas
    try:
        loan = services.borrow_book(book, request.user)
    except services.LoanError as error:
        messages.error(request, str(error))  # a mensagem da regra que impediu o empréstimo
        return redirect("catalog:book_list")

    messages.success(request, f"Empréstimo feito! Devolva “{book.title}” até {loan.due_date:%d/%m/%Y}.")
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


# ---------- Relatórios (equipe) ----------


@staff_required
def reports_index(request):
    """Página com a lista de relatórios disponíveis."""
    # Pares (pedaço da URL, título) para o template montar os links
    reports = [(slug, title) for slug, (title, _) in REPORTS.items()]
    return render(request, "catalog/reports_index.html", {"reports": reports})


def get_report(slug):
    """Procura o relatório pelo pedaço da URL e já gera os dados.

    Não é uma view (não recebe request): é uma função auxiliar usada pelas duas views abaixo.
    """
    if slug not in REPORTS:
        raise Http404("Relatório não encontrado.")
    title, build = REPORTS[slug]
    return title, build()  # agora sim a função do relatório é chamada (com parênteses)


@staff_required
def report_detail(request, slug):
    """Mostra um relatório na tela, com botões para baixar."""
    title, data = get_report(slug)
    # **data espalha headers e rows no contexto
    context = {"slug": slug, "title": title, **data}
    return render(request, "catalog/report_detail.html", context)


@staff_required
def report_export(request, slug, file_format):
    """Baixa um relatório em CSV, Excel ou PDF."""
    if file_format not in EXPORTERS:
        raise Http404("Formato desconhecido.")
    title, data = get_report(slug)
    # Nome do arquivo com a data de hoje, ex.: relatorio-populares-2026-09-24
    filename = f"relatorio-{slug}-{timezone.localdate():%Y-%m-%d}"
    return EXPORTERS[file_format](filename, title, data["headers"], data["rows"])
