class Contato:
    def __init__(self, nome, telefone, email):
        self.nome = nome
        self.telefone = telefone
        self.email = email

    def __str__(self):
        return f"{self.nome} | {self.telefone} | {self.email}"


class Agenda:
    def __init__(self):
        # A lista pertence à agenda e armazena objetos Contato.
        self.contatos = []

    def adicionar_contato(self, contato):
        self.contatos.append(contato)
        print("Contato adicionado.")

    def listar_contatos(self):
        if not self.contatos:
            print("Agenda vazia.")
            return
        for contato in self.contatos:
            print(contato)

    def buscar_contato(self, nome):
        for contato in self.contatos:
            if contato.nome.lower() == nome.lower():
                return contato
        return None


def menu():
    agenda = Agenda()

    while True:
        print("\n1. Adicionar contato")
        print("2. Listar contatos")
        print("3. Buscar contato")
        print("4. Sair")
        opcao = input("Escolha: ")

        if opcao == "1":
            contato = Contato(
                input("Nome: "),
                input("Telefone: "),
                input("E-mail: ")
            )
            agenda.adicionar_contato(contato)
        elif opcao == "2":
            agenda.listar_contatos()
        elif opcao == "3":
            contato = agenda.buscar_contato(input("Nome: "))
            print(contato if contato else "Contato não encontrado.")
        elif opcao == "4":
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()
