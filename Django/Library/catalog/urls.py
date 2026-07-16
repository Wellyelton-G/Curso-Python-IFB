"""Rotas (URLs) específicas do app catalog.

Cada `path` abaixo liga um caminho de URL a uma função em `views.py`.
O `app_name` permite usar nomes de rota com namespace, por exemplo `catalog:book_list`.
"""

from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    # raiz do app (e do site se incluído como "/"): lista livros
    path("", views.book_list, name="book_list"),
    path("book/<int:book_id>/", views.book_detail, name="book_detail"),  # adicionada rota de detalhes
    path("advanced-search/", views.advanced_search, name="advanced_search"),
    path("me/searches/", views.search_history, name="search_history"),
    path("signup/", views.signup, name="signup"),
    # Ações do usuário
    path("borrow/<int:book_id>/", views.borrow_book, name="borrow_book"),
    path("return/<int:loan_id>/", views.return_book, name="return_book"),
    path("me/loans/", views.my_loans, name="my_loans"),
    # Ferramentas de staff (evitamos o prefixo 'admin/' para não colidir com o Django Admin)
    path("staff/book/<int:book_id>/borrowers/", views.admin_book_borrowers, name="admin_book_borrowers"),
    path("staff/overdue/", views.admin_overdue_loans, name="admin_overdue_loans"),
    path("staff/loan/<int:loan_id>/return/", views.admin_mark_returned, name="admin_mark_returned"),
    # Avaliações
    path("book/<int:book_id>/review/", views.add_review, name="add_review"),
    path("review/<int:review_id>/delete/", views.delete_review, name="delete_review"),
    # Relatórios e exportação (apenas staff) -> acessar direto pelas URLs:
    # /catalog/reports/loans/
    # /catalog/reports/popular-books/
    # /catalog/reports/active-users/
    # /catalog/reports/overdue-loans/
    # Exportação: /catalog/reports/export/?type=loans&format=pdf|xlsx
    path("reports/loans/", views.report_loans, name="report_loans"),
    path("reports/popular-books/", views.report_popular_books, name="report_popular_books"),
    path("reports/active-users/", views.report_active_users, name="report_active_users"),
    path("reports/overdue-loans/", views.report_overdue_loans, name="report_overdue_loans"),
    path("reports/export/", views.report_export, name="report_export"),  # ?type=loans&format=pdf|xlsx
]