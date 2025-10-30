from django.db import models
from django.contrib.auth.models import User
from catalog.models import Book
import datetime

class BorrowedBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(default=datetime.date.today() + datetime.timedelta(days=14))
    returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.book}"