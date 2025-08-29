# ================== CLASSE CASA ==================
class Casa:
    # Classe interna Comodo só existe dentro da Casa
    # Isso representa a COMPOSIÇÃO: o Cômodo depende da Casa para existir
    class Comodo:  
        def __init__(self, nome, area):
            self.__nome = nome   # nome do cômodo (privado)
            self.__area = area   # área do cômodo em m² (privado)

        # Getter para o nome do cômodo
        def get_nome(self): #serve para acessar o atributo privado nome
            return self.__nome

        # Getter para a área do cômodo
        def get_area(self):
            return self.__area

    # Construtor da Casa
    def __init__(self, endereco):
        self.__endereco = endereco         # endereço da casa
        self.__comodos = []                # lista que guarda objetos Comodo

    # Getter para endereço
    def get_endereco(self):
        return self.__endereco

    # Método para adicionar um cômodo à casa
    # Aqui criamos o objeto Comodo dentro da Casa (não de fora)
    def adicionar_comodo(self, nome, area):
        comodo = Casa.Comodo(nome, area)   # cria um objeto Comodo
        self.__comodos.append(comodo)      # adiciona na lista de cômodos

    # Método para listar todos os cômodos da casa
    def listar_comodos(self):
        if not self.__comodos:  # verifica se a lista está vazia
            print("A casa ainda não tem cômodos.")
        else:
            print(f"\n--- Cômodos da Casa ({self.__endereco}) ---")
            for c in self.__comodos:
                print(f"{c.get_nome()} - {c.get_area()} m²")

    # Método para calcular a área total da casa
    def calcular_area_total(self):
        # soma a área de todos os cômodos usando list comprehension
        return sum([c.get_area() for c in self.__comodos])


# ================== PROGRAMA PRINCIPAL ==================
if __name__ == "__main__":
    casa = None  # ainda não temos uma casa criada

    while True:
        # Menu interativo
        print("\n=== MENU CASA ===")
        print("1. Criar casa")
        print("2. Adicionar cômodo")
        print("3. Listar cômodos")
        print("4. Calcular área total")
        print("5. Sair")

        opcao = input("Escolha uma opção: ")

        # Criar casa
        if opcao == "1":
            endereco = input("Digite o endereço da casa: ")
            casa = Casa(endereco)  # cria um objeto da classe Casa
            print("Casa criada com sucesso!")

        # Adicionar cômodo
        elif opcao == "2":
            if casa is None:  # verifica se já existe uma casa
                print("Crie uma casa primeiro!")
            else:
                nome = input("Nome do cômodo (ex: sala, cozinha): ")
                area = float(input("Área do cômodo (em m²): "))
                casa.adicionar_comodo(nome, area)  # chama o método da Casa
                print(f"Cômodo '{nome}' adicionado com sucesso!")

        # Listar cômodos
        elif opcao == "3":
            if casa is None:
                print("Crie uma casa primeiro!")
            else:
                casa.listar_comodos()

        # Calcular área total
        elif opcao == "4":
            if casa is None:
                print("Crie uma casa primeiro!")
            else:
                print(f"Área total da casa: {casa.calcular_area_total()} m²")

        # Encerrar programa
        elif opcao == "5":
            print("Encerrando o programa... Até logo!")
            break

        # Tratamento de opção inválida
        else:
            print("Opção inválida, tente novamente!")
