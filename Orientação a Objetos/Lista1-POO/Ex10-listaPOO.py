# ===== Classe base: Personagem =====
class Personagem:
    def __init__(self, nome, constelacao):
        self.nome = nome
        self.constelacao = constelacao

    def apresentar(self):
        # Método comum a todos os personagens
        print(f"Eu sou {self.nome}, da constelação de {self.constelacao}!")


# ===== Classe auxiliar: Cavaleiro de Bronze =====
class CavaleiroDeBronze:
    def __init__(self, poder_de_luta):
        self.poder_de_luta = poder_de_luta

    def golpe_especial(self):
        # Método exclusivo dos Cavaleiros de Bronze
        print(f"Executando o golpe especial com poder de luta {self.poder_de_luta}!")


# ===== Classe auxiliar: Cavaleiro de Ouro =====
class CavaleiroDeOuro:
    def __init__(self, casa_do_zodiaco):
        self.casa_do_zodiaco = casa_do_zodiaco

    def defender_casa(self):
        # Método exclusivo dos Cavaleiros de Ouro
        print(f"Defendendo a casa de {self.casa_do_zodiaco} com honra!")


# ===== Classe principal: Cavaleiro Híbrido =====
# Essa classe herda de Personagem, CavaleiroDeBronze e CavaleiroDeOuro
# Exemplo de HERANÇA MÚLTIPLA
class CavaleiroHibrido(Personagem, CavaleiroDeBronze, CavaleiroDeOuro):
    def __init__(self, nome, constelacao, poder_de_luta, casa_do_zodiaco):
        # Chamando os construtores das superclasses individualmente
        Personagem.__init__(self, nome, constelacao)
        CavaleiroDeBronze.__init__(self, poder_de_luta)
        CavaleiroDeOuro.__init__(self, casa_do_zodiaco)

    def agir(self):
        # Método que demonstra POLIMORFISMO:
        # Combina os comportamentos das classes herdadas
        self.apresentar()         # método da classe Personagem
        self.golpe_especial()     # método da classe CavaleiroDeBronze
        self.defender_casa()      # método da classe CavaleiroDeOuro


# ===== Lista que armazena os cavaleiros criados =====
personagens = []  # Lista com objetos da classe CavaleiroHibrido


# ===== Menu interativo =====
def menu():
    while True:
        # Apresentação do menu principal
        print("\n=== CAVALEIROS DO ZODÍACO ===")
        print("1. Cadastrar Cavaleiro Híbrido")
        print("2. Listar Cavaleiros")
        print("3. Executar Golpes Especiais e Defesas")
        print("0. Sair")

        opcao = input("Escolha uma opção: ")

        # Opção 1: Cadastrar novo cavaleiro
        if opcao == "1":
            nome = input("Nome do cavaleiro: ")
            constelacao = input("Constelação: ")
            poder = int(input("Poder de luta: "))
            casa = input("Casa do Zodíaco: ")

            # Cria objeto do tipo CavaleiroHibrido e adiciona à lista
            hibrido = CavaleiroHibrido(nome, constelacao, poder, casa)
            personagens.append(hibrido)
            print(f"Cavaleiro {nome} cadastrado com sucesso!")

        # Opção 2: Mostrar todos os cavaleiros cadastrados
        elif opcao == "2":
            if not personagens:
                print("Nenhum cavaleiro cadastrado ainda.")
            else:
                print("\n--- LISTA DE CAVALEIROS ---")
                for i, p in enumerate(personagens, 1):
                    print(f"{i}. {p.nome} - {p.constelacao} - Casa de {p.casa_do_zodiaco} - Poder: {p.poder_de_luta}")

        # Opção 3: Executar ações dos cavaleiros
        elif opcao == "3":
            if not personagens:
                print("Nenhum cavaleiro para executar ações.")
            else:
                print("\n--- AÇÕES DOS CAVALEIROS ---")
                for p in personagens:
                    p.agir()  # Polimorfismo: cada cavaleiro realiza suas ações combinadas

        # Opção 0: Encerrar o programa
        elif opcao == "0":
            print("Saindo... Até mais, cavaleiro!")
            break

        # Opção inválida
        else:
            print("Opção inválida. Tente novamente.")


# ===== Execução do programa principal =====
if __name__ == "__main__":
    menu()  # chama o menu interativo ao iniciar o script
