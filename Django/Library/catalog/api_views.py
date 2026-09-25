"""Views da API REST (Django REST Framework).

Cada ViewSet agrupa, numa classe só, as operações sobre um recurso
(listar, consultar, criar, alterar, apagar). O router, em api_urls.py,
transforma essas operações em endereços e métodos HTTP.
"""

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import services  # as mesmas regras de empréstimo usadas pelas páginas
from .models import Category, Loan
from .permissions import IsStaffOrReadOnly
from .serializers import BookSerializer, CategorySerializer, LoanSerializer
from .views import filter_books  # a mesma busca e os mesmos filtros do acervo


class BookViewSet(viewsets.ModelViewSet):
    """Livros do acervo.

    Um ModelViewSet já oferece as cinco operações do CRUD:
    GET /livros/, GET /livros/{id}/, POST /livros/, PUT e PATCH /livros/{id}/ e DELETE /livros/{id}/.
    """

    serializer_class = BookSerializer
    permission_classes = [IsStaffOrReadOnly]  # ler: todos; escrever: só a equipe

    def get_queryset(self):
        # Reaproveita a busca da Aula 4: /api/livros/?q=machado&disponivel=1&ordenar=author
        return filter_books(self.request.query_params)

    def destroy(self, request, *args, **kwargs):
        """DELETE /livros/{id}/: não apaga livros que já têm histórico de empréstimos."""
        book = self.get_object()
        if book.loans.exists():
            # 409 Conflict: o pedido é válido, mas entra em conflito com o estado atual dos dados
            return Response(
                {"detail": "Este livro tem histórico de empréstimos e não pode ser apagado."},
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)  # o comportamento padrão: apaga e responde 204

    @extend_schema(request=None, responses={201: LoanSerializer})
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def emprestar(self, request, pk=None):
        """POST /livros/{id}/emprestar/: empresta o livro para o usuário autenticado."""
        book = self.get_object()  # 404 se o livro não existir
        try:
            loan = services.borrow_book(book, request.user)
        except services.LoanError as error:
            return Response({"detail": str(error)}, status=status.HTTP_409_CONFLICT)
        return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Categorias (somente leitura): GET /categorias/ e GET /categorias/{id}/."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]  # qualquer pessoa pode consultar


class LoanViewSet(viewsets.ReadOnlyModelViewSet):
    """Os empréstimos do usuário autenticado: GET /emprestimos/ e GET /emprestimos/{id}/."""

    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ao gerar a documentação (/api/docs/) não há usuário logado: devolvemos uma consulta vazia
        if getattr(self, "swagger_fake_view", False):
            return Loan.objects.none()
        # Só os empréstimos de quem fez o pedido: o de outra pessoa responde 404
        return Loan.objects.filter(user=self.request.user).select_related("book")

    @extend_schema(request=None, responses={200: LoanSerializer})
    @action(detail=True, methods=["post"])
    def devolver(self, request, pk=None):
        """POST /emprestimos/{id}/devolver/: registra a devolução."""
        loan = self.get_object()
        if not loan.is_active:
            return Response({"detail": "Este livro já tinha sido devolvido."}, status=status.HTTP_409_CONFLICT)
        loan.mark_returned()  # a mesma regra usada pelas páginas e pelo Admin
        return Response(LoanSerializer(loan).data)
