from abc import ABC, abstractmethod


class AcaoInvalidaError(Exception):
    pass


class Habilidade:
    def __init__(self, nome, dano, custo_energia):
        self.nome = nome
        self.dano = dano
        self.custo_energia = custo_energia


class Item:
    def __init__(self, nome, cura):
        self.nome = nome
        self.cura = cura


class Personagem(ABC):
    def __init__(self, nome, vida, energia, nivel, defesa):
        self.nome = nome
        self.vida = vida
        self.vida_maxima = vida
        self.energia = energia
        self.nivel = nivel
        self.defesa = defesa
        self.habilidades = []
        self.itens = []

    @property
    def vivo(self):
        return self.vida > 0

    @abstractmethod
    def atacar(self, alvo):
        pass

    def usar_habilidade(self, habilidade, alvo):
        if not self.vivo:
            raise AcaoInvalidaError("Personagem derrotado não pode agir.")
        if habilidade.custo_energia > self.energia:
            raise AcaoInvalidaError("Energia insuficiente.")
        self.energia -= habilidade.custo_energia
        dano = max(0, habilidade.dano - alvo.defesa)
        alvo.vida = max(0, alvo.vida - dano)
        return dano

    def usar_item(self, item):
        if not self.vivo:
            raise AcaoInvalidaError("Personagem derrotado não pode agir.")
        self.vida = min(self.vida_maxima, self.vida + item.cura)
        self.itens.remove(item)


class Guerreiro(Personagem):
    def atacar(self, alvo):
        dano = max(0, 16 + self.nivel * 2 - alvo.defesa)
        alvo.vida = max(0, alvo.vida - dano)
        return dano


class Mago(Personagem):
    def atacar(self, alvo):
        dano = max(0, 20 + self.nivel * 3 - alvo.defesa)
        self.energia = max(0, self.energia - 5)
        alvo.vida = max(0, alvo.vida - dano)
        return dano


class Arqueiro(Personagem):
    def atacar(self, alvo):
        dano = max(0, 14 + self.nivel * 2.5 - alvo.defesa)
        alvo.vida = max(0, alvo.vida - dano)
        return dano


class Batalha:
    def __init__(self, personagens):
        self.personagens = personagens
        self.historico = []
        self.turno = 0

    def personagens_vivos(self):
        return [p for p in self.personagens if p.vivo]

    def executar_ataque(self, atacante, alvo):
        if atacante not in self.personagens_vivos():
            raise AcaoInvalidaError("Atacante não pode agir.")
        dano = atacante.atacar(alvo)
        self.turno += 1
        self.historico.append(f"Turno {self.turno}: {atacante.nome} causou {dano:.0f} de dano em {alvo.nome}.")

    def encerrada(self):
        return len(self.personagens_vivos()) <= 1

    def vencedor(self):
        vivos = self.personagens_vivos()
        return vivos[0] if len(vivos) == 1 else None


if __name__ == "__main__":
    guerreiro = Guerreiro("Garen", 100, 30, 2, 8)
    mago = Mago("Lyra", 80, 60, 2, 4)
    batalha = Batalha([guerreiro, mago])

    while not batalha.encerrada():
        batalha.executar_ataque(guerreiro, mago)
        if mago.vivo:
            batalha.executar_ataque(mago, guerreiro)

    print("\n".join(batalha.historico))
    print(f"Vencedor: {batalha.vencedor().nome}")
