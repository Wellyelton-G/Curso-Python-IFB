from abc import ABC


class ProgressoInsuficienteError(Exception):
    pass


class Usuario(ABC):
    def __init__(self, nome, email):
        self.nome = nome
        self.email = email


class Professor(Usuario):
    def criar_curso(self, titulo):
        return Curso(titulo, self)

    def criar_aula(self, curso, titulo):
        aula = Aula(titulo)
        curso.aulas.append(aula)
        return aula


class Aluno(Usuario):
    def __init__(self, nome, email):
        super().__init__(nome, email)
        self.matriculas = []

    def matricular(self, curso):
        matricula = Matricula(self, curso)
        self.matriculas.append(matricula)
        curso.matriculas.append(matricula)
        return matricula


class Aula:
    def __init__(self, titulo):
        self.titulo = titulo


class Curso:
    def __init__(self, titulo, professor):
        self.titulo = titulo
        self.professor = professor
        self.aulas = []
        self.matriculas = []


class Avaliacao:
    def __init__(self, titulo, nota):
        if not 0 <= nota <= 10:
            raise ValueError("Nota inválida.")
        self.titulo = titulo
        self.nota = nota


class Matricula:
    def __init__(self, aluno, curso):
        self.aluno = aluno
        self.curso = curso
        self.aulas_concluidas = set()
        self.avaliacoes = []
        self.certificado_emitido = False

    def concluir_aula(self, aula):
        if aula not in self.curso.aulas:
            raise ValueError("A aula não pertence ao curso.")
        self.aulas_concluidas.add(aula)

    def progresso(self):
        if not self.curso.aulas:
            return 0
        return len(self.aulas_concluidas) / len(self.curso.aulas) * 100

    def realizar_avaliacao(self, avaliacao):
        if self.progresso() < 70:
            raise ProgressoInsuficienteError("É necessário concluir ao menos 70% do curso.")
        self.avaliacoes.append(avaliacao)

    def media(self):
        if not self.avaliacoes:
            return 0
        return sum(a.nota for a in self.avaliacoes) / len(self.avaliacoes)

    def emitir_certificado(self):
        if self.progresso() == 100 and self.media() >= 6:
            self.certificado_emitido = True
            return f"Certificado emitido para {self.aluno.nome}."
        return "Requisitos para certificação não atendidos."


if __name__ == "__main__":
    professor = Professor("Carlos", "prof@exemplo.com")
    curso = professor.criar_curso("POO em Python")
    aulas = [professor.criar_aula(curso, f"Aula {i}") for i in range(1, 4)]

    aluno = Aluno("Ana", "ana@exemplo.com")
    matricula = aluno.matricular(curso)
    for aula in aulas:
        matricula.concluir_aula(aula)

    matricula.realizar_avaliacao(Avaliacao("Prova final", 8.5))
    print(f"Progresso: {matricula.progresso():.0f}%")
    print(matricula.emitir_certificado())
