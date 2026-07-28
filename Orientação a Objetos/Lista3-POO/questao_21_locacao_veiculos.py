from abc import ABC, abstractmethod
from datetime import date


class VeiculoIndisponivelError(Exception):
    pass


class ClienteInexistenteError(Exception):
    pass


class PeriodoInvalidoError(Exception):
    pass


class Veiculo(ABC):
    def __init__(self, placa, modelo, valor_base):
        self.placa = placa
        self.modelo = modelo
        self.valor_base = valor_base
        self.disponivel = True

    @abstractmethod
    def calcular_diaria(self):
        pass


class Carro(Veiculo):
    def calcular_diaria(self):
        return self.valor_base


class Moto(Veiculo):
    def calcular_diaria(self):
        return self.valor_base * 0.75


class Van(Veiculo):
    def calcular_diaria(self):
        return self.valor_base * 1.40


class Cliente:
    def __init__(self, documento, nome):
        self.documento = documento
        self.nome = nome
        self.historico = []


class Locacao:
    MULTA_DIARIA = 80.0

    def __init__(self, cliente, veiculo, inicio, fim_previsto):
        if fim_previsto < inicio:
            raise PeriodoInvalidoError("A data final não pode ser anterior à inicial.")
        if not veiculo.disponivel:
            raise VeiculoIndisponivelError("Veículo indisponível.")
        self.cliente = cliente
        self.veiculo = veiculo
        self.inicio = inicio
        self.fim_previsto = fim_previsto
        self.fim_real = None
        veiculo.disponivel = False

    def quantidade_diarias(self):
        return (self.fim_previsto - self.inicio).days + 1

    def calcular_total(self):
        return self.quantidade_diarias() * self.veiculo.calcular_diaria()

    def devolver(self, data_devolucao):
        self.fim_real = data_devolucao
        self.veiculo.disponivel = True
        atraso = max(0, (data_devolucao - self.fim_previsto).days)
        return atraso * self.MULTA_DIARIA


class Agencia:
    def __init__(self):
        self.veiculos = {}
        self.clientes = {}
        self.locacoes = []

    def cadastrar_veiculo(self, veiculo):
        self.veiculos[veiculo.placa] = veiculo

    def cadastrar_cliente(self, cliente):
        self.clientes[cliente.documento] = cliente

    def realizar_locacao(self, documento, placa, inicio, fim):
        cliente = self.clientes.get(documento)
        if not cliente:
            raise ClienteInexistenteError("Cliente não cadastrado.")
        veiculo = self.veiculos[placa]
        locacao = Locacao(cliente, veiculo, inicio, fim)
        self.locacoes.append(locacao)
        cliente.historico.append(locacao)
        return locacao

    def veiculos_disponiveis(self):
        return [v for v in self.veiculos.values() if v.disponivel]


if __name__ == "__main__":
    agencia = Agencia()
    agencia.cadastrar_cliente(Cliente("123", "Ana"))
    agencia.cadastrar_veiculo(Carro("AAA1A11", "Sedan", 180))

    locacao = agencia.realizar_locacao("123", "AAA1A11", date(2026, 7, 1), date(2026, 7, 3))
    print(f"Locação: R$ {locacao.calcular_total():.2f}")
    print(f"Multa: R$ {locacao.devolver(date(2026, 7, 5)):.2f}")
