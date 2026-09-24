from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse  # gera o endereço a partir do nome da rota (como o {% url %})
from django.utils import timezone

from .models import Book, Loan


def make_loan(book, user, days=14):
    """Atalho para criar empréstimos nos testes (days negativo = prazo já vencido)."""
    return Loan.objects.create(book=book, user=user, due_date=timezone.localdate() + timedelta(days=days))


class LoanModelTests(TestCase):
    """Testes das regras que ficam nos models."""

    def setUp(self):
        # setUp roda antes de CADA teste; o banco de testes começa vazio
        self.user = User.objects.create_user("maria", password="senha-forte-123")
        self.book = Book.objects.create(title="Dom Casmurro", author="Machado de Assis",
                                        isbn="9788535910663", copies_total=2)

    def test_copies_available_desconta_emprestimos_ativos(self):
        self.assertEqual(self.book.copies_available, 2)
        make_loan(self.book, self.user)
        self.assertEqual(self.book.copies_available, 1)  # uma cópia saiu

    def test_emprestimo_com_prazo_vencido_esta_atrasado(self):
        loan = make_loan(self.book, self.user, days=-1)  # prazo era ontem
        self.assertTrue(loan.is_overdue)

    def test_mark_returned_encerra_o_emprestimo(self):
        loan = make_loan(self.book, self.user)
        loan.mark_returned()
        self.assertFalse(loan.is_active)
        self.assertFalse(loan.is_overdue)
        self.assertEqual(self.book.copies_available, 2)  # a cópia voltou para a estante


class BookListViewTests(TestCase):
    """Testes da página do acervo."""

    def setUp(self):
        self.user = User.objects.create_user("maria", password="senha-forte-123")
        self.client.force_login(self.user)  # entra no sistema sem precisar digitar a senha
        Book.objects.create(title="Dom Casmurro", author="Machado de Assis", isbn="1111111111111")
        Book.objects.create(title="Capitães da Areia", author="Jorge Amado", isbn="2222222222222")

    def test_exige_login(self):
        self.client.logout()
        response = self.client.get(reverse("catalog:book_list"))
        self.assertEqual(response.status_code, 302)  # 302 = redirecionou para o login

    def test_busca_por_autor(self):
        # O segundo argumento do get vira a parte ?q=machado da URL
        response = self.client.get(reverse("catalog:book_list"), {"q": "machado"})
        self.assertContains(response, "Dom Casmurro")
        self.assertNotContains(response, "Capitães da Areia")

    def test_filtro_somente_disponiveis(self):
        livro = Book.objects.get(isbn="2222222222222")
        make_loan(livro, self.user)  # a única cópia saiu
        response = self.client.get(reverse("catalog:book_list"), {"disponivel": "1"})
        self.assertContains(response, "Dom Casmurro")
        self.assertNotContains(response, "Capitães da Areia")

    def test_paginacao_mostra_10_por_pagina(self):
        # Mais 15 livros: com os 2 do setUp, são 17 livros, ou seja, 2 páginas
        for i in range(15):
            Book.objects.create(title=f"Livro {i:02d}", author="Autor", isbn=f"99900000000{i:02d}")
        response = self.client.get(reverse("catalog:book_list"))
        # response.context guarda as variáveis que a view enviou para o template
        self.assertEqual(len(response.context["page_obj"]), 10)
        self.assertContains(response, "Página 1 de 2")


class LoanViewsTests(TestCase):
    """Testes de emprestar e devolver pelas páginas."""

    def setUp(self):
        self.maria = User.objects.create_user("maria", password="senha-forte-123")
        self.joao = User.objects.create_user("joao", password="senha-forte-123")
        self.book = Book.objects.create(title="Dom Casmurro", author="Machado de Assis",
                                        isbn="9788535910663", copies_total=1)

    def test_emprestar_cria_emprestimo(self):
        self.client.force_login(self.maria)
        # args preenche o <int:book_id> da rota
        self.client.post(reverse("catalog:borrow_book", args=[self.book.id]))
        self.assertEqual(Loan.objects.filter(user=self.maria, book=self.book).count(), 1)

    def test_emprestar_exige_post(self):
        self.client.force_login(self.maria)
        response = self.client.get(reverse("catalog:borrow_book", args=[self.book.id]))
        self.assertEqual(response.status_code, 405)  # 405 = método não permitido
        self.assertEqual(Loan.objects.count(), 0)  # nada foi criado

    def test_nao_empresta_sem_copias(self):
        make_loan(self.book, self.joao)  # João pegou a única cópia
        self.client.force_login(self.maria)
        self.client.post(reverse("catalog:borrow_book", args=[self.book.id]))
        self.assertFalse(Loan.objects.filter(user=self.maria).exists())

    def test_nao_devolve_emprestimo_de_outra_pessoa(self):
        loan = make_loan(self.book, self.joao)
        self.client.force_login(self.maria)  # Maria tenta devolver o livro do João
        response = self.client.post(reverse("catalog:return_book", args=[loan.id]))
        self.assertEqual(response.status_code, 404)
        loan.refresh_from_db()  # relê o empréstimo do banco
        self.assertTrue(loan.is_active)  # continua ativo


class StaffViewsTests(TestCase):
    """Testes da área da equipe."""

    def setUp(self):
        self.leitor = User.objects.create_user("maria", password="senha-forte-123")
        self.equipe = User.objects.create_user("bibliotecaria", password="senha-forte-123", is_staff=True)
        self.book = Book.objects.create(title="Dom Casmurro", author="Machado de Assis", isbn="9788535910663")

    def test_leitor_comum_recebe_403(self):
        self.client.force_login(self.leitor)
        response = self.client.get(reverse("catalog:overdue_loans"))
        self.assertEqual(response.status_code, 403)  # 403 = proibido

    def test_equipe_ve_atrasados(self):
        make_loan(self.book, self.leitor, days=-3)
        self.client.force_login(self.equipe)
        response = self.client.get(reverse("catalog:overdue_loans"))
        self.assertContains(response, "Dom Casmurro")

    def test_equipe_registra_devolucao(self):
        loan = make_loan(self.book, self.leitor, days=-3)
        self.client.force_login(self.equipe)
        self.client.post(reverse("catalog:staff_mark_returned", args=[loan.id]))
        loan.refresh_from_db()
        self.assertFalse(loan.is_active)
