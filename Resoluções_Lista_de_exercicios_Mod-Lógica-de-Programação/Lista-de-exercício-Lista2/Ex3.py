def exponenciacao(x, y):
    # Quando y for 0, o resultado é sempre 1
    if y == 0:
        return 1
    
    resultado = 1
    for _ in range(abs(y)):  # Itera 'y' vezes
        resultado *= x
    
    # Se y for negativo, faz a inversão do resultado
    if y < 0:
        return 1 / resultado
    return resultado

# Lê os valores de x e y
x = int(input("Digite o valor de x (base): "))
y = int(input("Digite o valor de y (expoente): "))

# Calcula e exibe o resultado da exponenciação
resultado = exponenciacao(x, y)
print(f"O resultado de {x} elevado a {y} é: {resultado}")