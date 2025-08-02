# Leitura da temperatura
temperatura = float(input("Digite a temperatura em °C: "))

# Classificação da temperatura
if temperatura < 0:
    classificacao = "Frio extremo"
elif 0 <= temperatura <= 10:
    classificacao = "Frio"
elif 11 <= temperatura <= 25:
    classificacao = "Ameno"
elif 26 <= temperatura <= 35:
    classificacao = "Quente"
else:  # temperatura > 35
    classificacao = "Muito quente"

# Exibição do resultado
print(f"\nTemperatura: {temperatura:.1f}°C")
print(f"Classificação: {classificacao}")
