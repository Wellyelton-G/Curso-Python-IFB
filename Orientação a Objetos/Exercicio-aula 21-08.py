def calculadora():
    while True:
        print("\n=== CALCULADORA ===")
        print("1. Soma")
        print("2. Subtração")
        print("3. Multiplicação")
        print("4. Divisão")
        print("5. Sair")

        try:
            opcao = int(input("Escolha uma opção (1-5): "))

            if opcao == 5:
                print("Encerrando a calculadora. Até logo!")
                break

            if opcao not in [1, 2, 3, 4]:
                print("Opção inválida! Tente novamente.")
                continue

            # Ler os dois números
            try:
                num1 = float(input("Digite o primeiro número: "))
                num2 = float(input("Digite o segundo número: "))
            except ValueError:
                print("Entrada inválida! Digite apenas números.")
                continue

            if opcao == 1:
                resultado = num1 + num2
                print(f"Resultado: {num1} + {num2} = {resultado}")
            elif opcao == 2:
                resultado = num1 - num2
                print(f"Resultado: {num1} - {num2} = {resultado}")
            elif opcao == 3:
                resultado = num1 * num2
                print(f"Resultado: {num1} * {num2} = {resultado}")
            elif opcao == 4:
                try:
                    resultado = num1 / num2
                    print(f"Resultado: {num1} / {num2} = {resultado}")
                except ZeroDivisionError:
                    print("Erro: Não é possível dividir por zero.")

        except ValueError:
            print("Entrada inválida! Escolha uma opção numérica entre 1 e 5.")


# Executar a calculadora
calculadora()
