"""Questao 28 - Jogo de batalha por turnos.

O controle das regras foi separado em tres partes: Personagem conhece seus
atributos, Habilidade conhece seu efeito e Batalha controla ordem e historico.
Essa divisao evita uma unica classe muito grande e dificil de manter.
"""

from abc import ABC, abstractmethod


class AcaoInvalidaError(Exception):
    """Representa qualquer acao proibida pelas regras da batalha."""


class Habilidade(ABC):
    """Estrategia abstrata para efeitos especiais diferentes."""

    def __init__(self, nome, custo_energia):
        self.nome = nome
        self.custo_energia = custo_energia

    def _consumir_energia(self, usuario):
        if usuario.energia < self.custo_energia:
            raise AcaoInvalidaError("Energia insuficiente.")
        usuario.energia -= self.custo_energia

    @abstractmethod
    def usar(self, usuario, alvo):
        """Cada subclasse produz um efeito diferente."""


class HabilidadeAtaque(Habilidade):
    def __init__(self, nome, custo_energia, dano):
        super().__init__(nome, custo_energia)
        self.dano = dano

    def usar(self, usuario, alvo):
        self._consumir_energia(usuario)
        dano_causado = alvo.receber_dano(self.dano + usuario.nivel * 2)
        return f"causou {dano_causado:.0f} de dano em {alvo.nome}"


class HabilidadeCura(Habilidade):
    def __init__(self, nome, custo_energia, cura):
        super().__init__(nome, custo_energia)
        self.cura = cura

    def usar(self, usuario, alvo=None):
        self._consumir_energia(usuario)
        vida_anterior = usuario.vida
        usuario.vida = min(usuario.vida_maxima, usuario.vida + self.cura)
        return f"recuperou {usuario.vida - vida_anterior:.0f} de vida"


class HabilidadeDefesa(Habilidade):
    def __init__(self, nome, custo_energia, bonus):
        super().__init__(nome, custo_energia)
        self.bonus = bonus

    def usar(self, usuario, alvo=None):
        self._consumir_energia(usuario)
        usuario.defesa += self.bonus
        return f"aumentou a defesa em {self.bonus}"


class Item:
    def __init__(self, nome, cura=0, energia=0):
        self.nome = nome
        self.cura = cura
        self.energia = energia

    def aplicar(self, personagem):
        vida_anterior = personagem.vida
        energia_anterior = personagem.energia
        personagem.vida = min(personagem.vida_maxima, personagem.vida + self.cura)
        personagem.energia = min(
            personagem.energia_maxima, personagem.energia + self.energia
        )
        return (
            personagem.vida - vida_anterior,
            personagem.energia - energia_anterior,
        )


class Personagem(ABC):
    """Classe abstrata: somente Guerreiro, Mago ou Arqueiro podem lutar."""

    def __init__(self, nome, vida, energia, nivel, defesa):
        self.nome = nome
        self.vida = float(vida)
        self.vida_maxima = float(vida)
        self.energia = float(energia)
        self.energia_maxima = float(energia)
        self.nivel = nivel
        self.defesa = defesa
        self.habilidades = []
        self.itens = []

    @property
    def vivo(self):
        return self.vida > 0

    def _validar_acao(self):
        if not self.vivo:
            raise AcaoInvalidaError("Personagem derrotado nao pode agir.")

    def receber_dano(self, ataque):
        if not self.vivo:
            raise AcaoInvalidaError("Nao e possivel atacar um personagem derrotado.")
        dano = max(0, ataque - self.defesa)
        self.vida = max(0, self.vida - dano)
        return dano

    @abstractmethod
    def atacar(self, alvo):
        """O calculo do ataque muda conforme a subclasse (polimorfismo)."""

    def aprender_habilidade(self, habilidade):
        self.habilidades.append(habilidade)

    def usar_habilidade(self, habilidade, alvo=None):
        self._validar_acao()
        if habilidade not in self.habilidades:
            raise AcaoInvalidaError("O personagem nao conhece essa habilidade.")
        if alvo is not None and not alvo.vivo:
            raise AcaoInvalidaError("O alvo ja foi derrotado.")
        return habilidade.usar(self, alvo)

    def adicionar_item(self, item):
        self.itens.append(item)

    def usar_item(self, item):
        self._validar_acao()
        if item not in self.itens:
            raise AcaoInvalidaError("O personagem nao possui esse item.")
        resultado = item.aplicar(self)
        self.itens.remove(item)  # o item e consumido depois do uso
        return resultado


class Guerreiro(Personagem):
    def atacar(self, alvo):
        self._validar_acao()
        return alvo.receber_dano(16 + self.nivel * 2)


class Mago(Personagem):
    def atacar(self, alvo):
        self._validar_acao()
        if self.energia < 5:
            raise AcaoInvalidaError("O mago precisa de 5 pontos de energia.")
        self.energia -= 5
        return alvo.receber_dano(20 + self.nivel * 3)


class Arqueiro(Personagem):
    def atacar(self, alvo):
        self._validar_acao()
        return alvo.receber_dano(14 + self.nivel * 2.5)


class Batalha:
    """Coordena turnos e registra todas as acoes realizadas."""

    def __init__(self, personagens):
        if len(personagens) < 2:
            raise ValueError("A batalha precisa de pelo menos dois personagens.")
        self.personagens = list(personagens)
        self.historico = ["Batalha iniciada."]
        self.numero_turno = 1
        self._indice_atual = 0

    def personagens_vivos(self):
        return [personagem for personagem in self.personagens if personagem.vivo]

    @property
    def personagem_da_vez(self):
        # Se alguem foi derrotado, avancamos ate encontrar um participante vivo.
        while not self.personagens[self._indice_atual].vivo:
            self._indice_atual = (self._indice_atual + 1) % len(self.personagens)
        return self.personagens[self._indice_atual]

    def _validar_turno(self, personagem):
        if self.encerrada():
            raise AcaoInvalidaError("A batalha ja terminou.")
        if personagem is not self.personagem_da_vez:
            raise AcaoInvalidaError(
                f"Agora e o turno de {self.personagem_da_vez.nome}."
            )

    def _encerrar_turno(self, descricao):
        self.historico.append(f"Turno {self.numero_turno}: {descricao}")
        if self.encerrada():
            vencedor = self.vencedor()
            self.historico.append(f"Batalha encerrada. Vencedor: {vencedor.nome}.")
            return
        self.numero_turno += 1
        self._indice_atual = (self._indice_atual + 1) % len(self.personagens)

    def executar_ataque(self, atacante, alvo):
        self._validar_turno(atacante)
        dano = atacante.atacar(alvo)
        self._encerrar_turno(
            f"{atacante.nome} atacou {alvo.nome} e causou {dano:.0f} de dano."
        )

    def executar_habilidade(self, usuario, habilidade, alvo=None):
        self._validar_turno(usuario)
        efeito = usuario.usar_habilidade(habilidade, alvo)
        self._encerrar_turno(f"{usuario.nome} usou {habilidade.nome} e {efeito}.")

    def executar_item(self, usuario, item):
        self._validar_turno(usuario)
        vida, energia = usuario.usar_item(item)
        self._encerrar_turno(
            f"{usuario.nome} usou {item.nome}: +{vida:.0f} vida, "
            f"+{energia:.0f} energia."
        )

    def encerrada(self):
        return len(self.personagens_vivos()) <= 1

    def vencedor(self):
        vivos = self.personagens_vivos()
        return vivos[0] if len(vivos) == 1 else None


if __name__ == "__main__":
    guerreiro = Guerreiro("Garen", 100, 30, 2, 8)
    mago = Mago("Lyra", 80, 60, 2, 4)
    golpe = HabilidadeAtaque("Golpe poderoso", 10, 30)
    guerreiro.aprender_habilidade(golpe)
    mago.adicionar_item(Item("Pocao", cura=15))
    batalha = Batalha([guerreiro, mago])

    # As acoes alternam obrigatoriamente entre os participantes vivos.
    while not batalha.encerrada():
        atual = batalha.personagem_da_vez
        alvo = mago if atual is guerreiro else guerreiro
        if atual is guerreiro and atual.energia >= golpe.custo_energia:
            batalha.executar_habilidade(atual, golpe, alvo)
        else:
            batalha.executar_ataque(atual, alvo)

    print("\n".join(batalha.historico))
