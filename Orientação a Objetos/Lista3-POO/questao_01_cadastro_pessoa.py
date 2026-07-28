class Pessoa:
    """Representa uma pessoa com nome, idade e cidade."""

    def __init__(self, nome, idade, cidade):
        # O construtor recebe os dados e os armazena no objeto.
        self.nome = nome
        self.idade = idade
        self.cidade = cidade

    def apresentar(self):
        # Este método usa os atributos do próprio objeto para montar a mensagem.
        print(f"Olá! Meu nome é {self.nome}, tenho {self.idade} anos e moro em {self.cidade}.")


if __name__ == "__main__":
    # Criamos dois objetos diferentes a partir da mesma classe.
    pessoa1 = Pessoa("Ana", 20, "Brasília")
    pessoa2 = Pessoa("Carlos", 32, "Goiânia")

    pessoa1.apresentar()
    pessoa2.apresentar()
