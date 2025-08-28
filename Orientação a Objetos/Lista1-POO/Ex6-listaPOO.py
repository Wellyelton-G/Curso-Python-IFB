class Funcionario:
    def __init__(self, nome, salario):
        self.__nome = nome          # atributo privado
        self.__salario = salario    # atributo privado

    # Métodos públicos (getters)
    def get_nome(self):
        return self.__nome

    def get_salario(self):
        return self.__salario


class Departamento:
    def __init__(self, nome):
        self.__nome = nome
        self.__funcionarios = []  # lista de objetos Funcionario (agregação)

    def get_nome(self):
        return self.__nome

    # Método público para adicionar funcionário
    def adicionar_funcionario(self, funcionario):
        self.__funcionarios.append(funcionario)
        #.append adiciona um item ao final da lista.

    # Método público para listar funcionários
    def listar_funcionarios(self):
        if not self.__funcionarios:
            print(f"Departamento {self.__nome} não tem funcionários.")
        else:
            print(f"\n--- Funcionários do Departamento {self.__nome} ---")
            for f in self.__funcionarios:
                print(f"{f.get_nome()} - R${f.get_salario():.2f}")

    # Método público para calcular média salarial
    def media_salarial(self):
        if not self.__funcionarios:
            return 0
        total = sum([f.get_salario() for f in self.__funcionarios])
        return total / len(self.__funcionarios)


# ================= PROGRAMA PRINCIPAL =================
if __name__ == "__main__":
    funcionarios = []   # lista de funcionários independentes
    departamentos = []  # lista de departamentos

    while True:
        print("\n=== MENU ===")
        print("1. Criar funcionário")
        print("2. Criar departamento")
        print("3. Adicionar funcionário a departamento")
        print("4. Listar funcionários de um departamento")
        print("5. Mostrar média salarial de um departamento")
        print("6. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            nome = input("Nome do funcionário: ")
            salario = float(input("Salário do funcionário: "))
            f = Funcionario(nome, salario)
            funcionarios.append(f)
            print("Funcionário criado com sucesso!")

        elif opcao == "2":
            nome = input("Nome do departamento: ")
            d = Departamento(nome)
            departamentos.append(d)
            print("Departamento criado com sucesso!")

        elif opcao == "3":
            if not funcionarios or not departamentos:
                print("Crie funcionários e departamentos primeiro!")
            else:
                print("\n--- Funcionários disponíveis ---")
                for i, f in enumerate(funcionarios, 1):
                    print(f"{i}. {f.get_nome()} - R${f.get_salario():.2f}")

                func_idx = int(input("Escolha o número do funcionário: ")) - 1

                print("\n--- Departamentos disponíveis ---")
                for i, d in enumerate(departamentos, 1):
                    print(f"{i}. {d.get_nome()}")

                dept_idx = int(input("Escolha o número do departamento: ")) - 1
                # len() é uma função pronta que retorna o tamanho de uma lista
                if 0 <= func_idx < len(funcionarios) and 0 <= dept_idx < len(departamentos):
                    departamentos[dept_idx].adicionar_funcionario(funcionarios[func_idx])
                    print("Funcionário adicionado ao departamento!")
                else:
                    print("Opção inválida!")

        elif opcao == "4":
            if not departamentos:
                print("Nenhum departamento criado ainda.")
            else:
                for i, d in enumerate(departamentos, 1): # É uma função pronta que gera índices automáticos, serve para percorrer uma lista e, ao mesmo tempo, pegar o índice (posição) de cada item. 
                    print(f"{i}. {d.get_nome()}")
                dept_idx = int(input("Escolha o número do departamento: ")) - 1
                if 0 <= dept_idx < len(departamentos):
                    departamentos[dept_idx].listar_funcionarios()
                else:
                    print("Opção inválida!")

        elif opcao == "5":
            if not departamentos:
                print("Nenhum departamento criado ainda.")
            else:
                for i, d in enumerate(departamentos, 1):
                    print(f"{i}. {d.get_nome()}")
                dept_idx = int(input("Escolha o número do departamento: ")) - 1
                if 0 <= dept_idx < len(departamentos):
                    media = departamentos[dept_idx].media_salarial()
                    print(f"Média salarial do departamento {departamentos[dept_idx].get_nome()}: R${media:.2f}")
                else:
                    print("Opção inválida!")

        elif opcao == "6":
            print("Saindo do programa... Até logo!")
            break

        else:
            print("Opção inválida! Tente novamente.")
