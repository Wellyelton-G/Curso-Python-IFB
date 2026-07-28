from abc import ABC, abstractmethod


class Funcionario(ABC):
    def __init__(self, nome, salario_base=0):
        self.nome = nome
        self.salario_base = salario_base

    @abstractmethod
    def calcular_pagamento(self):
        pass


class FuncionarioHorista(Funcionario):
    def __init__(self, nome, horas_trabalhadas, valor_hora):
        super().__init__(nome)
        self.horas_trabalhadas = horas_trabalhadas
        self.valor_hora = valor_hora

    def calcular_pagamento(self):
        return self.horas_trabalhadas * self.valor_hora


class FuncionarioComissionado(Funcionario):
    def __init__(self, nome, salario_base, comissao):
        super().__init__(nome, salario_base)
        self.comissao = comissao

    def calcular_pagamento(self):
        return self.salario_base + self.comissao


class FuncionarioTemporario(Funcionario):
    def __init__(self, nome, dias_trabalhados, valor_diario):
        super().__init__(nome)
        self.dias_trabalhados = dias_trabalhados
        self.valor_diario = valor_diario

    def calcular_pagamento(self):
        return self.dias_trabalhados * self.valor_diario


if __name__ == "__main__":
    funcionarios = [
        FuncionarioHorista("Ana", 80, 30),
        FuncionarioComissionado("Bruno", 2500, 700),
        FuncionarioTemporario("Carla", 15, 180)
    ]

    for funcionario in funcionarios:
        print(f"{funcionario.nome}: R$ {funcionario.calcular_pagamento():.2f}")
