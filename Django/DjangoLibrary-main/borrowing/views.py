from django.shortcuts import render, redirect, get_object_or_404
from .models import BorrowedBook
from .forms import BorrowBookForm, RegisterForm
from catalog.models import Book
from django.contrib.auth.decorators import login_required


@login_required
def borrow_book(request):
    if request.method == 'POST':
        form = BorrowBookForm(request.POST)
        if form.is_valid():
            borrowed = form.save(commit=False)
            borrowed.user = request.user
            borrowed.save()

            # Decrease available copies
            book = borrowed.book
            book.available_copies -= 1
            book.save()

            return redirect('my_books')
    else:
        form = BorrowBookForm()
    return render(request, 'borrowing/borrow_book.html', {'form': form})

@login_required
def return_book(request, pk):
    borrowed_book = get_object_or_404(BorrowedBook, pk=pk, user=request.user, returned=False)
    borrowed_book.returned = True
    borrowed_book.save()

    # Increase available copies
    book = borrowed_book.book
    book.available_copies += 1
    book.save()

    return redirect('my_books')

@login_required
def my_books(request):
    borrowed_books = BorrowedBook.objects.filter(user=request.user, returned=False)
    history = BorrowedBook.objects.filter(user=request.user, returned=True).order_by('-borrow_date')[:10]
    return render(request, 'borrowing/my_books.html', {
        'borrowed_books': borrowed_books,
        'history': history,
    })

@login_required
def overdue_books(request):
    overdue = BorrowedBook.objects.filter(due_date__lt=datetime.date.today(), returned=False)
    return render(request, 'borrowing/overdue_books.html', {'overdue_books': overdue})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login after successful registration
    else:
        form = RegisterForm()
    
    return render(request, 'registration/register.html', {'form': form})