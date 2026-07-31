"""Questao 6: validacao no construtor impede objetos em estado invalido."""


class ContaEnergia:
    """Calcula o valor de uma conta de energia elétrica."""

    def __init__(self, nome_cliente, consumo_kwh, valor_kwh):
        if consumo_kwh < 0:
            raise ValueError("O consumo não pode ser negativo.")
        if valor_kwh < 0:
            raise ValueError("O valor do kWh não pode ser negativo.")
        self.nome_cliente = nome_cliente
        self.consumo_kwh = consumo_kwh
        self.valor_kwh = valor_kwh

    def calcular_total(self):
        # O consumo em kWh multiplicado pela tarifa resulta no valor da conta.
        return self.consumo_kwh * self.valor_kwh

    def exibir_dados(self):
        print(f"Cliente: {self.nome_cliente}")
        print(f"Consumo: {self.consumo_kwh:.2f} kWh")
        print(f"Valor do kWh: R$ {self.valor_kwh:.2f}")
        print(f"Total a pagar: R$ {self.calcular_total():.2f}")


if __name__ == "__main__":
    try:
        conta = ContaEnergia("João", 180, 0.92)
        conta.exibir_dados()
    except ValueError as erro:
        print(erro)
