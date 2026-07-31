"""Questao 3: um objeto pode oferecer diferentes visoes do mesmo valor."""


class Temperatura:
    """Armazena uma temperatura em Celsius e realiza conversões."""

    def __init__(self, celsius):
        self.celsius = celsius

    def para_fahrenheit(self):
        # A conversao nao altera Celsius; apenas devolve um valor calculado.
        return self.celsius * 1.8 + 32

    def para_kelvin(self):
        # Kelvin usa a mesma escala de variacao, deslocada em 273,15.
        return self.celsius + 273.15

    def exibir_valores(self):
        print(f"Celsius: {self.celsius:.2f} °C")
        print(f"Fahrenheit: {self.para_fahrenheit():.2f} °F")
        print(f"Kelvin: {self.para_kelvin():.2f} K")


if __name__ == "__main__":
    try:
        valor = float(input("Informe a temperatura em Celsius: "))
        temperatura = Temperatura(valor)
        temperatura.exibir_valores()
    except ValueError:
        print("Digite um número válido.")
