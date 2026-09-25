"""Serializers: convertem objetos do banco em JSON (e JSON recebido em objetos).

Cumprem na API o papel que o BaseModel do Pydantic cumpria no FastAPI:
descrevem os campos, validam os dados recebidos e montam as respostas.
"""

from rest_framework import serializers

from .models import Book, Category, Loan


class CategorySerializer(serializers.ModelSerializer):
    """Categoria em JSON: {"id": 1, "name": "Romance", "description": "..."}."""

    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class BookSerializer(serializers.ModelSerializer):
    """Livro em JSON. Os campos e as validações (ex.: ISBN único) vêm do model."""

    # Campo só de leitura: o nome da categoria, além do id que já vem no campo "category"
    category_name = serializers.CharField(source="category.name", read_only=True)
    # Campo calculado, também só de leitura: quantas cópias podem ser emprestadas agora
    available = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id", "title", "author", "isbn", "category", "category_name",
            "language", "publisher", "edition_year", "copies_total", "available",
        ]

    def get_available(self, obj) -> int:
        """Valor do campo "available" (o "-> int" ajuda a documentação a mostrar o tipo)."""
        # Na listagem, o valor já vem calculado do banco pelo annotate da filter_books.
        # Num livro recém-criado pela API ele não existe, então usamos a @property do model.
        if hasattr(obj, "available"):
            return obj.available
        return obj.copies_available


class LoanSerializer(serializers.ModelSerializer):
    """Empréstimo em JSON. Todos os campos são só de leitura: quem cria é a regra de negócio."""

    book_title = serializers.CharField(source="book.title", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)  # a @property do model Loan

    class Meta:
        model = Loan
        fields = ["id", "book", "book_title", "borrowed_at", "due_date", "returned_at", "is_overdue"]
        read_only_fields = ["book", "borrowed_at", "due_date", "returned_at"]
