"""Questao 4: as regras de preco ficam junto ao objeto Produto."""


class Produto:
    """Representa um produto com percentual de desconto."""

    def __init__(self, nome, preco, percentual_desconto):
        if preco < 0:
            raise ValueError("O preço não pode ser negativo.")
        if not 0 <= percentual_desconto <= 100:
            raise ValueError("O desconto deve estar entre 0 e 100.")
        self.nome = nome
        self.preco = preco
        self.percentual_desconto = percentual_desconto

    def calcular_desconto(self):
        # Dividir por 100 transforma o percentual em uma proporcao decimal.
        return self.preco * self.percentual_desconto / 100

    def calcular_preco_final(self):
        # Reutilizar calcular_desconto evita duplicar a mesma formula.
        return self.preco - self.calcular_desconto()

    def exibir_resumo(self):
        print(f"Produto: {self.nome}")
        print(f"Preço original: R$ {self.preco:.2f}")
        print(f"Desconto: R$ {self.calcular_desconto():.2f}")
        print(f"Preço final: R$ {self.calcular_preco_final():.2f}")


if __name__ == "__main__":
    produto = Produto("Teclado", 150.00, 10)
    produto.exibir_resumo()
