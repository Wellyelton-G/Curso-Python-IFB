# Leitura dos valores
A = int(input("Digite o valor de A: "))
B = int(input("Digite o valor de B: "))

# Exibe os valores originais
print(f"\nValores antes da troca:")
print(f"A = {A}")
print(f"B = {B}")

# Troca dos valores
A, B = B, A  # troca simultânea 

# Exibe os valores trocados
print(f"\nValores depois da troca:")
print(f"A = {A}")
print(f"B = {B}")
