"""Configurações do Django Admin para Book e Loan.

O Django Admin é um painel pronto para gerenciar dados. Aqui
personalizamos como os modelos aparecem e criamos uma ação
para marcar empréstimos como devolvidos.
"""

from django.contrib import admin
from django.utils import timezone

from .models import Book, Loan


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
	# Quais colunas mostrar na listagem
	list_display = ("title", "author", "isbn", "copies_total", "copies_available")
	# Campos pesquisáveis na barra de busca
	search_fields = ("title", "author", "isbn")


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
	# Listagem com campos úteis e um indicador de atraso
	list_display = ("book", "user", "borrowed_at", "due_date", "returned_at", "_is_overdue")
	# Filtro lateral por devolução
	list_filter = ("returned_at",)
	# Busca por título do livro e username do usuário (lookup via relacionamento)
	search_fields = ("book__title", "user__username")
	# Ação em massa: marcar registros selecionados como devolvidos
	actions = ("marcar_como_devolvido",)

	@admin.display(boolean=True, description="Atrasado")
	def _is_overdue(self, obj: Loan):
		return obj.is_overdue

	@admin.action(description="Marcar como devolvido")
	def marcar_como_devolvido(self, request, queryset):
		# Percorre apenas empréstimos ainda ativos e define returned_at
		updated = 0
		now = timezone.now()
		for loan in queryset.filter(returned_at__isnull=True):
			loan.returned_at = now
			loan.save(update_fields=["returned_at"])
			updated += 1
		self.message_user(request, f"{updated} empréstimo(s) marcados como devolvidos.")
