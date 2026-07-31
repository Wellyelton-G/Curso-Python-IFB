"""Questao 23: entregas polimorficas e maquina de estados do pedido."""

from abc import ABC, abstractmethod


class EstadoInvalidoError(Exception):
    pass


class Endereco:
    def __init__(self, cidade, regiao):
        self.cidade = cidade
        self.regiao = regiao


class Cliente:
    def __init__(self, nome, endereco):
        self.nome = nome
        self.endereco = endereco


class Entrega(ABC):
    @abstractmethod
    def calcular_frete(self, peso, distancia, regiao):
        pass

    @abstractmethod
    def calcular_prazo(self, distancia):
        pass

    @abstractmethod
    def rastrear(self):
        pass


class EntregaNormal(Entrega):
    def calcular_frete(self, peso, distancia, regiao):
        adicional = 10 if regiao == "remota" else 0
        return 12 + peso * 1.5 + distancia * 0.05 + adicional

    def calcular_prazo(self, distancia):
        return max(3, int(distancia / 300) + 3)

    def rastrear(self):
        return "Rastreamento normal ativo."


class EntregaExpressa(Entrega):
    def calcular_frete(self, peso, distancia, regiao):
        adicional = 20 if regiao == "remota" else 0
        return 25 + peso * 2.5 + distancia * 0.09 + adicional

    def calcular_prazo(self, distancia):
        return max(1, int(distancia / 700) + 1)

    def rastrear(self):
        return "Rastreamento expresso em tempo real."


class EntregaRetiradaLocal(Entrega):
    def calcular_frete(self, peso, distancia, regiao):
        return 0

    def calcular_prazo(self, distancia):
        return 1

    def rastrear(self):
        return "Pedido aguardando retirada."


class Pedido:
    ESTADOS = [
        "Pedido criado",
        "Pagamento confirmado",
        "Em separação",
        "Enviado",
        "Em transporte",
        "Entregue"
    ]

    def __init__(self, cliente, entrega, peso, distancia):
        self.cliente = cliente
        self.entrega = entrega
        self.peso = peso
        self.distancia = distancia
        self.estado = self.ESTADOS[0]

    def avancar_estado(self, novo_estado):
        # Uma maquina de estados permite somente a proxima etapa da sequencia.
        atual = self.ESTADOS.index(self.estado)
        esperado = atual + 1
        if esperado >= len(self.ESTADOS) or self.ESTADOS[esperado] != novo_estado:
            raise EstadoInvalidoError("Transição de estado inválida.")
        self.estado = novo_estado


class Transportadora:
    def calcular(self, pedido):
        # A transportadora delega a formula ao tipo concreto de Entrega.
        regiao = pedido.cliente.endereco.regiao
        return pedido.entrega.calcular_frete(pedido.peso, pedido.distancia, regiao)


if __name__ == "__main__":
    cliente = Cliente("Ana", Endereco("Brasília", "centro"))
    pedido = Pedido(cliente, EntregaExpressa(), 2.5, 120)
    frete = Transportadora().calcular(pedido)
    print(f"Frete: R$ {frete:.2f}")
    pedido.avancar_estado("Pagamento confirmado")
    print(pedido.estado)
