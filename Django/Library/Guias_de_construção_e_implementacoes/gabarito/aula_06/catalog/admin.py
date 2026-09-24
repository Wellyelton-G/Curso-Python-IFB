from django.contrib import admin

from .models import Book, Category, Loan, Review, SearchQuery  # o ponto significa "deste mesmo app"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)  # a vírgula faz disto uma tupla de um item só


# O decorator @admin.register liga o model Book à classe de configuração logo abaixo
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # Colunas mostradas na lista de livros (pode incluir @property, como copies_available)
    list_display = ("title", "author", "category", "language", "edition_year",
                    "copies_total", "copies_available")
    # Filtros laterais por categoria e idioma
    list_filter = ("category", "language")
    # Campos pesquisados pela caixa de busca do Admin
    search_fields = ("title", "author", "isbn", "publisher")


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    # "atrasado" não é um campo: é o método definido mais abaixo nesta classe
    list_display = ("book", "user", "borrowed_at", "due_date", "returned_at", "atrasado")
    # Filtros que aparecem na lateral direita da lista
    list_filter = ("returned_at", "due_date")
    # Dois sublinhados "atravessam" a ForeignKey: busca no título do livro e no nome do usuário
    search_fields = ("book__title", "user__username")
    # Ações em massa disponíveis no menu "Ação" da lista
    actions = ["marcar_como_devolvido"]

    # boolean=True faz o Admin mostrar um ícone de sim/não em vez de True/False
    @admin.display(boolean=True, description="Atrasado?")
    def atrasado(self, obj):
        # obj é o empréstimo da linha que está sendo desenhada
        return obj.is_overdue

    @admin.action(description="Marcar como devolvido")
    def marcar_como_devolvido(self, request, queryset):
        # queryset contém os empréstimos que o usuário marcou na lista
        ativos = queryset.filter(returned_at__isnull=True)  # ignora os que já foram devolvidos
        total = ativos.count()
        for loan in ativos:
            loan.mark_returned()  # reaproveita a regra que está no model
        # Mensagem que aparece no topo da página do Admin
        self.message_user(request, f"{total} empréstimo(s) marcado(s) como devolvido(s).")


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ("user", "q", "created_at")
    list_filter = ("created_at",)
    search_fields = ("q", "user__username")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("book__title", "user__username", "comment")
