class Animal:
    def __init__(self, nome, idade):
        self.nome = nome
        self.idade = idade

    def emitir_som(self):
        raise NotImplementedError("A subclasse deve implementar emitir_som().")


class Cachorro(Animal):
    def emitir_som(self):
        return "Au au!"


class Gato(Animal):
    def emitir_som(self):
        return "Miau!"


class Vaca(Animal):
    def emitir_som(self):
        return "Muuu!"


if __name__ == "__main__":
    animais = [
        Cachorro("Rex", 4),
        Gato("Mimi", 2),
        Vaca("Estrela", 5)
    ]

    # O mesmo método produz resultados diferentes conforme o tipo do objeto.
    for animal in animais:
        print(f"{animal.nome}: {animal.emitir_som()}")
