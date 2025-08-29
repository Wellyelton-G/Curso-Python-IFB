# Importa ferramentas para definir classes abstratas
from abc import ABC, abstractmethod

# ===== CLASSE ABSTRATA BASE: Lutador =====
class Lutador(ABC):
    # Método abstrato: todas as subclasses DEVEM implementar
    @abstractmethod
    def get_nome(self):
        pass

    @abstractmethod
    def get_poder(self):
        pass

    @abstractmethod
    def atacar(self):
        pass

# ===== SUBCLASSE: Saiyajin =====
class Saiyajin(Lutador):
    # Construtor que recebe nome e poder
    def __init__(self, nome, poder):
        if not nome.strip():
            raise ValueError(" O nome do Saiyajin não pode estar vazio.") #validação simples do nome do lutador. strip() remove espaços em branco do início e fim. O raise é usado para lançar (forçar) um erro de forma controlada. O ValueError é um tipo padrão de erro usado quando um valor passado é inválido para determinada operação.
        if poder <= 0:
            raise ValueError(" O nível de poder deve ser positivo.")
        self.nome = nome
        self.poder = poder

    # Retorna o nome do lutador
    def get_nome(self):
        return self.nome

    # Retorna o poder do lutador
    def get_poder(self):
        return self.poder

    # Comportamento específico do ataque de um Saiyajin
    def atacar(self):
        print(f"{self.nome} grita 'Kamehamehaaaaa!' e ataca com poder {self.poder}!")


# ===== SUBCLASSE: Androide =====
class Androide(Lutador):
    def __init__(self, nome, poder):
        if not nome.strip():
            raise ValueError(" O nome do Androide não pode estar vazio.")
        if poder <= 0:
            raise ValueError(" O nível de poder deve ser positivo.")
        self.nome = nome
        self.poder = poder

    def get_nome(self):
        return self.nome

    def get_poder(self):
        return self.poder

    def atacar(self):
        print(f"{self.nome} lança um ataque de energia robótico com força {self.poder}!")


# ===== SUBCLASSE: Namekuseijin =====
class Namekuseijin(Lutador):
    def __init__(self, nome, poder):
        if not nome.strip():
            raise ValueError(" O nome do Namekuseijin não pode estar vazio.")
        if poder <= 0:
            raise ValueError(" O nível de poder deve ser positivo.")
        self.nome = nome
        self.poder = poder

    def get_nome(self):
        return self.nome

    def get_poder(self):
        return self.poder

    def atacar(self):
        print(f"{self.nome} estica o braço e desfere um golpe elástico de poder {self.poder}!")


# Lista global que guarda todos os lutadores cadastrados
lutadores = []


# ===== MENU INTERATIVO PARA USUÁRIO =====
def menu():
    while True:
        # Exibe as opções
        print("\n=== TORNEIO DE ARTES MARCIAIS - DRAGON BALL ===")
        print("1. Cadastrar Lutador")
        print("2. Listar Lutadores")
        print("3. Simular Ataques")
        print("0. Sair")

        # Recebe a escolha do usuário
        opcao = input("Escolha uma opção: ").strip()

        # === CADASTRO DE NOVO LUTADOR ===
        if opcao == "1":
            print("\n[1] Saiyajin  [2] Androide  [3] Namekuseijin")
            tipo = input("Escolha a raça do lutador: ").strip()

            nome = input("Nome do lutador: ").strip()

            # Valida se o poder é um número inteiro
            try:
                poder = int(input("Nível de poder (valor inteiro positivo): "))
            except ValueError:
                print(" Valor inválido! O poder deve ser um número inteiro.")
                continue

            # Cria o objeto conforme a raça escolhida
            try:
                if tipo == "1":
                    lutador = Saiyajin(nome, poder)
                elif tipo == "2":
                    lutador = Androide(nome, poder)
                elif tipo == "3":
                    lutador = Namekuseijin(nome, poder)
                else:
                    print(" Raça inválida! Escolha 1, 2 ou 3.")
                    continue

                # Adiciona à lista de lutadores
                lutadores.append(lutador)
                print(f"{nome} foi inscrito no torneio!")

            except ValueError as e:
                # Mostra a mensagem de erro definida nas classes
                print(e)

        # === LISTAGEM DOS LUTADORES CADASTRADOS ===
        elif opcao == "2":
            if not lutadores:
                print(" Nenhum lutador cadastrado.")
            else:
                print("\n--- LUTADORES INSCRITOS ---")
                for i, l in enumerate(lutadores, 1):
                    print(f"{i}. {l.get_nome()} - Poder: {l.get_poder()}")

        # === SIMULAÇÃO DE ATAQUES COM POLIMORFISMO ===
        elif opcao == "3":
            if not lutadores:
                print(" Nenhum lutador para atacar.")
            else:
                print("\n--- SIMULAÇÃO DE ATAQUES ---")
                for l in lutadores:
                    l.atacar()  # Aqui o polimorfismo acontece

        # === SAIR DO PROGRAMA ===
        elif opcao == "0":
            print(" Encerrando o torneio. Até a próxima batalha!")
            break

        # === OPÇÃO INVÁLIDA ===
        else:
            print(" Opção inválida. Tente novamente.")


# ===== PONTO DE ENTRADA DO PROGRAMA =====
if __name__ == "__main__":
    menu()
