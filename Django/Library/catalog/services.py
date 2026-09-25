"""Regras de negócio dos empréstimos.

Ficam aqui, fora das views, porque são usadas em dois lugares:
pelas páginas do site (views.py) e pela API (api_views.py).
Assim a regra é escrita uma vez só, e as duas portas de entrada se comportam igual.
"""

from datetime import timedelta  # representa um intervalo de tempo (ex.: 14 dias)

from django.db import transaction
from django.utils import timezone

from .models import Book, Loan

LOAN_DAYS = 21  # prazo padrão de empréstimo, em dias corridos (contando fins de semana e feriados)


class LoanError(Exception):
    """Uma regra de empréstimo impediu a ação. A mensagem explica o motivo ao usuário."""


def borrow_book(book, user):
    """Cria um empréstimo do livro para o usuário e devolve o Loan criado.

    Levanta LoanError se alguma regra não for cumprida.
    """
    # Aula 9: conferir e gravar precisam acontecer como uma coisa só (uma transação).
    # Se algo der errado no meio, nada é gravado.
    with transaction.atomic():
        # Relê o livro TRAVANDO a linha dele até o fim da transação. Se outra pessoa estiver
        # emprestando o mesmo livro agora, este pedido espera ela terminar antes de continuar.
        book = Book.objects.select_for_update().get(pk=book.pk)

        # Regra 1: precisa haver cópia disponível
        if book.copies_available == 0:
            raise LoanError(f"Não há cópias disponíveis de “{book.title}”.")

        # Regra 2: a pessoa não pode estar com este mesmo livro ainda sem devolver
        if book.loans.filter(user=user, returned_at__isnull=True).exists():
            raise LoanError(f"Você já está com “{book.title}”.")

        # Tudo certo: calcula o prazo e cria o empréstimo
        due_date = timezone.localdate() + timedelta(days=LOAN_DAYS)
        return Loan.objects.create(book=book, user=user, due_date=due_date)
