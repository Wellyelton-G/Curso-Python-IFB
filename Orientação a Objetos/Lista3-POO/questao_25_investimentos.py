from abc import ABC, abstractmethod


class Investimento(ABC):
    def __init__(self, nome, valor):
        self.nome = nome
        self.valor = valor

    @abstractmethod
    def calcular_rendimento(self):
        pass

    @abstractmethod
    def calcular_imposto(self):
        pass

    @abstractmethod
    def exibir_risco(self):
        pass


class Poupanca(Investimento):
    def calcular_rendimento(self):
        return self.valor * 0.006

    def calcular_imposto(self):
        return 0

    def exibir_risco(self):
        return "Baixo"


class CDB(Investimento):
    def calcular_rendimento(self):
        return self.valor * 0.012

    def calcular_imposto(self):
        return self.calcular_rendimento() * 0.175

    def exibir_risco(self):
        return "Baixo"


class FundoInvestimento(Investimento):
    def calcular_rendimento(self):
        return self.valor * 0.015

    def calcular_imposto(self):
        return self.calcular_rendimento() * 0.20

    def exibir_risco(self):
        return "Médio"


class Acao(Investimento):
    def calcular_rendimento(self):
        return self.valor * 0.025

    def calcular_imposto(self):
        return max(0, self.calcular_rendimento() * 0.15)

    def exibir_risco(self):
        return "Alto"


class Investidor:
    def __init__(self, nome):
        self.nome = nome


class CarteiraInvestimentos:
    def __init__(self, investidor):
        self.investidor = investidor
        self.investimentos = []

    def adicionar(self, investimento):
        self.investimentos.append(investimento)

    def patrimonio_total(self):
        return sum(i.valor for i in self.investimentos)

    def rendimentos(self):
        return sum(i.calcular_rendimento() for i in self.investimentos)

    def impostos(self):
        return sum(i.calcular_imposto() for i in self.investimentos)

    def distribuicao(self):
        total = self.patrimonio_total()
        return {i.nome: (i.valor / total * 100 if total else 0) for i in self.investimentos}

    def por_risco(self):
        resultado = {}
        for investimento in self.investimentos:
            resultado.setdefault(investimento.exibir_risco(), []).append(investimento.nome)
        return resultado


if __name__ == "__main__":
    carteira = CarteiraInvestimentos(Investidor("Ana"))
    carteira.adicionar(Poupanca("Reserva", 5000))
    carteira.adicionar(Acao("Ações", 3000))
    print(f"Patrimônio: R$ {carteira.patrimonio_total():.2f}")
    print(f"Rendimentos: R$ {carteira.rendimentos():.2f}")
    print(carteira.distribuicao())
