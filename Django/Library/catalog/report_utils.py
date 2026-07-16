from django.db.models import Count
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Loan, Book

User = get_user_model()

def build_report_dataset(report_type: str):
	"""Retorna dict com title, headers, rows para cada tipo de relatório."""
	now_str = timezone.localtime().strftime("%d/%m/%Y %H:%M")
	if report_type == "loans":
		qs = Loan.objects.select_related("book", "user").order_by("-borrowed_at")
		return {
			"title": f"Relatório de Empréstimos ({now_str})",
			"headers": ["Livro", "Usuário", "Emprestado em", "Devolver até", "Status"],
			"rows": [
				[
					l.book.title,
					str(l.user),
					l.borrowed_at.strftime("%d/%m/%Y"),
					l.due_date.strftime("%d/%m/%Y"),
					"Devolvido" if l.returned_at else ("Atrasado" if l.is_overdue else "Em aberto"),
				]
				for l in qs
			],
		}
	if report_type == "popular_books":
		qs = (
			Book.objects.annotate(total_loans=Count("loans"))
			.filter(total_loans__gt=0)
			.order_by("-total_loans", "title")[:50]
		)
		return {
			"title": f"Livros Mais Populares ({now_str})",
			"headers": ["Título", "Autor", "Empréstimos"],
			"rows": [[b.title, b.author, b.total_loans] for b in qs],
		}
	if report_type == "active_users":
		qs = (
			User.objects.annotate(total_loans=Count("loans"))
			.filter(total_loans__gt=0)
			.order_by("-total_loans", "username")[:50]
		)
		return {
			"title": f"Usuários Mais Ativos ({now_str})",
			"headers": ["Usuário", "Empréstimos"],
			"rows": [[str(u), u.total_loans] for u in qs],
		}
	if report_type == "overdue_loans":
		qs = (
			Loan.objects.select_related("book", "user")
			.filter(returned_at__isnull=True, due_date__lt=timezone.localdate())
			.order_by("due_date")
		)
		return {
			"title": f"Empréstimos Atrasados ({now_str})",
			"headers": ["Livro", "Usuário", "Devolver até", "Dias atraso"],
			"rows": [
				[
					l.book.title,
					str(l.user),
					l.due_date.strftime("%d/%m/%Y"),
					(timezone.localdate() - l.due_date).days,
				]
				for l in qs
			],
		}
	return {"title": "Relatório vazio", "headers": [], "rows": []}
