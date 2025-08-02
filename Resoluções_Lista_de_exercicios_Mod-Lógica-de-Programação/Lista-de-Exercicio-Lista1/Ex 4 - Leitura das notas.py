# Leitura das notas
P1 = float(input("Digite a nota da prova 1 (P1): "))
P2 = float(input("Digite a nota da prova 2 (P2): "))
T1 = float(input("Digite a nota do trabalho 1 (T1): "))
T2 = float(input("Digite a nota do trabalho 2 (T2): "))

# Cálculo das médias
MP = (P1 + P2) / 2  # Média das provas
MT = (T1 + T2) / 2  # Média dos trabalhos
MF = 0.8 * MP + 0.2 * MT  # Média final ponderada

# Exibição das médias
print(f"\nMédia das provas (MP): {MP:.2f}")
print(f"Média dos trabalhos (MT): {MT:.2f}")
print(f"Média final (MF): {MF:.2f}")

# Verificação da situação
if MF >= 6.0:
    print("Situação: Aprovado ")
else:
    print("Situação: Não aprovado ")
