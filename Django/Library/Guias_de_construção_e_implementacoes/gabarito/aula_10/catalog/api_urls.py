"""Endereços da API. Todos começam com /api/ (veja library/urls.py)."""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import permissions
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import APIRootView, DefaultRouter

from . import api_views

app_name = "api"


class PublicAPIRootView(APIRootView):
    """Página inicial da API (/api/), com os links dos recursos. Aberta a todos."""

    permission_classes = [permissions.AllowAny]


# O router cria as rotas de cada ViewSet automaticamente:
# livros/ e livros/{id}/, e também as @action, como livros/{id}/emprestar/
router = DefaultRouter()
router.APIRootView = PublicAPIRootView  # sem isto, a página inicial exigiria login
router.register("livros", api_views.BookViewSet, basename="livro")
router.register("categorias", api_views.CategoryViewSet, basename="categoria")
router.register("emprestimos", api_views.LoanViewSet, basename="emprestimo")

urlpatterns = [
    path("", include(router.urls)),
    # POST com usuário e senha devolve um token: {"token": "..."}
    path("token/", obtain_auth_token, name="token"),
    # Descrição da API no padrão OpenAPI e a página de documentação interativa (Swagger)
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api:schema"), name="docs"),
]
