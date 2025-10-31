from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import Book, Loan


class LoanModelTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user("u1", password="pass")
		self.book = Book.objects.create(title="Teste", author="Autor", isbn="0000000000000", copies_total=2)

	def test_overdue_logic(self):
		# Create valid loan (due today) to satisfy DB constraint
		loan = Loan.objects.create(book=self.book, user=self.user, due_date=timezone.localdate())
		self.assertFalse(loan.is_overdue)
		# Simulate overdue without saving (avoid constraint)
		loan.due_date = timezone.localdate() - timedelta(days=1)
		self.assertTrue(loan.is_overdue)

	def test_mark_returned_sets_timestamp(self):
		loan = Loan.objects.create(book=self.book, user=self.user, due_date=timezone.localdate() + timedelta(days=7))
		self.assertIsNone(loan.returned_at)
		loan.mark_returned()
		loan.refresh_from_db()
		self.assertIsNotNone(loan.returned_at)

	def test_copies_available_counts_active_loans(self):
		self.assertEqual(self.book.copies_available, 2)
		Loan.objects.create(book=self.book, user=self.user, due_date=timezone.localdate() + timedelta(days=7))
		self.assertEqual(self.book.copies_available, 1)


class AuthViewsTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user("u2", password="pass")

	def test_logout_requires_post_and_redirects(self):
		# Login
		self.client.login(username="u2", password="pass")
		# GET should be 405 from Django 5.x LogoutView
		resp_get = self.client.get("/logout/")
		self.assertEqual(resp_get.status_code, 405)
		# POST should log out and redirect to login
		resp_post = self.client.post("/logout/")
		self.assertEqual(resp_post.status_code, 302)
		self.assertIn("/login/", resp_post.headers.get("Location", ""))
