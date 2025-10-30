from django.urls import path, include
from django.contrib import admin
from catalog import views as catalog_views
from borrowing import views as borrowing_views
from django.contrib.auth import views as auth_views
from borrowing.views import register_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Catalog
    path('', catalog_views.book_list, name='book_list'),
    path('add-book/', catalog_views.add_book, name='add_book'),
    
    # Borrowing
    path('borrow/', borrowing_views.borrow_book, name='borrow_book'),
    path('return/<int:pk>/', borrowing_views.return_book, name='return_book'),
    path('my-books/', borrowing_views.my_books, name='my_books'),
    path('overdue/', borrowing_views.overdue_books, name='overdue_books'),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register_view, name='register')  # ← Adicionado
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)