# Leitura do custo de fábrica
custo_fabrica = float(input("Digite o custo de fábrica do carro: R$ "))

# Cálculo do custo ao consumidor
distribuidor = custo_fabrica * 0.12
impostos = custo_fabrica * 0.30
custo_consumidor = custo_fabrica + distribuidor + impostos

# Exibição dos resultados
print(f"\nResumo do custo do carro:")
print(f"Custo de fábrica:       R$ {custo_fabrica:.2f}")
print(f"Distribuidor (12%):    R$ {distribuidor:.2f}")
print(f"Impostos (30%):        R$ {impostos:.2f}")
print(f"Custo ao consumidor:   R$ {custo_consumidor:.2f}")
