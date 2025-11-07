"""
URL configuration for library project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    # Redirecionamento de compatibilidade: se alguém visitar /admin/overdue/
    # (antigo caminho), enviamos para a nova rota nomeada do app.
    path('admin/overdue/', RedirectView.as_view(pattern_name='catalog:admin_overdue_loans', permanent=False)),

    # Painel do Django Admin (gerenciamento de usuários, livros etc.)
    path('admin/', admin.site.urls),

    # Autenticação (views prontas do Django)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Fluxo de recuperação de senha (templates básicos)
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # URLs do nosso app principal (catalog) na raiz do site
    path('', include('catalog.urls', namespace='catalog')),
]

# Servir arquivos de media em desenvolvimento
# Quando DEBUG=True, o Django serve arquivos de MEDIA_ROOT automaticamente
# static(): função auxiliar que adiciona a rota /media/<caminho> → arquivo físico
# Em produção (DEBUG=False), configure o servidor web para servir media/
# Exemplo Nginx: location /media/ { alias /caminho/para/media/; }
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
