from typing import List, Optional

# =========================
# Classe Livro
# =========================
class Livro:
    """
    Representa um livro de biblioteca.
    """

    def __init__(self, titulo: str, autor: str, livro_id: int):
        # Atributos privados (não acessíveis diretamente de fora)
        self.__titulo = titulo
        self.__autor = autor
        self.__id = livro_id
        self.__disponivel = True  # True se o livro está disponível para empréstimo

    # ---- GETTERS (acessam atributos privados) ----
    def get_titulo(self) -> str:
        """Retorna o título do livro."""
        return self.__titulo

    def get_autor(self) -> str:
        """Retorna o autor do livro."""
        return self.__autor

    def get_id(self) -> int:
        """Retorna o ID do livro."""
        return self.__id

    def is_disponivel(self) -> bool:
        """Retorna True se o livro está disponível para empréstimo."""
        return self.__disponivel

    # ---- SETTERS (alteram atributos privados) ----
    def set_titulo(self, novo_titulo: str) -> None:
        """Altera o título do livro."""
        if not novo_titulo:
            raise ValueError("Título não pode ser vazio.")
        self.__titulo = novo_titulo

    def set_autor(self, novo_autor: str) -> None:
        """Altera o autor do livro."""
        if not novo_autor:
            raise ValueError("Autor não pode ser vazio.")
        self.__autor = novo_autor

    # ID geralmente não muda, então não há setter para ID

    # ---- MÉTODOS INTERNOS (encapsulados) ----
    def _marcar_emprestado(self) -> None:
        """Marca o livro como emprestado (uso interno)."""
        if not self.__disponivel:
            raise RuntimeError("Livro já está emprestado.")
        self.__disponivel = False

    def _marcar_devolvido(self) -> None:
        """Marca o livro como devolvido (uso interno)."""
        if self.__disponivel:
            raise RuntimeError("Livro já está disponível.")
        self.__disponivel = True

    def __repr__(self) -> str:
        status = "disponível" if self.__disponivel else "emprestado"
        return f"<Livro {self.__id}: '{self.__titulo}' ({self.__autor}) - {status}>"


# =========================
# Classe Usuario
# =========================
class Usuario:
    """
    Representa um usuário da biblioteca.
    """

    def __init__(self, nome: str, matricula: str):
        self.nome = nome                 # Público: pode ser acessado diretamente
        self.__matricula = matricula     # Privado: acesso controlado
        self.__emprestados: List[Livro] = []  # Lista de livros emprestados

    # ---- GETTERS / SETTERS (encapsulamento da matrícula) ----
    def get_matricula(self) -> str:
        """Retorna a matrícula do usuário."""
        return self.__matricula

    def set_matricula(self, nova_matricula: str) -> None:
        """Altera a matrícula do usuário."""
        if not nova_matricula:
            raise ValueError("Matrícula não pode ser vazia.")
        self.__matricula = nova_matricula

    # ---- OPERAÇÕES DE EMPRÉSTIMO/DEVOLUÇÃO ----
    def emprestar(self, livro: Livro) -> None:
        """
        Realiza o empréstimo de um livro, se ele estiver disponível.
        """
        if not livro.is_disponivel():
            raise RuntimeError("Não é possível emprestar: livro indisponível.")
        livro._marcar_emprestado()  # Marca o livro como emprestado
        self.__emprestados.append(livro)

    def devolver(self, livro_id: int) -> None:
        """
        Devolve um livro pelo ID, se ele estiver com o usuário.
        """
        livro = self._buscar_livro_emp(livro_id)
        if livro is None:
            raise LookupError("Este usuário não possui um livro com esse ID.")
        livro._marcar_devolvido()
        self.__emprestados.remove(livro)

    # ---- CONSULTAS ----
    def listar_emprestimos(self) -> List[Livro]:
        """
        Retorna uma lista dos livros atualmente emprestados pelo usuário.
        """
        # Retorna uma cópia para evitar alterações externas
        return list(self.__emprestados)

    def _buscar_livro_emp(self, livro_id: int) -> Optional[Livro]:
        """
        Busca um livro emprestado pelo ID.
        """
        for l in self.__emprestados:
            if l.get_id() == livro_id:
                return l
        return None

    def __repr__(self) -> str:
        return f"<Usuario {self.nome} (matrícula protegida) - {len(self.__emprestados)} livro(s)>"


# =========================
# Exemplo de uso didático
# =========================
if __name__ == "__main__":
    print("=== Exemplo de uso do sistema de biblioteca ===\n")

    # Criação de livros (IDs únicos)
    l1 = Livro("O Programador Pragmático", "Andrew Hunt e David Thomas", 101)
    l2 = Livro("Clean Code", "Robert C. Martin", 102)

    # Criação de usuário
    u = Usuario("Ana Silva", "IFB2025-0001")

    # Empréstimo de livro
    print(f"{u.nome} vai emprestar o livro: {l1.get_titulo()}")
    u.emprestar(livro=l1)
    print("Livros emprestados:", u.listar_emprestimos())  # Mostra livros emprestados

    # Tentativa de emprestar um livro já emprestado -> erro
    print("\nTentando emprestar o mesmo livro novamente...")
    try:
        u.emprestar(livro=l1)
    except RuntimeError as e:
        print("Aviso:", e)

    # Devolução de livro
    print("\nDevolvendo o livro...")
    u.devolver(livro_id=101)
    print("Situação do livro após devolução:", l1)  # Agora disponível novamente

    # Testando getters/setters
    print("\nMatrícula atual:", u.get_matricula())
    u.set_matricula("IFB2025-0099")
    print("Matrícula alterada:", u.get_matricula())

    # Atualizando dados do livro via setters
    print("\nAtualizando título do livro 2...")
    l2.set_titulo("Clean Code (2ª ed.)")
    print("Livro atualizado:", l2)

    print("\n=== Fim do exemplo didático ===")

def menu():
    print("\n=== Sistema de Biblioteca ===")
    print("1 - Cadastrar livro")
    print("2 - Consultar livros cadastrados")
    print("3 - Cadastrar usuário")
    print("4 - Realizar empréstimo")
    print("5 - Devolver livro")
    print("6 - Listar usuários e seus empréstimos")
    print("0 - Sair")
    return input("Escolha uma opção: ")

if __name__ == "__main__":
    biblioteca = Biblioteca()
    usuarios: List[Usuario] = []

    while True:
        opcao = menu()
        if opcao == "1":
            print("\n--- Cadastro de Livro ---")
            try:
                titulo = input("Título: ").strip()
                autor = input("Autor: ").strip()
                livro_id = int(input("ID do livro (número): "))
                biblioteca.cadastrar_livro(titulo, autor, livro_id)
            except Exception as e:
                print("Erro:", e)
        elif opcao == "2":
            print("\n--- Livros Cadastrados ---")
            biblioteca.consultar_livros()
        elif opcao == "3":
            print("\n--- Cadastro de Usuário ---")
            nome = input("Nome do usuário: ").strip()
            matricula = input("Matrícula: ").strip()
            usuarios.append(Usuario(nome, matricula))
            print("Usuário cadastrado com sucesso!")
        elif opcao == "4":
            print("\n--- Empréstimo de Livro ---")
            if not usuarios:
                print("Nenhum usuário cadastrado.")
                continue
            if not biblioteca.livros:
                print("Nenhum livro cadastrado.")
                continue
            matricula = input("Matrícula do usuário: ").strip()
            usuario = next((u for u in usuarios if u.get_matricula() == matricula), None)
            if not usuario:
                print("Usuário não encontrado.")
                continue
            try:
                livro_id = int(input("ID do livro para empréstimo: "))
                livro = biblioteca.buscar_livro_por_id(livro_id)
                if not livro:
                    print("Livro não encontrado.")
                else:
                    usuario.emprestar(livro)
                    print("Empréstimo realizado com sucesso!")
            except Exception as e:
                print("Erro:", e)
        elif opcao == "5":
            print("\n--- Devolução de Livro ---")
            if not usuarios:
                print("Nenhum usuário cadastrado.")
                continue
            matricula = input("Matrícula do usuário: ").strip()
            usuario = next((u for u in usuarios if u.get_matricula() == matricula), None)
            if not usuario:
                print("Usuário não encontrado.")
                continue
            try:
                livro_id = int(input("ID do livro para devolução: "))
                usuario.devolver(livro_id)
                print("Livro devolvido com sucesso!")
            except Exception as e:
                print("Erro:", e)
        elif opcao == "6":
            print("\n--- Usuários e seus empréstimos ---")
            if not usuarios:
                print("Nenhum usuário cadastrado.")
            for u in usuarios:
                print(f"\nUsuário: {u.nome} (Matrícula: {u.get_matricula()})")
                emprestimos = u.listar_emprestimos()
                if not emprestimos:
                    print("  Nenhum livro emprestado.")
                else:
                    for livro in emprestimos:
                        print(" ", livro)
        elif opcao == "0":
            print("Saindo do sistema. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")