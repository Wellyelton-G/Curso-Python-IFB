# ================= Classes =================

class Autor:
    def __init__(self, nome, nacionalidade):
        self.nome = nome
        self.nacionalidade = nacionalidade

    def __str__(self):
        return f"{self.nome} ({self.nacionalidade})"


class Livro:
    def __init__(self, titulo, ano, autor: Autor):
        self.titulo = titulo
        self.ano = ano
        self.autor = autor

    def __str__(self):
        return f"'{self.titulo}' ({self.ano}) - {self.autor}"


class Biblioteca:
    def __init__(self, nome):
        self.nome = nome
        self.livros = []

    def criar_livro(self, titulo, ano, autor: Autor):
        livro = Livro(titulo, ano, autor)
        self.livros.append(livro)
        print(f"Livro '{titulo}' adicionado com sucesso!")
        return livro

    def listar_livros(self):
        if not self.livros:
            print("Nenhum livro disponível na biblioteca.")
        else:
            print(f"\nLivros disponíveis na {self.nome}:")
            for i, livro in enumerate(self.livros, 1):
                print(f"{i}. {livro}")


class Usuario:
    def __init__(self, nome, biblioteca: Biblioteca):
        self.nome = nome
        self.biblioteca = biblioteca

    def pegar_emprestado(self):
        if not self.biblioteca.livros:
            print("Não há livros disponíveis para empréstimo.")
            return
        print("\nSelecione o livro que deseja pegar emprestado:")
        for i, livro in enumerate(self.biblioteca.livros, 1):
            print(f"{i}. {livro}")
        try:
            escolha = int(input("Digite o número do livro: "))
            if 1 <= escolha <= len(self.biblioteca.livros):
                livro = self.biblioteca.livros[escolha - 1]
                print(f"{self.nome} pegou o livro '{livro.titulo}' emprestado.\n")
            else:
                print("Escolha inválida.")
        except ValueError:
            print("Entrada inválida. Digite um número.")

# ================= Programa Interativo =================

def menu():
    print("\n=== Sistema da Biblioteca ===")
    print("1. Listar livros disponíveis")
    print("2. Adicionar livro")
    print("3. Pegar livro emprestado")
    print("4. Sair")
    return input("Escolha uma opção: ")

# Criando biblioteca
biblioteca = Biblioteca("Biblioteca Central")

# Criando usuário
nome_usuario = input("Digite seu nome: ")
usuario = Usuario(nome_usuario, biblioteca)

# Loop principal
while True:
    opcao = menu()
    if opcao == "1":
        biblioteca.listar_livros()
    elif opcao == "2":
        titulo = input("Digite o título do livro: ")
        ano = input("Digite o ano do livro: ")
        nome_autor = input("Digite o nome do autor: ")
        nacionalidade_autor = input("Digite a nacionalidade do autor: ")
        autor = Autor(nome_autor, nacionalidade_autor)
        biblioteca.criar_livro(titulo, ano, autor)
    elif opcao == "3":
        usuario.pegar_emprestado()
    elif opcao == "4":
        print("Encerrando o sistema. Até logo!")
        break
    else:
        print("Opção inválida. Tente novamente.")
