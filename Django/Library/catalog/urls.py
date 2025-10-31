"""Rotas (URLs) específicas do app catalog.

Cada `path` abaixo liga um caminho de URL a uma função em `views.py`.
O `app_name` permite usar nomes de rota com namespace, por exemplo `catalog:book_list`.
"""

from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    # Página inicial: lista livros
    path("", views.book_list, name="book_list"),
    # Ações do usuário
    path("borrow/<int:book_id>/", views.borrow_book, name="borrow_book"),
    path("return/<int:loan_id>/", views.return_book, name="return_book"),
    path("me/loans/", views.my_loans, name="my_loans"),
    # Ferramentas de staff (evitamos o prefixo 'admin/' para não colidir com o Django Admin)
    path("staff/book/<int:book_id>/borrowers/", views.admin_book_borrowers, name="admin_book_borrowers"),
    path("staff/overdue/", views.admin_overdue_loans, name="admin_overdue_loans"),
    path("staff/loan/<int:loan_id>/return/", views.admin_mark_returned, name="admin_mark_returned"),
]