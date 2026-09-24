from django.core.management.base import BaseCommand  # classe base de todo comando do manage.py

from catalog.models import Book, Category

# Dados de exemplo. Cada tupla: (título, autor, categoria, ano, idioma, cópias)
LIVROS = [
    ("Dom Casmurro", "Machado de Assis", "Romance", 1899, "Português", 3),
    ("Memórias Póstumas de Brás Cubas", "Machado de Assis", "Romance", 1881, "Português", 2),
    ("O Cortiço", "Aluísio Azevedo", "Romance", 1890, "Português", 2),
    ("Iracema", "José de Alencar", "Romance", 1865, "Português", 1),
    ("Capitães da Areia", "Jorge Amado", "Romance", 1937, "Português", 2),
    ("Vidas Secas", "Graciliano Ramos", "Romance", 1938, "Português", 2),
    ("A Hora da Estrela", "Clarice Lispector", "Romance", 1977, "Português", 1),
    ("Pride and Prejudice", "Jane Austen", "Romance", 1813, "Inglês", 1),
    ("Cien años de soledad", "Gabriel García Márquez", "Romance", 1967, "Espanhol", 1),
    ("1984", "George Orwell", "Ficção científica", 1949, "Português", 3),
    ("Admirável Mundo Novo", "Aldous Huxley", "Ficção científica", 1932, "Português", 2),
    ("Fahrenheit 451", "Ray Bradbury", "Ficção científica", 1953, "Português", 1),
    ("Duna", "Frank Herbert", "Ficção científica", 1965, "Português", 2),
    ("Eu, Robô", "Isaac Asimov", "Ficção científica", 1950, "Português", 1),
    ("Python Fluente", "Luciano Ramalho", "Tecnologia", 2015, "Português", 2),
    ("Código Limpo", "Robert C. Martin", "Tecnologia", 2008, "Português", 2),
    ("Entendendo Algoritmos", "Aditya Bhargava", "Tecnologia", 2016, "Português", 3),
    ("Pense em Python", "Allen B. Downey", "Tecnologia", 2012, "Português", 2),
    ("Automate the Boring Stuff with Python", "Al Sweigart", "Tecnologia", 2015, "Inglês", 1),
    ("Sapiens", "Yuval Noah Harari", "História", 2011, "Português", 2),
    ("O Povo Brasileiro", "Darcy Ribeiro", "História", 1995, "Português", 1),
    ("Raízes do Brasil", "Sérgio Buarque de Holanda", "História", 1936, "Português", 1),
    ("Casa-Grande & Senzala", "Gilberto Freyre", "História", 1933, "Português", 1),
    ("Reinações de Narizinho", "Monteiro Lobato", "Infantojuvenil", 1931, "Português", 2),
    ("Harry Potter e a Pedra Filosofal", "J. K. Rowling", "Infantojuvenil", 1997, "Português", 3),
    ("O Hobbit", "J. R. R. Tolkien", "Infantojuvenil", 1937, "Português", 2),
    ("Le Petit Prince", "Antoine de Saint-Exupéry", "Infantojuvenil", 1943, "Francês", 1),
]


class Command(BaseCommand):
    # Texto mostrado em: python manage.py help popular_acervo
    help = "Cadastra categorias e livros de exemplo (pode rodar várias vezes sem duplicar)."

    def handle(self, *args, **options):
        """Método chamado pelo Django quando o comando é executado."""
        # enumerate numera os livros a partir de 1; a tupla é desempacotada direto no for
        for numero, (titulo, autor, categoria, ano, idioma, copias) in enumerate(LIVROS, start=1):
            # Busca a categoria pelo nome ou cria se ainda não existir.
            # get_or_create devolve (objeto, criou?); o _ indica que não usaremos o segundo valor.
            cat, _ = Category.objects.get_or_create(name=categoria)

            # ISBN fictício, só para testes: 978 + número com 10 dígitos (9780000000001, ...)
            isbn = f"978{numero:010d}"

            # Procura o livro pelo ISBN: se existir, atualiza com os "defaults"; se não, cria.
            # Por isso o comando pode rodar várias vezes sem duplicar nada.
            _, criado = Book.objects.update_or_create(
                isbn=isbn,
                defaults={
                    "title": titulo,
                    "author": autor,
                    "category": cat,
                    "edition_year": ano,
                    "language": idioma,
                    "copies_total": copias,
                },
            )
            acao = "criado" if criado else "atualizado"
            self.stdout.write(f"{acao}: {titulo}")  # escreve no terminal

        # style.SUCCESS pinta a mensagem de verde no terminal
        self.stdout.write(self.style.SUCCESS(f"Pronto! {len(LIVROS)} livros no acervo de exemplo."))
