class Retangulo:
    """Calcula área e perímetro de um retângulo."""

    def __init__(self, base, altura):
        if base <= 0 or altura <= 0:
            raise ValueError("Base e altura devem ser maiores que zero.")
        self.base = base
        self.altura = altura

    def calcular_area(self):
        return self.base * self.altura

    def calcular_perimetro(self):
        return 2 * (self.base + self.altura)

    def exibir_dados(self):
        print(f"Base: {self.base:.2f}")
        print(f"Altura: {self.altura:.2f}")
        print(f"Área: {self.calcular_area():.2f}")
        print(f"Perímetro: {self.calcular_perimetro():.2f}")


if __name__ == "__main__":
    try:
        base = float(input("Informe a base: "))
        altura = float(input("Informe a altura: "))
        retangulo = Retangulo(base, altura)
        retangulo.exibir_dados()
    except ValueError as erro:
        print(f"Entrada inválida: {erro}")
