import threading
import unittest.mock
from datetime import timedelta
from io import StringIO

from django.contrib.auth.models import User
from django.core import mail  # caixa de saída de e-mails usada nos testes
from django.core.management import call_command
from django.db import connection
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse  # gera o endereço a partir do nome da rota (como o {% url %})
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase  # testes da API (Aula 8)

from . import services
from .models import Book, Category, Loan, Review, SearchQuery


def make_loan(book, user, days=14):
    """Atalho para criar empréstimos nos testes (days negativo = prazo já vencido)."""
    return Loan.objects.create(book=book, user=user, due_date=timezone.localdate() + timedelta(days=days))


class LoanModelTests(TestCase):
    """Testes das regras que ficam nos models."""

    def setUp(self):
        # setUp roda antes de CADA teste; o banco de testes começa vazio
        self.user = User.objects.create_user("maria", password="senha-forte-123")
        self.book = Book.objects.create(
            title="Dom Casmurro", author="Machado de Assis", isbn="9788535910663", copies_total=2
        )

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
        self.book = Book.objects.create(
            title="Dom Casmurro", author="Machado de Assis", isbn="9788535910663", copies_total=1
        )

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


class CatalogFiltersTests(TestCase):
    """Testes da Aula 4: filtros, ordenação, histórico e exportação."""

    def setUp(self):
        self.user = User.objects.create_user("maria", password="senha-forte-123")
        self.client.force_login(self.user)
        romance = Category.objects.create(name="Romance")
        tecnologia = Category.objects.create(name="Tecnologia")
        Book.objects.create(
            title="Dom Casmurro",
            author="Machado de Assis",
            isbn="1111111111111",
            category=romance,
            language="Português",
            edition_year=1899,
        )
        Book.objects.create(
            title="Python Fluente",
            author="Luciano Ramalho",
            isbn="2222222222222",
            category=tecnologia,
            language="Português",
            edition_year=2015,
        )
        Book.objects.create(
            title="Pride and Prejudice",
            author="Jane Austen",
            isbn="3333333333333",
            category=romance,
            language="Inglês",
            edition_year=1813,
        )
        self.romance = romance

    def titles(self, response):
        """Títulos que apareceram na página, na ordem em que apareceram."""
        return [book.title for book in response.context["page_obj"]]

    def test_filtro_por_categoria(self):
        response = self.client.get(reverse("catalog:book_list"), {"categoria": self.romance.id})
        self.assertEqual(self.titles(response), ["Dom Casmurro", "Pride and Prejudice"])

    def test_filtro_por_idioma_e_ano(self):
        # "português" em minúsculas: o filtro __iexact ignora maiúsculas
        response = self.client.get(reverse("catalog:book_list"), {"idioma": "português", "ano_min": "1900"})
        self.assertEqual(self.titles(response), ["Python Fluente"])

    def test_ordenar_por_edicao_mais_recente(self):
        response = self.client.get(reverse("catalog:book_list"), {"ordenar": "recent"})
        self.assertEqual(self.titles(response), ["Python Fluente", "Dom Casmurro", "Pride and Prejudice"])

    def test_busca_entra_no_historico(self):
        self.client.get(reverse("catalog:book_list"), {"q": "python"})
        busca = SearchQuery.objects.get(user=self.user)  # get falharia se não houvesse exatamente uma
        self.assertEqual(busca.q, "python")

    def test_abrir_a_lista_sem_filtros_nao_gera_historico(self):
        self.client.get(reverse("catalog:book_list"))
        self.assertEqual(SearchQuery.objects.count(), 0)

    def test_exportar_csv_respeita_os_filtros(self):
        response = self.client.get(reverse("catalog:export_books", args=["csv"]), {"q": "python"})
        conteudo = response.content.decode("utf-8")  # bytes -> texto
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("Python Fluente", conteudo)
        self.assertNotIn("Dom Casmurro", conteudo)

    def test_exportar_excel(self):
        response = self.client.get(reverse("catalog:export_books", args=["xlsx"]))
        self.assertEqual(response.status_code, 200)
        # Todo arquivo .xlsx é, por dentro, um arquivo ZIP, e arquivos ZIP começam com "PK"
        self.assertTrue(response.content.startswith(b"PK"))

    def test_sugestoes_devolvem_json(self):
        response = self.client.get(reverse("catalog:book_suggestions"), {"q": "mach"})
        self.assertEqual(response.json(), {"suggestions": ["Machado de Assis"]})


class AccountTests(TestCase):
    """Testes da Aula 5: cadastro e recuperação de senha."""

    def test_cadastro_cria_usuario_e_ja_entra(self):
        # Os nomes password1 e password2 são os campos de senha do UserCreationForm
        response = self.client.post(
            reverse("catalog:signup"),
            {
                "username": "ana",
                "email": "ana@exemplo.com",
                "password1": "uma-senha-bem-forte-42",
                "password2": "uma-senha-bem-forte-42",
            },
        )
        self.assertRedirects(response, reverse("catalog:book_list"))
        self.assertTrue(User.objects.filter(username="ana").exists())
        # Já está logada: a lista de livros abre direto (200) em vez de mandar para o login
        self.assertEqual(self.client.get(reverse("catalog:book_list")).status_code, 200)

    def test_cadastro_recusa_email_repetido(self):
        User.objects.create_user("ana", email="ana@exemplo.com", password="x")
        response = self.client.post(
            reverse("catalog:signup"),
            {
                "username": "ana2",
                "email": "ANA@exemplo.com",  # mesmo e-mail, com letras maiúsculas
                "password1": "uma-senha-bem-forte-42",
                "password2": "uma-senha-bem-forte-42",
            },
        )
        self.assertContains(response, "Já existe uma conta com este e-mail.")

    def test_recuperar_senha_envia_email(self):
        User.objects.create_user("ana", email="ana@exemplo.com", password="x")
        self.client.post(reverse("password_reset"), {"email": "ana@exemplo.com"})
        # Nos testes o Django não envia e-mails de verdade: eles ficam guardados em mail.outbox
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("ana@exemplo.com", mail.outbox[0].to)


class ReviewTests(TestCase):
    """Testes da Aula 5: página do livro e avaliações."""

    def setUp(self):
        self.maria = User.objects.create_user("maria", password="senha-forte-123")
        self.joao = User.objects.create_user("joao", password="senha-forte-123")
        self.book = Book.objects.create(title="Dom Casmurro", author="Machado de Assis", isbn="9788535910663")
        self.url = reverse("catalog:review_book", args=[self.book.id])

    def test_so_avalia_quem_ja_pegou_emprestado(self):
        self.client.force_login(self.maria)  # Maria nunca pegou o livro
        self.client.post(self.url, {"rating": 5, "comment": "Ótimo"})
        self.assertEqual(Review.objects.count(), 0)

    def test_avaliar_e_depois_editar_mantem_uma_avaliacao(self):
        make_loan(self.book, self.maria)
        self.client.force_login(self.maria)
        self.client.post(self.url, {"rating": 3, "comment": "Bom"})
        self.client.post(self.url, {"rating": 5, "comment": "Mudei de ideia: ótimo!"})
        review = Review.objects.get()  # get() sem filtro: falha se houver mais de uma avaliação
        self.assertEqual(review.rating, 5)

    def test_nota_fora_de_1_a_5_e_recusada(self):
        make_loan(self.book, self.maria)
        self.client.force_login(self.maria)
        response = self.client.post(self.url, {"rating": 9})
        self.assertEqual(response.status_code, 200)  # a página volta mostrando o erro
        self.assertEqual(Review.objects.count(), 0)

    def test_pagina_do_livro_mostra_a_media(self):
        Review.objects.create(book=self.book, user=self.maria, rating=5)
        Review.objects.create(book=self.book, user=self.joao, rating=4)
        self.client.force_login(self.maria)
        response = self.client.get(reverse("catalog:book_detail", args=[self.book.id]))
        self.assertContains(response, "4,5")  # média de 5 e 4, com vírgula (pt-br)
        self.assertContains(response, "2 avaliações")

    def test_nao_apaga_avaliacao_de_outra_pessoa(self):
        review = Review.objects.create(book=self.book, user=self.joao, rating=4)
        self.client.force_login(self.maria)
        response = self.client.post(reverse("catalog:delete_review", args=[review.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Review.objects.filter(pk=review.pk).exists())  # continua lá


class ReportTests(TestCase):
    """Testes da Aula 6: relatórios e exportação."""

    def setUp(self):
        self.equipe = User.objects.create_user("bibliotecaria", password="senha-forte-123", is_staff=True)
        self.leitor = User.objects.create_user("maria", password="senha-forte-123")
        self.popular = Book.objects.create(title="Dom Casmurro", author="Machado de Assis", isbn="1111111111111")
        self.outro = Book.objects.create(title="Iracema", author="José de Alencar", isbn="2222222222222")
        make_loan(self.popular, self.leitor, days=-5).mark_returned()  # empréstimo antigo, já devolvido
        make_loan(self.popular, self.leitor, days=-2)  # ainda com ela, e atrasado 2 dias
        make_loan(self.outro, self.leitor)  # em dia

    def test_leitor_comum_nao_ve_relatorios(self):
        self.client.force_login(self.leitor)
        response = self.client.get(reverse("catalog:reports_index"))
        self.assertEqual(response.status_code, 403)

    def test_todos_os_relatorios_abrem(self):
        from .reports import REPORTS

        self.client.force_login(self.equipe)
        for slug in REPORTS:
            # subTest: se um relatório falhar, a mensagem diz qual foi
            with self.subTest(relatorio=slug):
                response = self.client.get(reverse("catalog:report_detail", args=[slug]))
                self.assertEqual(response.status_code, 200)

    def test_livros_populares_em_ordem(self):
        from .reports import popular_books

        # Os relatórios são funções comuns: dá para testar sem passar por página nenhuma
        data = popular_books()
        self.assertEqual(data["rows"][0], ["Dom Casmurro", "Machado de Assis", 2])
        self.assertEqual(data["rows"][1], ["Iracema", "José de Alencar", 1])

    def test_relatorio_de_atrasados(self):
        from .reports import overdue_loans

        data = overdue_loans()
        self.assertEqual(len(data["rows"]), 1)
        self.assertEqual(data["rows"][0][3], 2)  # quarta coluna: 2 dias de atraso

    def test_exportar_em_todos_os_formatos(self):
        self.client.force_login(self.equipe)
        # Como cada tipo de arquivo começa: CSV com o BOM + "Livro", XLSX com "PK", PDF com "%PDF"
        inicio_esperado = {"csv": "Livro".encode("utf-8-sig"), "xlsx": b"PK", "pdf": b"%PDF"}
        for file_format, inicio in inicio_esperado.items():
            with self.subTest(formato=file_format):
                url = reverse("catalog:report_export", args=["emprestimos", file_format])
                response = self.client.get(url)
                self.assertTrue(response.content.startswith(inicio))

    def test_relatorio_inexistente_da_404(self):
        self.client.force_login(self.equipe)
        response = self.client.get(reverse("catalog:report_detail", args=["nao-existe"]))
        self.assertEqual(response.status_code, 404)


class DeployTests(TestCase):
    """Testes da Aula 7: arquivos estáticos e funcionamento com DEBUG desligado."""

    def setUp(self):
        self.user = User.objects.create_user("maria", password="senha-forte-123")
        self.book = Book.objects.create(title="Dom Casmurro", author="Machado de Assis", isbn="1111111111111")
        self.client.force_login(self.user)

    def test_css_e_js_vem_de_arquivos_estaticos(self):
        response = self.client.get(reverse("catalog:book_list"))
        self.assertContains(response, "/static/css/style.css")
        self.assertContains(response, "/static/js/theme.js")

    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_paginas_funcionam_com_debug_desligado(self):
        # Simula o servidor: DEBUG=False e apenas o endereço permitido
        for url in [
            reverse("catalog:book_list"),
            reverse("catalog:book_detail", args=[self.book.id]),
            reverse("catalog:my_loans"),
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_endereco_inexistente_da_404_sem_detalhes(self):
        response = self.client.get("/pagina-que-nao-existe/")
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, "Using the URLconf", status_code=404)  # sem a página técnica do DEBUG


class ApiTests(APITestCase):
    """Testes da Aula 8: a API REST.

    APITestCase é o TestCase do DRF: o self.client entende JSON e autenticação por token.
    """

    def setUp(self):
        self.maria = User.objects.create_user("maria", password="senha-forte-123")
        self.joao = User.objects.create_user("joao", password="senha-forte-123")
        self.equipe = User.objects.create_user("bibliotecaria", password="senha-forte-123", is_staff=True)
        self.romance = Category.objects.create(name="Romance")
        self.book = Book.objects.create(
            title="Dom Casmurro", author="Machado de Assis", isbn="1111111111111", copies_total=1, category=self.romance
        )
        Book.objects.create(title="Vidas Secas", author="Graciliano Ramos", isbn="2222222222222")

    # ---------- leitura pública ----------

    def test_lista_de_livros_e_publica_e_paginada(self):
        response = self.client.get("/api/livros/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)  # a paginação devolve o total...
        self.assertEqual(len(response.data["results"]), 2)  # ...e os itens da página em "results"

    def test_busca_na_api_usa_os_filtros_do_acervo(self):
        response = self.client.get("/api/livros/", {"q": "machado"})
        titulos = [livro["title"] for livro in response.data["results"]]
        self.assertEqual(titulos, ["Dom Casmurro"])

    def test_detalhe_do_livro(self):
        response = self.client.get(f"/api/livros/{self.book.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["category_name"], "Romance")
        self.assertEqual(response.data["available"], 1)

    def test_livro_inexistente_da_404(self):
        response = self.client.get("/api/livros/9999/")
        self.assertEqual(response.status_code, 404)

    # ---------- escrita: só a equipe ----------

    def test_visitante_nao_cadastra_livro(self):
        response = self.client.post("/api/livros/", {"title": "Novo", "author": "A", "isbn": "3333333333333"})
        self.assertEqual(response.status_code, 401)  # 401: não informou quem é

    def test_leitor_nao_cadastra_livro(self):
        self.client.force_authenticate(self.maria)
        response = self.client.post("/api/livros/", {"title": "Novo", "author": "A", "isbn": "3333333333333"})
        self.assertEqual(response.status_code, 403)  # 403: sabe quem é, mas não tem permissão

    def test_equipe_cadastra_altera_e_apaga_livro(self):
        self.client.force_authenticate(self.equipe)
        response = self.client.post(
            "/api/livros/",
            {"title": "Iracema", "author": "José de Alencar", "isbn": "3333333333333", "copies_total": 2},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        novo_id = response.data["id"]
        self.assertEqual(response.data["available"], 2)

        response = self.client.patch(f"/api/livros/{novo_id}/", {"copies_total": 4}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Book.objects.get(pk=novo_id).copies_total, 4)

        response = self.client.delete(f"/api/livros/{novo_id}/")
        self.assertEqual(response.status_code, 204)  # 204: apagado, resposta sem conteúdo
        self.assertFalse(Book.objects.filter(pk=novo_id).exists())

    def test_isbn_repetido_da_400(self):
        self.client.force_authenticate(self.equipe)
        response = self.client.post(
            "/api/livros/", {"title": "X", "author": "Y", "isbn": "1111111111111"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("isbn", response.data)  # a resposta diz qual campo está errado

    def test_nao_apaga_livro_com_historico(self):
        make_loan(self.book, self.maria)
        self.client.force_authenticate(self.equipe)
        response = self.client.delete(f"/api/livros/{self.book.id}/")
        self.assertEqual(response.status_code, 409)
        self.assertTrue(Book.objects.filter(pk=self.book.id).exists())

    # ---------- empréstimos ----------

    def test_emprestar_pela_api(self):
        self.client.force_authenticate(self.maria)
        response = self.client.post(f"/api/livros/{self.book.id}/emprestar/")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["book_title"], "Dom Casmurro")
        self.assertTrue(Loan.objects.filter(user=self.maria, book=self.book).exists())

    def test_emprestar_sem_copias_da_409(self):
        make_loan(self.book, self.joao)  # a única cópia
        self.client.force_authenticate(self.maria)
        response = self.client.post(f"/api/livros/{self.book.id}/emprestar/")
        self.assertEqual(response.status_code, 409)
        self.assertIn("Não há cópias", response.data["detail"])

    def test_emprestar_exige_autenticacao(self):
        response = self.client.post(f"/api/livros/{self.book.id}/emprestar/")
        self.assertEqual(response.status_code, 401)

    def test_cada_um_ve_so_os_proprios_emprestimos(self):
        make_loan(self.book, self.maria)
        make_loan(Book.objects.get(isbn="2222222222222"), self.joao)
        self.client.force_authenticate(self.maria)
        response = self.client.get("/api/emprestimos/")
        self.assertEqual([e["book_title"] for e in response.data["results"]], ["Dom Casmurro"])

    def test_devolver_pela_api(self):
        loan = make_loan(self.book, self.maria)
        self.client.force_authenticate(self.maria)
        response = self.client.post(f"/api/emprestimos/{loan.id}/devolver/")
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data["returned_at"])

    def test_nao_devolve_emprestimo_de_outra_pessoa(self):
        loan = make_loan(self.book, self.joao)
        self.client.force_authenticate(self.maria)
        response = self.client.post(f"/api/emprestimos/{loan.id}/devolver/")
        self.assertEqual(response.status_code, 404)

    # ---------- token e documentação ----------

    def test_token_permite_usar_a_api(self):
        response = self.client.post("/api/token/", {"username": "maria", "password": "senha-forte-123"})
        self.assertEqual(response.status_code, 200)
        token = response.data["token"]
        # Um cliente novo, sem sessão: só o token no cabeçalho Authorization
        cliente = APIClient()
        cliente.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(cliente.get("/api/emprestimos/").status_code, 200)

    def test_senha_errada_nao_gera_token(self):
        response = self.client.post("/api/token/", {"username": "maria", "password": "errada"})
        self.assertEqual(response.status_code, 400)

    def test_pagina_inicial_da_api_e_publica(self):
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("livros", response.data)  # links para os recursos

    def test_documentacao_da_api(self):
        self.assertEqual(self.client.get("/api/docs/").status_code, 200)
        self.assertEqual(self.client.get("/api/schema/").status_code, 200)


class ConcurrencyTests(TransactionTestCase):
    """Aula 9: duas pessoas tentam pegar a última cópia exatamente ao mesmo tempo."""

    def test_duas_pessoas_nao_levam_a_ultima_copia(self):
        book = Book.objects.create(
            title="Dom Casmurro", author="Machado de Assis", isbn="1111111111111", copies_total=1
        )
        maria = User.objects.create_user("maria", password="x")
        joao = User.objects.create_user("joao", password="x")

        # A "barreira" faz as duas threads esperarem uma pela outra num ponto do código:
        # logo depois de conferir as cópias e antes de gravar o empréstimo.
        barreira = threading.Barrier(2, timeout=2)
        localdate_original = timezone.localdate

        def espera_a_outra_pessoa(*args, **kwargs):
            try:
                barreira.wait()  # as duas chegam aqui depois de conferir que "há cópia"
            except threading.BrokenBarrierError:
                pass  # a outra thread não chegou (estava bloqueada esperando a primeira terminar)
            return localdate_original(*args, **kwargs)

        resultados = []

        def tentar_emprestar(usuario):
            try:
                services.borrow_book(Book.objects.get(pk=book.pk), usuario)
                resultados.append("emprestou")
            except services.LoanError:
                resultados.append("recusado")
            finally:
                connection.close()  # cada thread usa a sua própria conexão com o banco

        with unittest.mock.patch("catalog.services.timezone.localdate", side_effect=espera_a_outra_pessoa):
            threads = [threading.Thread(target=tentar_emprestar, args=(u,)) for u in (maria, joao)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

        self.assertEqual(sorted(resultados), ["emprestou", "recusado"])
        self.assertEqual(Loan.objects.filter(book=book).count(), 1)


class CoverageGapTests(TestCase):
    """Aula 9: testes que faltavam, encontrados com o relatório de cobertura."""

    def setUp(self):
        self.maria = User.objects.create_user("maria", password="senha-forte-123")
        self.book = Book.objects.create(
            title="Dom Casmurro", author="Machado de Assis", isbn="1111111111111", copies_total=2
        )

    def test_nao_empresta_o_mesmo_livro_duas_vezes(self):
        # A regra existia desde a Aula 2, mas nenhum teste passava por ela
        services.borrow_book(self.book, self.maria)
        with self.assertRaisesMessage(services.LoanError, "Você já está com"):
            services.borrow_book(self.book, self.maria)
        self.assertEqual(Loan.objects.filter(user=self.maria).count(), 1)

    def test_comando_popular_acervo_nao_duplica(self):
        # call_command roda um comando do manage.py dentro do teste; StringIO guarda o que ele imprimiria
        call_command("popular_acervo", stdout=StringIO())
        call_command("popular_acervo", stdout=StringIO())  # rodar de novo não pode duplicar nada
        self.assertEqual(Book.objects.filter(isbn__startswith="9780000").count(), 27)
        self.assertEqual(Category.objects.count(), 5)

    def test_acao_do_admin_marca_como_devolvido(self):
        loan = make_loan(self.book, self.maria)
        admin = User.objects.create_superuser("admin", password="senha-forte-123")
        self.client.force_login(admin)
        # O formulário de ações do Admin envia o nome da ação e os ids marcados na lista
        self.client.post(
            reverse("admin:catalog_loan_changelist"),
            {"action": "marcar_como_devolvido", "_selected_action": [loan.id]},
        )
        loan.refresh_from_db()
        self.assertFalse(loan.is_active)
