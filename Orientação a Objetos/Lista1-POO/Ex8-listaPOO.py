# ===== Classe Base =====
class Personagem:
    def __init__(self, nome, nivel):
        self.nome = nome      # nome do personagem
        self.nivel = nivel    # nível do personagem

    def atacar(self):
        # Método genérico (será sobrescrito nas subclasses)
        print(f"{self.nome} ataca de forma genérica!")


# ===== Subclasse Guerreiro =====
class Guerreiro(Personagem):
    def __init__(self, nome, nivel, forca):
        super().__init__(nome, nivel)  # chama o construtor da classe base
        self.forca = forca             # atributo adicional do Guerreiro

    def atacar(self):
        # Sobrescrita do método atacar (polimorfismo)
        print(f"{self.nome} (Guerreiro nível {self.nivel}) ataca com espada! Força: {self.forca}")


# ===== Subclasse Mago =====
class Mago(Personagem):
    def __init__(self, nome, nivel, mana):
        super().__init__(nome, nivel)  # chama o construtor da classe base
        self.mana = mana               # atributo adicional do Mago

    def atacar(self):
        # Sobrescrita do método atacar (polimorfismo)
        print(f"{self.nome} (Mago nível {self.nivel}) lança magia! Mana: {self.mana}")


# ===== Programa Principal =====
if __name__ == "__main__":
    # Criando personagens (classe base + subclasses)
    personagem_generico = Personagem("Aventureiro", 1)
    guerreiro = Guerreiro("Thorin", 5, forca=80)
    mago = Mago("Gandalf", 10, mana=120)

    # Lista polimórfica: diferentes classes tratadas como a base
    personagens = [personagem_generico, guerreiro, mago]

    # Invocando o método atacar em todos (polimorfismo em tempo de execução)
    print("\n--- ATAQUES DOS PERSONAGENS ---")
    for p in personagens:
        p.atacar()  # comportamento depende da classe real do objeto
