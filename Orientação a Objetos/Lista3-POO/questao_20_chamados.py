"""Questao 20: chamado encapsulado com historico de alteracoes."""

from datetime import datetime


class Usuario:
    def __init__(self, nome):
        self.nome = nome


class Tecnico:
    def __init__(self, nome):
        self.nome = nome


class Chamado:
    STATUS_VALIDOS = {"Aberto", "Em atendimento", "Encerrado"}
    PRIORIDADES = {"Baixa", "Média", "Alta"}

    def __init__(self, numero, descricao, prioridade, usuario):
        if prioridade not in self.PRIORIDADES:
            raise ValueError("Prioridade inválida.")
        self.numero = numero
        self.descricao = descricao
        self.__prioridade = prioridade
        self.__status = "Aberto"
        self.usuario = usuario
        self.tecnico = None
        self.historico = []
        self._registrar("Chamado aberto.")

    def _registrar(self, texto):
        # Centralizar o registro garante o mesmo formato em todo o historico.
        self.historico.append(f"{datetime.now():%d/%m/%Y %H:%M:%S} | {texto}")

    def atribuir_tecnico(self, tecnico):
        self.tecnico = tecnico
        self._registrar(f"Técnico atribuído: {tecnico.nome}.")

    def alterar_prioridade(self, prioridade):
        if prioridade not in self.PRIORIDADES:
            raise ValueError("Prioridade inválida.")
        self.__prioridade = prioridade
        self._registrar(f"Prioridade alterada para {prioridade}.")

    def registrar_atendimento(self, observacao):
        if not self.tecnico:
            raise RuntimeError("Atribua um técnico antes do atendimento.")
        self.__status = "Em atendimento"
        self._registrar(f"Atendimento: {observacao}")

    def encerrar(self):
        self.__status = "Encerrado"
        self._registrar("Chamado encerrado.")

    @property
    def status(self):
        # O status privado pode ser lido, mas suas mudancas passam pelos metodos.
        return self.__status


class CentralSuporte:
    def __init__(self):
        self.chamados = []

    def abrir_chamado(self, chamado):
        self.chamados.append(chamado)

    def listar_por_status(self, status):
        return [c for c in self.chamados if c.status == status]


if __name__ == "__main__":
    central = CentralSuporte()
    chamado = Chamado(1, "Computador não liga", "Alta", Usuario("Maria"))
    central.abrir_chamado(chamado)
    chamado.atribuir_tecnico(Tecnico("João"))
    chamado.registrar_atendimento("Fonte de alimentação verificada.")
    chamado.encerrar()

    print("\n".join(chamado.historico))
