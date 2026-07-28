from abc import ABC, abstractmethod


class SaldoInsuficienteError(Exception):
    pass


class Rota:
    def __init__(self, origem, destino, distancia_km):
        self.origem = origem
        self.destino = destino
        self.distancia_km = distancia_km


class Transporte(ABC):
    @abstractmethod
    def calcular_tarifa(self, rota):
        pass

    @abstractmethod
    def calcular_tempo_estimado(self, rota):
        pass

    def exibir_rota(self, rota):
        return f"{rota.origem} para {rota.destino}"


class Onibus(Transporte):
    def calcular_tarifa(self, rota):
        return 5.50

    def calcular_tempo_estimado(self, rota):
        return rota.distancia_km / 25 * 60


class Metro(Transporte):
    def calcular_tarifa(self, rota):
        return 5.50

    def calcular_tempo_estimado(self, rota):
        return rota.distancia_km / 40 * 60


class BicicletaCompartilhada(Transporte):
    def calcular_tarifa(self, rota):
        return 2 + rota.distancia_km * 0.30

    def calcular_tempo_estimado(self, rota):
        return rota.distancia_km / 15 * 60


class TransporteAplicativo(Transporte):
    def calcular_tarifa(self, rota):
        return 6 + rota.distancia_km * 2.10

    def calcular_tempo_estimado(self, rota):
        return rota.distancia_km / 35 * 60


class CartaoTransporte:
    def __init__(self, saldo=0):
        self.saldo = saldo

    def debitar(self, valor):
        if valor > self.saldo:
            raise SaldoInsuficienteError("Saldo insuficiente.")
        self.saldo -= valor


class Passageiro:
    def __init__(self, nome, cartao):
        self.nome = nome
        self.cartao = cartao
        self.historico = []


class Viagem:
    def __init__(self, passageiro, transporte, rota):
        self.passageiro = passageiro
        self.transporte = transporte
        self.rota = rota

    def realizar(self, integracao=False):
        tarifa = self.transporte.calcular_tarifa(self.rota)
        if integracao:
            tarifa *= 0.50
        self.passageiro.cartao.debitar(tarifa)
        self.passageiro.historico.append(self)
        return tarifa


def sugerir_menor_custo(transportes, rota):
    return min(transportes, key=lambda t: t.calcular_tarifa(rota))


if __name__ == "__main__":
    rota = Rota("Centro", "Campus", 12)
    opcoes = [Onibus(), Metro(), BicicletaCompartilhada(), TransporteAplicativo()]
    melhor = sugerir_menor_custo(opcoes, rota)
    print(f"Menor custo: {melhor.__class__.__name__}, R$ {melhor.calcular_tarifa(rota):.2f}")
