"""Questao 24 - Sistema de controle hospitalar.

O exemplo destaca heranca entre pessoas, composicao entre paciente e
prontuario, associacao nas consultas e controle de acesso por tipo de objeto.
"""

from datetime import datetime


class ConflitoAgendaError(Exception):
    """O mesmo medico nao pode atender duas consultas no mesmo horario."""


class AcessoNaoAutorizadoError(Exception):
    """Protege dados clinicos contra leitura ou alteracao indevida."""


class CadastroDuplicadoError(Exception):
    """Identificadores profissionais e documentos devem ser unicos."""


class Pessoa:
    """Classe-base com os dados comuns a todas as pessoas."""

    def __init__(self, nome, identificador):
        self.nome = nome
        self.identificador = str(identificador)


class Paciente(Pessoa):
    def __init__(self, nome, documento):
        super().__init__(nome, documento)
        # Composicao: o prontuario pertence exclusivamente a este paciente e
        # nasce no mesmo momento que ele.
        self.prontuario = Prontuario(self)


class Medico(Pessoa):
    def __init__(self, nome, crm):
        super().__init__(nome, crm)
        self.crm = self.identificador


class Enfermeiro(Pessoa):
    def __init__(self, nome, coren):
        super().__init__(nome, coren)
        self.coren = self.identificador


class Prescricao:
    def __init__(self, medicamento, orientacao):
        self.medicamento = medicamento
        self.orientacao = orientacao

    def __str__(self):
        return f"{self.medicamento}: {self.orientacao}"


class Prontuario:
    """Encapsula os registros para impedir acesso direto indiscriminado."""

    def __init__(self, paciente):
        self.__paciente = paciente
        self.__registros = []

    @property
    def paciente(self):
        return self.__paciente

    def adicionar_diagnostico(self, profissional, diagnostico):
        # isinstance considera Medico e eventuais subclasses de Medico.
        if not isinstance(profissional, Medico):
            raise AcessoNaoAutorizadoError(
                "Apenas medicos podem registrar diagnosticos."
            )
        self.__registros.append(
            {
                "data": datetime.now(),
                "medico": profissional.nome,
                "diagnostico": diagnostico,
            }
        )

    # Mantemos este nome como atalho para facilitar o estudo da versao anterior.
    def adicionar_registro(self, profissional, texto):
        self.adicionar_diagnostico(profissional, texto)

    def consultar(self, profissional):
        # Medicos podem escrever e ler; enfermeiros possuem acesso somente para
        # consulta. Outros tipos de pessoa nao recebem os dados clinicos.
        if not isinstance(profissional, (Medico, Enfermeiro)):
            raise AcessoNaoAutorizadoError("Profissional sem permissao.")
        return [dict(registro) for registro in self.__registros]


class Consulta:
    """Associacao entre um paciente e um medico em determinado horario."""

    def __init__(self, paciente, medico, horario):
        self.paciente = paciente
        self.medico = medico
        self.horario = horario
        self.prescricoes = []

    def registrar_diagnostico(self, profissional, diagnostico):
        if profissional is not self.medico:
            raise AcessoNaoAutorizadoError(
                "Somente o medico da consulta pode registrar o diagnostico."
            )
        self.paciente.prontuario.adicionar_diagnostico(profissional, diagnostico)

    def adicionar_prescricao(self, profissional, prescricao):
        if profissional is not self.medico:
            raise AcessoNaoAutorizadoError(
                "Somente o medico da consulta pode prescrever."
            )
        self.prescricoes.append(prescricao)


class Hospital:
    """Fachada que oferece as operacoes solicitadas no enunciado."""

    def __init__(self):
        # Dicionarios permitem localizar cadastros por documento, CRM ou COREN.
        self.pacientes = {}
        self.medicos = {}
        self.enfermeiros = {}
        self.consultas = []

    @staticmethod
    def _cadastrar(colecao, pessoa):
        if pessoa.identificador in colecao:
            raise CadastroDuplicadoError("Identificador ja cadastrado.")
        colecao[pessoa.identificador] = pessoa
        return pessoa

    def cadastrar_paciente(self, paciente):
        return self._cadastrar(self.pacientes, paciente)

    def cadastrar_medico(self, medico):
        return self._cadastrar(self.medicos, medico)

    def cadastrar_enfermeiro(self, enfermeiro):
        return self._cadastrar(self.enfermeiros, enfermeiro)

    def agendar(self, paciente, medico, horario):
        if paciente.identificador not in self.pacientes:
            raise ValueError("Paciente nao cadastrado.")
        if medico.identificador not in self.medicos:
            raise ValueError("Medico nao cadastrado.")

        # Duas consultas de pacientes diferentes ainda conflitam se o medico e
        # o horario forem os mesmos.
        for consulta in self.consultas:
            if consulta.medico is medico and consulta.horario == horario:
                raise ConflitoAgendaError(
                    "O medico ja possui consulta nesse horario."
                )
        consulta = Consulta(paciente, medico, horario)
        self.consultas.append(consulta)
        return consulta

    def historico_paciente(self, paciente):
        return [item for item in self.consultas if item.paciente is paciente]


if __name__ == "__main__":
    hospital = Hospital()
    paciente = hospital.cadastrar_paciente(Paciente("Ana", "CPF123"))
    medico = hospital.cadastrar_medico(Medico("Dr. Carlos", "CRM123"))
    enfermeiro = hospital.cadastrar_enfermeiro(Enfermeiro("Bia", "COREN10"))

    consulta = hospital.agendar(
        paciente, medico, datetime(2026, 7, 30, 10, 0)
    )
    consulta.registrar_diagnostico(medico, "Diagnostico de exemplo.")
    consulta.adicionar_prescricao(
        medico, Prescricao("Medicamento A", "1 vez ao dia")
    )
    print(paciente.prontuario.consultar(enfermeiro))
