"""Questao 8: os metodos controlam as mudancas de estado da lampada."""


class Lampada:
    def __init__(self, cor, potencia):
        self.cor = cor
        self.potencia = potencia
        self.ligada = False

    def ligar(self):
        # A guarda evita repetir uma operacao que nao mudaria o estado.
        if self.ligada:
            print("A lâmpada já está ligada.")
            return
        self.ligada = True
        print("Lâmpada ligada.")

    def desligar(self):
        if not self.ligada:
            print("A lâmpada já está desligada.")
            return
        self.ligada = False
        print("Lâmpada desligada.")

    def mostrar_estado(self):
        # A expressao condicional converte o booleano em texto amigavel.
        estado = "ligada" if self.ligada else "desligada"
        print(f"Lâmpada {self.cor}, {self.potencia} W, está {estado}.")


if __name__ == "__main__":
    lampada = Lampada("branca", 12)
    lampada.mostrar_estado()
    lampada.ligar()
    lampada.ligar()
    lampada.desligar()
