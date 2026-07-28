from datetime import datetime


class ConflitoAgendaError(Exception):
    pass


class AcessoNaoAutorizadoError(Exception):
    pass


class Pessoa:
    def __init__(self, nome):
        self.nome = nome


class Paciente(Pessoa):
    def __init__(self, nome):
        super().__init__(nome)
        self.prontuario = Prontuario(self)


class Medico(Pessoa):
    def __init__(self, nome, crm):
        super().__init__(nome)
        self.crm = crm


class Enfermeiro(Pessoa):
    pass


class Prescricao:
    def __init__(self, medicamento, orientacao):
        self.medicamento = medicamento
        self.orientacao = orientacao


class Prontuario:
    def __init__(self, paciente):
        self.__paciente = paciente
        self.__registros = []

    def adicionar_registro(self, profissional, texto):
        if not isinstance(profissional, Medico):
            raise AcessoNaoAutorizadoError("Apenas médicos podem registrar diagnósticos.")
        self.__registros.append(texto)

    def consultar(self, profissional):
        if not isinstance(profissional, (Medico, Enfermeiro)):
            raise AcessoNaoAutorizadoError("Profissional sem permissão.")
        return list(self.__registros)


class Consulta:
    def __init__(self, paciente, medico, horario):
        self.paciente = paciente
        self.medico = medico
        self.horario = horario
        self.prescricoes = []

    def adicionar_prescricao(self, profissional, prescricao):
        if profissional is not self.medico:
            raise AcessoNaoAutorizadoError("Somente o médico da consulta pode prescrever.")
        self.prescricoes.append(prescricao)


class Hospital:
    def __init__(self):
        self.consultas = []

    def agendar(self, paciente, medico, horario):
        for consulta in self.consultas:
            if consulta.medico is medico and consulta.horario == horario:
                raise ConflitoAgendaError("O médico já possui consulta nesse horário.")
        consulta = Consulta(paciente, medico, horario)
        self.consultas.append(consulta)
        return consulta

    def historico_paciente(self, paciente):
        return [c for c in self.consultas if c.paciente is paciente]


if __name__ == "__main__":
    hospital = Hospital()
    paciente = Paciente("Ana")
    medico = Medico("Dr. Carlos", "CRM123")
    consulta = hospital.agendar(paciente, medico, datetime(2026, 7, 30, 10, 0))
    paciente.prontuario.adicionar_registro(medico, "Diagnóstico de exemplo.")
    consulta.adicionar_prescricao(medico, Prescricao("Medicamento A", "1 vez ao dia"))
    print(paciente.prontuario.consultar(medico))
