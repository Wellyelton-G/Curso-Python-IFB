#Definiçao da Função
def converter_moeda():
    # Menu de opções
    print("Selecione a moeda para conversão:")
    print("1. Dólar")
    print("2. Euro")
    print("3. Libra")
    print("4. Iene")
    
    # Recebe a escolha do usuário
    opcao = int(input("Digite o número correspondente à moeda escolhida: "))
    
    # Recebe o valor em reais
    valor_reais = float(input("Digite o valor em reais (R$): "))
    
    # Taxas de conversão fictícias
    if opcao == 1:
        valor_convertido = valor_reais * 0.19  # Dólar
        moeda = "Dólares"
    elif opcao == 2:
        valor_convertido = valor_reais * 0.17  # Euro
        moeda = "Euros"
    elif opcao == 3:
        valor_convertido = valor_reais * 0.15  # Libra
        moeda = "Libras"
    elif opcao == 4:
        valor_convertido = valor_reais * 25  # Iene
        moeda = "Ienes"
    else:
        print("Opção inválida!")
        return
    
    # Exibe o valor convertido
    print(f"{valor_reais} reais é equivalente a {valor_convertido:.2f} {moeda}.")

# Chama a função para execução
converter_moeda()