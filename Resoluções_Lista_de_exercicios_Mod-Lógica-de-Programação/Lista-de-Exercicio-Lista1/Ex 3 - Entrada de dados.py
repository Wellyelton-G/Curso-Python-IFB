# Entrada de dados
tamanho_mb = float(input("Informe o tamanho do arquivo (em MB): "))
velocidade_mbps = float(input("Informe a velocidade da internet (em Mbps): "))

# Conversão de MB para megabits
tamanho_megabits = tamanho_mb / 8

# Cálculo do tempo em segundos
tempo_segundos = tamanho_megabits / velocidade_mbps

# Conversão para minutos
tempo_minutos = tempo_segundos / 60

# Exibição do resultado
print(f"\nTempo aproximado de download: {tempo_minutos:.2f} minutos")
