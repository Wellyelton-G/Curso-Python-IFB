"""Modelo de dominio do sistema de gestao academica."""

from abc import ABC, abstractmethod

from excecoes import (
    AlunoNaoMatriculadoError,
    CadastroDuplicadoError,
    DadosInvalidosError,
    EntidadeNaoEncontradaError,
    MatriculaDuplicadaError,
    PermissaoNegadaError,
)


class Pessoa(ABC):
    """Abstracao comum: por possuir metodo abstrato, nao pode ser instanciada."""

    def __init__(self, nome):
        if not str(nome).strip():
            raise DadosInvalidosError("O nome nao pode ficar vazio.")
        self._nome = str(nome).strip()  # encapsulamento

    @property
    def nome(self):
        return self._nome

    @abstractmethod
    def descricao(self):
        """Exemplo de polimorfismo nas subclasses."""


class Aluno(Pessoa):
    def __init__(self, nome, matricula):
        super().__init__(nome)
        self.__matricula = str(matricula).strip()
        if not self.__matricula:
            raise DadosInvalidosError("A matricula nao pode ficar vazia.")
        self.matriculas_turmas = []

    @property
    def matricula(self):
        return self.__matricula

    def descricao(self):
        return f"Aluno: {self.nome} ({self.matricula})"


class Professor(Pessoa):
    def __init__(self, nome, registro):
        super().__init__(nome)
        self.registro = str(registro).strip()
        self.turmas = []

    def descricao(self):
        return f"Professor: {self.nome} ({self.registro})"

    def _verificar_turma(self, turma):
        if turma.professor is not self or turma not in self.turmas:
            raise PermissaoNegadaError(
                "O professor so pode registrar dados em suas proprias turmas."
            )

    def registrar_nota(self, turma, aluno, nota, descricao="Avaliacao", peso=1):
        self._verificar_turma(turma)
        turma.localizar_matricula(aluno).adicionar_avaliacao(nota, descricao, peso)

    def registrar_frequencia(self, turma, aluno, percentual):
        self._verificar_turma(turma)
        turma.localizar_matricula(aluno).registrar_frequencia(percentual)


class Coordenador(Pessoa):
    def __init__(self, nome, registro):
        super().__init__(nome)
        self.registro = str(registro).strip()

    def descricao(self):
        return f"Coordenador: {self.nome} ({self.registro})"

    def criar_curso(self, codigo, nome):
        return Curso(codigo, nome)

    def criar_disciplina(self, codigo, nome, carga_horaria):
        return Disciplina(codigo, nome, carga_horaria)

    def criar_turma(self, codigo, disciplina, professor):
        return Turma(codigo, disciplina, professor)


class Disciplina:
    def __init__(self, codigo, nome, carga_horaria):
        self.codigo = str(codigo).strip()
        self.nome = str(nome).strip()
        self.carga_horaria = int(carga_horaria)
        if not self.codigo or not self.nome or self.carga_horaria <= 0:
            raise DadosInvalidosError("Dados da disciplina invalidos.")


class Curso:
    """Agrega disciplinas, que podem existir independentemente do curso."""

    def __init__(self, codigo, nome):
        self.codigo = str(codigo).strip()
        self.nome = str(nome).strip()
        self.disciplinas = []
        if not self.codigo or not self.nome:
            raise DadosInvalidosError("Dados do curso invalidos.")

    def adicionar_disciplina(self, disciplina):
        if any(item.codigo == disciplina.codigo for item in self.disciplinas):
            raise CadastroDuplicadoError("Disciplina ja adicionada ao curso.")
        self.disciplinas.append(disciplina)


class Avaliacao:
    def __init__(self, valor, descricao="Avaliacao", peso=1):
        self.valor = float(valor)
        self.descricao = str(descricao).strip() or "Avaliacao"
        self.peso = float(peso)
        if not 0 <= self.valor <= 10:
            raise DadosInvalidosError("A nota deve estar entre 0 e 10.")
        if self.peso <= 0:
            raise DadosInvalidosError("O peso deve ser maior que zero.")


class Frequencia:
    def __init__(self, percentual=0):
        self.percentual = float(percentual)
        if not 0 <= self.percentual <= 100:
            raise DadosInvalidosError("A frequencia deve estar entre 0 e 100.")


class Matricula:
    """Compoe avaliacoes e frequencia; liga um aluno a uma turma."""

    def __init__(self, aluno, turma):
        self.aluno = aluno
        self.turma = turma
        self.avaliacoes = []
        self.frequencia = Frequencia()

    def adicionar_avaliacao(self, valor, descricao="Avaliacao", peso=1):
        self.avaliacoes.append(Avaliacao(valor, descricao, peso))

    def registrar_frequencia(self, percentual):
        self.frequencia = Frequencia(percentual)

    @property
    def media_final(self):
        if not self.avaliacoes:
            return 0.0
        total_pesos = sum(item.peso for item in self.avaliacoes)
        return sum(item.valor * item.peso for item in self.avaliacoes) / total_pesos

    @property
    def situacao(self):
        if self.frequencia.percentual < 75:
            return "Reprovado por falta"
        return "Aprovado" if self.media_final >= 6 else "Reprovado por nota"


class Turma:
    def __init__(self, codigo, disciplina, professor):
        self.codigo = str(codigo).strip()
        self.disciplina = disciplina
        self.professor = professor
        self.matriculas = []  # composicao: pertencem a esta turma
        if not self.codigo:
            raise DadosInvalidosError("O codigo da turma nao pode ficar vazio.")
        professor.turmas.append(self)

    @property
    def alunos(self):
        return [matricula.aluno for matricula in self.matriculas]

    def matricular_aluno(self, aluno):
        if aluno in self.alunos:
            raise MatriculaDuplicadaError("Aluno ja matriculado nesta turma.")
        matricula = Matricula(aluno, self)
        self.matriculas.append(matricula)
        aluno.matriculas_turmas.append(matricula)
        return matricula

    def localizar_matricula(self, aluno):
        for matricula in self.matriculas:
            if matricula.aluno is aluno:
                return matricula
        raise AlunoNaoMatriculadoError("Aluno nao matriculado nesta turma.")


class HistoricoEscolar:
    """Depende do aluno e de suas matriculas para produzir o relatorio."""

    def __init__(self, aluno):
        self.aluno = aluno

    def gerar(self):
        linhas = [f"Historico escolar - {self.aluno.nome} ({self.aluno.matricula})"]
        if not self.aluno.matriculas_turmas:
            linhas.append("Nenhuma disciplina cursada.")
        for item in self.aluno.matriculas_turmas:
            notas = ", ".join(f"{a.descricao}: {a.valor:.1f}" for a in item.avaliacoes)
            linhas.append(
                f"{item.turma.disciplina.nome} | Notas: {notas or 'sem notas'} | "
                f"Media: {item.media_final:.2f} | Frequencia: "
                f"{item.frequencia.percentual:.1f}% | Situacao: {item.situacao}"
            )
        return "\n".join(linhas)


class SistemaAcademico:
    """Fachada que mantem os cadastros e garante codigos unicos."""

    def __init__(self):
        self.alunos = {}
        self.professores = {}
        self.coordenadores = {}
        self.disciplinas = {}
        self.cursos = {}
        self.turmas = {}

    @staticmethod
    def _adicionar(colecao, chave, objeto, mensagem):
        if chave in colecao:
            raise CadastroDuplicadoError(mensagem)
        colecao[chave] = objeto
        return objeto

    def cadastrar_aluno(self, nome, matricula):
        chave = str(matricula).strip()
        if chave in self.alunos:
            raise MatriculaDuplicadaError("A matricula do aluno deve ser unica.")
        return self._adicionar(self.alunos, chave, Aluno(nome, chave), "Matricula duplicada.")

    def cadastrar_professor(self, nome, registro):
        chave = str(registro).strip()
        return self._adicionar(self.professores, chave, Professor(nome, chave), "Professor ja cadastrado.")

    def cadastrar_coordenador(self, nome, registro):
        chave = str(registro).strip()
        return self._adicionar(self.coordenadores, chave, Coordenador(nome, chave), "Coordenador ja cadastrado.")

    def adicionar_curso(self, coordenador, codigo, nome):
        curso = coordenador.criar_curso(codigo, nome)
        return self._adicionar(self.cursos, curso.codigo, curso, "Curso ja cadastrado.")

    def adicionar_disciplina(self, coordenador, codigo, nome, carga_horaria):
        disciplina = coordenador.criar_disciplina(codigo, nome, carga_horaria)
        return self._adicionar(self.disciplinas, disciplina.codigo, disciplina, "Disciplina ja cadastrada.")

    def adicionar_turma(self, coordenador, codigo, disciplina, professor):
        if codigo in self.turmas:
            raise CadastroDuplicadoError("Turma ja cadastrada.")
        turma = coordenador.criar_turma(codigo, disciplina, professor)
        self.turmas[turma.codigo] = turma
        return turma

    @staticmethod
    def obter(colecao, chave, tipo):
        try:
            return colecao[str(chave).strip()]
        except KeyError as erro:
            raise EntidadeNaoEncontradaError(f"{tipo} nao encontrado(a).") from erro
