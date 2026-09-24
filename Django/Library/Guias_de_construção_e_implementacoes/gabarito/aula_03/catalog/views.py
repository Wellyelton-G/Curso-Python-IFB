from datetime import timedelta  # representa um intervalo de tempo (ex.: 14 dias)
from functools import wraps  # ajuda a escrever decorators

from django.contrib import messages  # mensagens de retorno ("Empréstimo feito!")
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied  # gera a resposta 403 (proibido)
from django.core.paginator import Paginator  # divide listas em páginas
from django.db.models import Count, F, Q  # ferramentas para montar consultas
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Book, Loan

LOAN_DAYS = 14  # prazo padrão de empréstimo, em dias
BOOKS_PER_PAGE = 10  # quantos livros aparecem por página


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


@login_required
def book_list(request):
    """Lista o acervo com busca, filtro de disponibilidade e paginação."""
    # 1) Consulta base: cada livro já vem com o campo calculado "available" (cópias disponíveis).
    #    Count conta os empréstimos ainda não devolvidos; F("copies_total") é o valor da coluna.
    books = Book.objects.annotate(
        available=F("copies_total") - Count("loans", filter=Q(loans__returned_at__isnull=True))
    ).order_by("title")

    # 2) Busca por texto: /?q=machado
    q = request.GET.get("q", "").strip()  # "" se o parâmetro não vier; strip tira espaços das pontas
    if q:
        # Q permite combinar condições com | (OU): título OU autor OU ISBN contém o texto
        books = books.filter(
            Q(title__icontains=q) | Q(author__icontains=q) | Q(isbn__icontains=q)
        )

    # 3) Somente disponíveis: /?disponivel=1
    only_available = request.GET.get("disponivel") == "1"
    if only_available:
        books = books.filter(available__gt=0)  # __gt significa "maior que"

    # 4) Paginação: /?page=2
    paginator = Paginator(books, BOOKS_PER_PAGE)
    # get_page aceita número inválido sem erro (vai para a primeira ou para a última página)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,  # só os livros da página atual
        "q": q,  # para o campo de busca mostrar o que foi digitado
        "only_available": only_available,  # para a caixa de seleção continuar marcada
    }
    return render(request, "catalog/book_list.html", context)


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
