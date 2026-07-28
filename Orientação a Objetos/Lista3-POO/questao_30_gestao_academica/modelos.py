from abc import ABC, abstractmethod
from excecoes import MatriculaDuplicadaError, PermissaoNegadaError


class Pessoa(ABC):
    """Classe abstrata. Não pode ser instanciada diretamente."""

    def __init__(self, nome):
        self.nome = nome

    @abstractmethod
    def tipo(self):
        pass


class Aluno(Pessoa):
    matriculas_usadas = set()

    def __init__(self, nome, matricula):
        super().__init__(nome)
        if matricula in self.matriculas_usadas:
            raise MatriculaDuplicadaError("A matrícula deve ser única.")
        self.__matricula = matricula
        self.matriculas_usadas.add(matricula)
        self.matriculas = []

    @property
    def matricula(self):
        return self.__matricula

    def tipo(self):
        return "Aluno"


class Professor(Pessoa):
    def __init__(self, nome):
        super().__init__(nome)
        self.turmas = []

    def tipo(self):
        return "Professor"

    def registrar_nota(self, turma, aluno, valor):
        if turma not in self.turmas:
            raise PermissaoNegadaError("O professor só pode registrar notas em suas próprias turmas.")
        turma.registrar_avaliacao(aluno, valor)

    def registrar_frequencia(self, turma, aluno, percentual):
        if turma not in self.turmas:
            raise PermissaoNegadaError("O professor só pode registrar frequência em suas próprias turmas.")
        turma.registrar_frequencia(aluno, percentual)


class Coordenador(Pessoa):
    def tipo(self):
        return "Coordenador"

    def criar_curso(self, nome):
        return Curso(nome)

    def criar_disciplina(self, codigo, nome):
        return Disciplina(codigo, nome)

    def criar_turma(self, codigo, disciplina, professor):
        return Turma(codigo, disciplina, professor)


class Disciplina:
    def __init__(self, codigo, nome):
        self.codigo = codigo
        self.nome = nome


class Curso:
    def __init__(self, nome):
        self.nome = nome
        self.disciplinas = []

    def adicionar_disciplina(self, disciplina):
        self.disciplinas.append(disciplina)


class Avaliacao:
    def __init__(self, valor):
        if not 0 <= valor <= 10:
            raise ValueError("A nota deve estar entre 0 e 10.")
        self.valor = valor


class Frequencia:
    def __init__(self, percentual):
        if not 0 <= percentual <= 100:
            raise ValueError("A frequência deve estar entre 0 e 100.")
        self.percentual = percentual


class Matricula:
    def __init__(self, aluno, turma):
        self.aluno = aluno
        self.turma = turma
        self.avaliacoes = []
        self.frequencia = Frequencia(0)

    def media_final(self):
        if not self.avaliacoes:
            return 0
        return sum(a.valor for a in self.avaliacoes) / len(self.avaliacoes)

    def situacao(self):
        if self.frequencia.percentual < 75:
            return "Reprovado por falta"
        return "Aprovado" if self.media_final() >= 6 else "Reprovado por nota"


class Turma:
    def __init__(self, codigo, disciplina, professor):
        self.codigo = codigo
        self.disciplina = disciplina
        self.professor = professor
        self.matriculas = []
        professor.turmas.append(self)

    def matricular_aluno(self, aluno):
        matricula = Matricula(aluno, self)
        self.matriculas.append(matricula)
        aluno.matriculas.append(matricula)
        return matricula

    def _localizar(self, aluno):
        for matricula in self.matriculas:
            if matricula.aluno is aluno:
                return matricula
        raise ValueError("Aluno não está matriculado na turma.")

    def registrar_avaliacao(self, aluno, valor):
        self._localizar(aluno).avaliacoes.append(Avaliacao(valor))

    def registrar_frequencia(self, aluno, percentual):
        self._localizar(aluno).frequencia = Frequencia(percentual)


class HistoricoEscolar:
    def __init__(self, aluno):
        self.aluno = aluno

    def gerar(self):
        linhas = [f"Histórico de {self.aluno.nome}, matrícula {self.aluno.matricula}"]
        for matricula in self.aluno.matriculas:
            linhas.append(
                f"{matricula.turma.disciplina.nome} | "
                f"Média: {matricula.media_final():.2f} | "
                f"Frequência: {matricula.frequencia.percentual:.1f}% | "
                f"Situação: {matricula.situacao()}"
            )
        return "\n".join(linhas)
