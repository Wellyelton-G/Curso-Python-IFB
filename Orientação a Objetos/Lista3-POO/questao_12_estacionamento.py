from datetime import datetime
from math import ceil


class Veiculo:
    def __init__(self, placa, modelo, horario_entrada=None):
        self.placa = placa.upper()
        self.modelo = modelo
        self.horario_entrada = horario_entrada or datetime.now()


class Estacionamento:
    VALOR_HORA = 5.00

    def __init__(self):
        self.veiculos = {}

    def registrar_entrada(self, veiculo):
        if veiculo.placa in self.veiculos:
            raise ValueError("Veículo já está no estacionamento.")
        self.veiculos[veiculo.placa] = veiculo

    def registrar_saida(self, placa, horario_saida=None):
        placa = placa.upper()
        if placa not in self.veiculos:
            raise ValueError("Veículo não encontrado.")
        veiculo = self.veiculos.pop(placa)
        saida = horario_saida or datetime.now()
        segundos = (saida - veiculo.horario_entrada).total_seconds()
        horas_cobradas = max(1, ceil(segundos / 3600))
        valor = horas_cobradas * self.VALOR_HORA
        return veiculo, horas_cobradas, valor

    def listar_veiculos(self):
        for veiculo in self.veiculos.values():
            print(f"{veiculo.placa} | {veiculo.modelo} | {veiculo.horario_entrada:%d/%m/%Y %H:%M}")


if __name__ == "__main__":
    from datetime import timedelta

    estacionamento = Estacionamento()
    entrada = datetime.now() - timedelta(hours=2, minutes=10)
    estacionamento.registrar_entrada(Veiculo("ABC1D23", "Sedan", entrada))
    estacionamento.listar_veiculos()
    veiculo, horas, valor = estacionamento.registrar_saida("ABC1D23")
    print(f"Saída de {veiculo.placa}. {horas} hora(s). Total: R$ {valor:.2f}")
