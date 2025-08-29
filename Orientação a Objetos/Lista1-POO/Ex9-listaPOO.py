# ===== CLASSE BASE: Participante =====
class Participante:
    def __init__(self, nome, email):
        self.nome = nome    # atributo comum a todos os participantes
        self.email = email  # atributo comum a todos os participantes

    def emitirCertificado(self):
        # Método genérico. Vai ser reescrito pelas classes filhas (polimorfismo)
        return f"Certificado emitido para {self.nome} (Participante genérico)."


# ===== SUBCLASSE: Aluno =====
class Aluno(Participante):
    def __init__(self, nome, email, curso):
        super().__init__(nome, email)  # chama o construtor da classe base
        self.curso = curso             # atributo exclusivo da classe Aluno

    def emitirCertificado(self):
        # Polimorfismo: substitui o comportamento do método da classe base
        return f"Certificado de conclusão emitido para {self.nome} no curso de {self.curso}."


# ===== SUBCLASSE: Instrutor =====
class Instrutor(Participante):
    def __init__(self, nome, email, especialidade):
        super().__init__(nome, email)      # chama o construtor da classe base
        self.especialidade = especialidade  # atributo exclusivo do Instrutor

    def emitirCertificado(self):
        # Polimorfismo: comportamento personalizado para Instrutor
        return f"Certificado de participação emitido para o instrutor {self.nome} (especialidade: {self.especialidade})."


# ===== LISTA QUE ARMAZENA TODOS OS PARTICIPANTES =====
participantes = []  # essa lista pode guardar objetos Aluno ou Instrutor


# ===== MENU INTERATIVO =====
def menu():
    while True:
        print("\n=== MENU PLATAFORMA DE CURSOS ===")
        print("1. Cadastrar participante")
        print("2. Listar participantes")
        print("3. Emitir certificados")
        print("0. Sair")

        opcao = input("Escolha uma opção: ")

        # Opção 1: Cadastrar novo participante (aluno ou instrutor)
        if opcao == "1":
            print("\nTipo de participante:")
            print("1. Aluno")
            print("2. Instrutor")
            tipo = input("Digite o tipo (1 ou 2): ")

            nome = input("Nome: ")
            email = input("E-mail: ")

            if tipo == "1":
                curso = input("Curso: ")
                aluno = Aluno(nome, email, curso)  # cria objeto Aluno
                participantes.append(aluno)        # adiciona à lista
                print("Aluno cadastrado com sucesso!")

            elif tipo == "2":
                especialidade = input("Especialidade: ")
                instrutor = Instrutor(nome, email, especialidade)  # cria objeto Instrutor
                participantes.append(instrutor)                    # adiciona à lista
                print("Instrutor cadastrado com sucesso!")

            else:
                print("Tipo inválido. Escolha 1 ou 2.")

        # Opção 2: Listar todos os participantes cadastrados
        elif opcao == "2":
            if not participantes:
                print("Nenhum participante cadastrado.")
            else:
                print("\n--- LISTA DE PARTICIPANTES ---")
                for i, p in enumerate(participantes, 1):
                    # usamos isinstance para identificar se é Aluno ou Instrutor
                    tipo = "Aluno" if isinstance(p, Aluno) else "Instrutor"
                    print(f"{i}. {p.nome} ({tipo}) - {p.email}")

        # Opção 3: Emitir os certificados de todos os participantes
        elif opcao == "3":
            if not participantes:
                print("Nenhum participante cadastrado.")
            else:
                print("\n--- EMISSÃO DE CERTIFICADOS ---")
                for p in participantes:
                    # Aqui ocorre o POLIMORFISMO: cada objeto usa sua própria versão de emitirCertificado()
                    print(p.emitirCertificado())

        # Opção 0: Sair do programa
        elif opcao == "0":
            print("Encerrando o programa... Até logo!")
            break

        # Opção inválida
        else:
            print("Opção inválida. Tente novamente.")


# ===== EXECUTANDO O PROGRAMA PRINCIPAL =====
if __name__ == "__main__":
    menu()  # inicia o menu interativo
