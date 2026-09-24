from django.urls import path

from . import views

# Namespace do app: nos templates escrevemos {% url 'catalog:book_list' %}
app_name = "catalog"

urlpatterns = [
    # Página inicial: lista de livros
    path("", views.book_list, name="book_list"),
    # <int:book_id> captura um número da URL e entrega para a view como book_id
    path("livros/<int:book_id>/emprestar/", views.borrow_book, name="borrow_book"),
    path("emprestimos/", views.my_loans, name="my_loans"),
    path("emprestimos/<int:loan_id>/devolver/", views.return_book, name="return_book"),
    # Área da equipe (prefixo "equipe/" para não colidir com o "admin/" do Django)
    path("equipe/atrasados/", views.overdue_loans, name="overdue_loans"),
    path("equipe/livros/<int:book_id>/leitores/", views.book_borrowers, name="book_borrowers"),
    path("equipe/emprestimos/<int:loan_id>/devolver/", views.staff_mark_returned, name="staff_mark_returned"),
]
