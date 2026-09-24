from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Lista de endereços do projeto. O Django testa de cima para baixo e usa o primeiro que combinar.
urlpatterns = [
    # Painel administrativo: /admin/
    path("admin/", admin.site.urls),
    # Login, logout e recuperação de senha prontos do Django: /contas/login/, /contas/logout/ ...
    path("contas/", include("django.contrib.auth.urls")),
    # Todos os outros endereços são resolvidos pelo arquivo catalog/urls.py
    path("", include("catalog.urls")),
]

# Só em desenvolvimento (DEBUG=True): o próprio Django entrega as imagens enviadas (capas).
# Em um servidor de verdade, quem faz isso é o servidor web (Nginx, Apache...).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
