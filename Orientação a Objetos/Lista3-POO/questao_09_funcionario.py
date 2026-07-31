"""Questao 9: encapsulamento do salario e alteracao por metodo controlado."""


class Funcionario:
    def __init__(self, nome, cargo, salario):
        if salario < 0:
            raise ValueError("O salário não pode ser negativo.")
        self.nome = nome
        self.cargo = cargo
        self.__salario = salario  # Atributo privado.

    def aplicar_reajuste(self, percentual):
        if percentual < 0:
            raise ValueError("O percentual não pode ser negativo.")
        # O novo salario e o antigo multiplicado por 1 mais a taxa decimal.
        self.__salario *= 1 + percentual / 100

    def get_salario(self):
        # Getter usado para consultar o atributo privado.
        return self.__salario

    def exibir_dados(self):
        print(f"Nome: {self.nome}")
        print(f"Cargo: {self.cargo}")
        print(f"Salário: R$ {self.__salario:.2f}")


if __name__ == "__main__":
    funcionario = Funcionario("Paulo", "Analista", 3500)
    funcionario.aplicar_reajuste(8)
    funcionario.exibir_dados()
