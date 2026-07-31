"""Questao 22 - Plataforma de cursos com avaliacao.

O exemplo foi dividido em pequenas classes para mostrar que cada objeto deve
ter uma responsabilidade. A plataforma organiza os cadastros; as regras de
progresso e certificacao pertencem a Matricula, pois variam de aluno para
aluno dentro de cada curso.
"""

from abc import ABC, abstractmethod


class ProgressoInsuficienteError(Exception):
    """Indica que o aluno tentou avaliar antes de concluir 70% do curso."""


class MatriculaDuplicadaError(Exception):
    """Impede que o mesmo aluno seja matriculado duas vezes no mesmo curso."""


class PermissaoNegadaError(Exception):
    """Usada quando um professor tenta alterar o curso de outro professor."""


class Usuario(ABC):
    """Abstracao comum a alunos e professores.

    O decorador @abstractmethod torna a classe realmente abstrata. Portanto,
    Usuario nao pode ser instanciado diretamente: somente suas subclasses.
    """

    def __init__(self, nome, email):
        self.nome = nome
        self.email = email

    @abstractmethod
    def exibir_perfil(self):
        """Cada tipo de usuario deve apresentar seu perfil de modo proprio."""


class Professor(Usuario):
    def __init__(self, nome, email):
        super().__init__(nome, email)
        self.cursos = []

    def exibir_perfil(self):
        return f"Professor {self.nome} - {len(self.cursos)} curso(s)"

    def criar_curso(self, titulo):
        curso = Curso(titulo, self)
        self.cursos.append(curso)
        return curso

    def criar_aula(self, curso, titulo):
        # A verificacao mantem a regra dentro do modelo, e nao apenas no menu.
        if curso.professor is not self:
            raise PermissaoNegadaError("O professor so pode alterar seus cursos.")
        aula = Aula(titulo)
        curso.adicionar_aula(aula)
        return aula


class Aluno(Usuario):
    def __init__(self, nome, email):
        super().__init__(nome, email)
        # Esta lista tambem funciona como historico de matriculas do aluno.
        self.matriculas = []

    def exibir_perfil(self):
        return f"Aluno {self.nome} - {len(self.matriculas)} matricula(s)"

    def matricular(self, curso):
        if any(item.curso is curso for item in self.matriculas):
            raise MatriculaDuplicadaError("Aluno ja matriculado neste curso.")
        matricula = Matricula(self, curso)
        # A associacao e registrada nos dois sentidos para facilitar consultas.
        self.matriculas.append(matricula)
        curso.matriculas.append(matricula)
        return matricula

    def historico_matriculas(self):
        return [
            {
                "curso": item.curso.titulo,
                "progresso": item.progresso(),
                "media": item.media(),
                "certificado": item.certificado_emitido,
            }
            for item in self.matriculas
        ]


class Aula:
    def __init__(self, titulo):
        self.titulo = titulo


class Curso:
    def __init__(self, titulo, professor):
        self.titulo = titulo
        self.professor = professor
        # Composicao: as aulas formam o conteudo deste curso.
        self.aulas = []
        self.matriculas = []

    def adicionar_aula(self, aula):
        self.aulas.append(aula)


class Avaliacao:
    def __init__(self, titulo, nota):
        if not 0 <= nota <= 10:
            raise ValueError("A nota deve estar entre 0 e 10.")
        self.titulo = titulo
        self.nota = float(nota)


class Matricula:
    """Relaciona um Aluno a um Curso e guarda seu desempenho individual."""

    def __init__(self, aluno, curso):
        self.aluno = aluno
        self.curso = curso
        # set evita registrar a conclusao da mesma aula mais de uma vez.
        self.aulas_concluidas = set()
        self.avaliacoes = []
        self.certificado_emitido = False

    def concluir_aula(self, aula):
        if aula not in self.curso.aulas:
            raise ValueError("A aula nao pertence ao curso.")
        self.aulas_concluidas.add(aula)

    def progresso(self):
        if not self.curso.aulas:
            return 0.0
        return len(self.aulas_concluidas) / len(self.curso.aulas) * 100

    def realizar_avaliacao(self, avaliacao):
        if self.progresso() < 70:
            raise ProgressoInsuficienteError(
                "E necessario concluir ao menos 70% do curso."
            )
        self.avaliacoes.append(avaliacao)

    def media(self):
        if not self.avaliacoes:
            return 0.0
        return sum(item.nota for item in self.avaliacoes) / len(self.avaliacoes)

    def emitir_certificado(self):
        # Exigimos todo o conteudo e media minima 6 para considerar aprovacao.
        if self.progresso() == 100 and self.media() >= 6:
            self.certificado_emitido = True
            return f"Certificado emitido para {self.aluno.nome}."
        return "Requisitos para certificacao nao atendidos."


class PlataformaCursos:
    """Fachada que centraliza os cadastros da aplicacao."""

    def __init__(self):
        self.usuarios = []
        self.cursos = []

    def cadastrar_usuario(self, usuario):
        if any(item.email == usuario.email for item in self.usuarios):
            raise ValueError("E-mail ja cadastrado.")
        self.usuarios.append(usuario)

    def publicar_curso(self, professor, titulo):
        curso = professor.criar_curso(titulo)
        self.cursos.append(curso)
        return curso


if __name__ == "__main__":
    plataforma = PlataformaCursos()
    professor = Professor("Carlos", "prof@exemplo.com")
    aluno = Aluno("Ana", "ana@exemplo.com")
    plataforma.cadastrar_usuario(professor)
    plataforma.cadastrar_usuario(aluno)

    curso = plataforma.publicar_curso(professor, "POO em Python")
    aulas = [professor.criar_aula(curso, f"Aula {i}") for i in range(1, 4)]
    matricula = aluno.matricular(curso)
    for aula in aulas:
        matricula.concluir_aula(aula)

    matricula.realizar_avaliacao(Avaliacao("Prova final", 8.5))
    print(aluno.exibir_perfil())  # mesma operacao, resultado polimorfico
    print(f"Progresso: {matricula.progresso():.0f}%")
    print(matricula.emitir_certificado())
