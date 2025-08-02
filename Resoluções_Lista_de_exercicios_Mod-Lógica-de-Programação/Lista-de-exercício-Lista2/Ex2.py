#Definindo a função principal
def menu_banco():
    saldo = 1000.00  # Saldo inicial de R$ 1000,00

    while True:
        # Menu de opções
        print("\nEscolha uma opção:")
        print("1. Depositar")
        print("2. Sacar")
        print("3. Consultar Saldo")
        print("4. Sair")

        # Recebe a escolha do usuário
        opcao = int(input("Digite o número correspondente à opção desejada: "))

        if opcao == 1:
            # Depositar
            deposito = input("Digite o valor a ser depositado: R$ ")
            deposito = deposito.replace(",", ".")  # Substitui a vírgula por ponto
            try:
                deposito = float(deposito)
                saldo += deposito
                print(f"Você depositou R$ {deposito:.2f}. Saldo atual: R$ {saldo:.2f}")
            except ValueError:
                print("Valor inválido! Por favor, insira um número válido.")

        elif opcao == 2:
            # Sacar
            saque = input("Digite o valor a ser sacado: R$ ")
            saque = saque.replace(",", ".")  # Substitui a vírgula por ponto
            try:
                saque = float(saque)
                if saque <= saldo:
                    saldo -= saque
                    print(f"Você sacou R$ {saque:.2f}. Saldo atual: R$ {saldo:.2f}")
                else:
                    print("Saldo insuficiente para realizar o saque.")
            except ValueError:
                print("Valor inválido! Por favor, insira um número válido.")

        elif opcao == 3:
            # Consultar Saldo
            print(f"Saldo atual: R$ {saldo:.2f}")
        
        elif opcao == 4:
            # Sair
            print("Saindo do programa...")
            break
        
        else:
            # Opção inválida
            print("Opção inválida. Tente novamente.")

# Chama a função para execução
menu_banco()