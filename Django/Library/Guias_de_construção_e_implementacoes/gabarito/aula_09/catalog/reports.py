"""Relatórios para a equipe da biblioteca.

Todo relatório é uma função que devolve o MESMO formato de dicionário:

    {"headers": ["Coluna 1", "Coluna 2"], "rows": [[valor, valor], [valor, valor]]}

Graças a esse "contrato", uma única página HTML, um único gerador de Excel
e um único gerador de PDF servem para todos os relatórios.
"""

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone

from .models import Book, Category, Loan


def all_loans():
    """Os 200 empréstimos mais recentes, com a situação de cada um."""
    # [:200] vira um LIMIT 200 no SQL: o banco devolve no máximo 200 linhas
    loans = Loan.objects.select_related("book", "user").order_by("-borrowed_at")[:200]
    rows = []
    for loan in loans:
        # A mesma lógica de situação usada na página "Meus empréstimos"
        if loan.returned_at:
            status = "Devolvido"
        elif loan.is_overdue:
            status = "Atrasado"
        else:
            status = "Em dia"
        rows.append(
            [
                loan.book.title,
                loan.user.username,
                loan.borrowed_at.strftime("%d/%m/%Y"),  # strftime formata a data como texto
                loan.due_date.strftime("%d/%m/%Y"),
                status,
            ]
        )
    return {"headers": ["Livro", "Leitor(a)", "Emprestado em", "Devolver até", "Situação"], "rows": rows}


def popular_books():
    """Os 20 livros mais emprestados de todos os tempos."""
    books = (
        Book.objects.annotate(total=Count("loans"))  # conta os empréstimos de cada livro (GROUP BY)
        .filter(total__gt=0)  # filtra pelo resultado da contagem (HAVING no SQL)
        .order_by("-total", "title")[:20]  # mais emprestados primeiro; empate: ordem alfabética
    )
    rows = [[book.title, book.author, book.total] for book in books]
    return {"headers": ["Título", "Autor(a)", "Empréstimos"], "rows": rows}


def active_readers():
    """Os 20 leitores que mais pegaram livros, e quantos estão com eles agora."""
    users = (
        User.objects.annotate(
            total=Count("loans"),  # todos os empréstimos da pessoa
            ativos=Count("loans", filter=Q(loans__returned_at__isnull=True)),  # só os não devolvidos
        )
        .filter(total__gt=0)
        .order_by("-total", "username")[:20]
    )
    rows = [[user.username, user.total, user.ativos] for user in users]
    return {"headers": ["Leitor(a)", "Empréstimos no total", "Com ele(a) agora"], "rows": rows}


def overdue_loans():
    """Empréstimos atrasados, do mais atrasado para o menos atrasado."""
    today = timezone.localdate()
    loans = (
        Loan.objects.filter(returned_at__isnull=True, due_date__lt=today)
        .select_related("book", "user")
        .order_by("due_date")  # prazo mais antigo = mais atrasado
    )
    # Subtrair duas datas dá um intervalo (timedelta); .days é o número de dias
    rows = [
        [loan.book.title, loan.user.username, loan.due_date.strftime("%d/%m/%Y"), (today - loan.due_date).days]
        for loan in loans
    ]
    return {"headers": ["Livro", "Leitor(a)", "Devolver até", "Dias de atraso"], "rows": rows}


def loans_by_category():
    """Quantos livros e quantos empréstimos cada categoria tem (um "GROUP BY")."""
    categories = Category.objects.annotate(
        # distinct=True: sem ele, cada livro seria contado uma vez para cada empréstimo que tem
        livros=Count("books", distinct=True),
        # books__loans atravessa duas relações: categoria -> livros -> empréstimos
        emprestimos=Count("books__loans"),
    ).order_by("-emprestimos", "name")
    rows = [[category.name, category.livros, category.emprestimos] for category in categories]
    return {"headers": ["Categoria", "Livros", "Empréstimos"], "rows": rows}


# "Cardápio" de relatórios: pedaço da URL -> (título, função que gera os dados).
# As funções aparecem sem parênteses: guardamos a função em si, para chamá-la depois.
REPORTS = {
    "emprestimos": ("Todos os empréstimos", all_loans),
    "populares": ("Livros mais emprestados", popular_books),
    "leitores": ("Leitores mais ativos", active_readers),
    "atrasados": ("Empréstimos atrasados", overdue_loans),
    "categorias": ("Empréstimos por categoria", loans_by_category),
}
