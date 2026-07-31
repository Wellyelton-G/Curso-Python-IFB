"""Questao 16: objetos associados e regra de disponibilidade."""


class Hospede:
    def __init__(self, nome, documento):
        self.nome = nome
        self.documento = documento


class Quarto:
    def __init__(self, numero, tipo, valor_diaria):
        self.numero = numero
        self.tipo = tipo
        self.valor_diaria = valor_diaria
        self.disponivel = True


class Reserva:
    def __init__(self, hospede, quarto, diarias):
        if diarias <= 0:
            raise ValueError("A quantidade de diárias deve ser positiva.")
        if not quarto.disponivel:
            raise RuntimeError("Quarto indisponível.")
        self.hospede = hospede
        self.quarto = quarto
        self.diarias = diarias
        self.ativa = True
        # Reservar muda imediatamente o estado do quarto relacionado.
        quarto.disponivel = False

    def calcular_valor(self):
        return self.quarto.valor_diaria * self.diarias

    def cancelar(self):
        if not self.ativa:
            raise RuntimeError("A reserva já foi cancelada.")
        self.ativa = False
        # Cancelar desfaz a indisponibilidade criada pela reserva.
        self.quarto.disponivel = True


class Hotel:
    def __init__(self):
        self.hospedes = []
        self.quartos = []
        self.reservas = []

    def cadastrar_hospede(self, hospede):
        self.hospedes.append(hospede)

    def cadastrar_quarto(self, quarto):
        self.quartos.append(quarto)

    def listar_quartos_disponiveis(self):
        return [q for q in self.quartos if q.disponivel]

    def realizar_reserva(self, hospede, quarto, diarias):
        reserva = Reserva(hospede, quarto, diarias)
        self.reservas.append(reserva)
        return reserva


if __name__ == "__main__":
    hotel = Hotel()
    hospede = Hospede("Ana", "123")
    quarto = Quarto(101, "Standard", 220)
    hotel.cadastrar_hospede(hospede)
    hotel.cadastrar_quarto(quarto)

    reserva = hotel.realizar_reserva(hospede, quarto, 3)
    print(f"Total: R$ {reserva.calcular_valor():.2f}")
