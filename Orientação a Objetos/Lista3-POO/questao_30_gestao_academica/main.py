"""Menu interativo do sistema de gestao academica."""

from pathlib import Path

from excecoes import SistemaAcademicoError
from modelos import HistoricoEscolar
from persistencia import RepositorioAcademico


ARQUIVO_DADOS = Path(__file__).with_name("dados_academicos.json")


def ler(texto):
    valor = input(texto).strip()
    if not valor:
        raise ValueError("O campo nao pode ficar vazio.")
    return valor


def cadastrar_pessoa(sistema):
    print("\n1. Aluno  2. Professor  3. Coordenador")
    tipo = ler("Tipo: ")
    nome = ler("Nome: ")
    registro = ler("Matricula/registro: ")
    if tipo == "1":
        pessoa = sistema.cadastrar_aluno(nome, registro)
    elif tipo == "2":
        pessoa = sistema.cadastrar_professor(nome, registro)
    elif tipo == "3":
        pessoa = sistema.cadastrar_coordenador(nome, registro)
    else:
        raise ValueError("Tipo invalido.")
    print("Cadastrado:", pessoa.descricao())


def criar_curso(sistema):
    coordenador = sistema.obter(
        sistema.coordenadores, ler("Registro do coordenador: "), "Coordenador"
    )
    curso = sistema.adicionar_curso(coordenador, ler("Codigo: "), ler("Nome: "))
    print("Curso criado:", curso.nome)


def criar_disciplina(sistema):
    coordenador = sistema.obter(
        sistema.coordenadores, ler("Registro do coordenador: "), "Coordenador"
    )
    disciplina = sistema.adicionar_disciplina(
        coordenador,
        ler("Codigo: "),
        ler("Nome: "),
        int(ler("Carga horaria: ")),
    )
    print("Disciplina criada:", disciplina.nome)


def associar_disciplina(sistema):
    sistema.obter(
        sistema.coordenadores, ler("Registro do coordenador: "), "Coordenador"
    )
    curso = sistema.obter(sistema.cursos, ler("Codigo do curso: "), "Curso")
    disciplina = sistema.obter(
        sistema.disciplinas, ler("Codigo da disciplina: "), "Disciplina"
    )
    curso.adicionar_disciplina(disciplina)
    print("Disciplina adicionada ao curso.")


def criar_turma(sistema):
    coordenador = sistema.obter(
        sistema.coordenadores, ler("Registro do coordenador: "), "Coordenador"
    )
    codigo = ler("Codigo da turma: ")
    disciplina = sistema.obter(
        sistema.disciplinas, ler("Codigo da disciplina: "), "Disciplina"
    )
    professor = sistema.obter(
        sistema.professores, ler("Registro do professor: "), "Professor"
    )
    turma = sistema.adicionar_turma(coordenador, codigo, disciplina, professor)
    print("Turma criada:", turma.codigo)


def matricular_aluno(sistema):
    turma = sistema.obter(sistema.turmas, ler("Codigo da turma: "), "Turma")
    aluno = sistema.obter(sistema.alunos, ler("Matricula do aluno: "), "Aluno")
    turma.matricular_aluno(aluno)
    print("Aluno matriculado na turma.")


def registrar_nota(sistema):
    professor = sistema.obter(
        sistema.professores, ler("Registro do professor: "), "Professor"
    )
    turma = sistema.obter(sistema.turmas, ler("Codigo da turma: "), "Turma")
    aluno = sistema.obter(sistema.alunos, ler("Matricula do aluno: "), "Aluno")
    descricao = ler("Descricao da avaliacao: ")
    professor.registrar_nota(
        turma, aluno, float(ler("Nota (0 a 10): ")), descricao, float(ler("Peso: "))
    )
    print("Nota registrada. Media atual:", f"{turma.localizar_matricula(aluno).media_final:.2f}")


def registrar_frequencia(sistema):
    professor = sistema.obter(
        sistema.professores, ler("Registro do professor: "), "Professor"
    )
    turma = sistema.obter(sistema.turmas, ler("Codigo da turma: "), "Turma")
    aluno = sistema.obter(sistema.alunos, ler("Matricula do aluno: "), "Aluno")
    professor.registrar_frequencia(turma, aluno, float(ler("Frequencia (%): ")))
    print("Frequencia registrada.")


def exibir_historico(sistema):
    aluno = sistema.obter(sistema.alunos, ler("Matricula do aluno: "), "Aluno")
    print("\n" + HistoricoEscolar(aluno).gerar())


def listar_cadastros(sistema):
    print("\nALUNOS")
    for pessoa in sistema.alunos.values():
        print("-", pessoa.descricao())
    print("PROFESSORES")
    for pessoa in sistema.professores.values():
        print("-", pessoa.descricao())
    print("CURSOS")
    for curso in sistema.cursos.values():
        nomes = ", ".join(d.nome for d in curso.disciplinas) or "sem disciplinas"
        print(f"- {curso.codigo}: {curso.nome} ({nomes})")
    print("TURMAS")
    for turma in sistema.turmas.values():
        print(
            f"- {turma.codigo}: {turma.disciplina.nome}, "
            f"prof. {turma.professor.nome}, {len(turma.alunos)} aluno(s)"
        )


def mostrar_menu():
    print("""
=== SISTEMA DE GESTAO ACADEMICA ===
1. Cadastrar pessoa
2. Criar curso
3. Criar disciplina
4. Adicionar disciplina a curso
5. Criar turma
6. Matricular aluno em turma
7. Registrar nota
8. Registrar frequencia
9. Exibir historico escolar
10. Listar cadastros
11. Salvar dados
0. Salvar e sair
""")


def menu():
    repositorio = RepositorioAcademico(ARQUIVO_DADOS)
    sistema, aviso = repositorio.carregar()
    if aviso:
        print("Aviso:", aviso)

    acoes = {
        "1": cadastrar_pessoa,
        "2": criar_curso,
        "3": criar_disciplina,
        "4": associar_disciplina,
        "5": criar_turma,
        "6": matricular_aluno,
        "7": registrar_nota,
        "8": registrar_frequencia,
        "9": exibir_historico,
        "10": listar_cadastros,
    }
    while True:
        mostrar_menu()
        opcao = input("Escolha: ").strip()
        try:
            if opcao == "0":
                repositorio.salvar(sistema)
                print("Dados salvos. Programa encerrado.")
                break
            if opcao == "11":
                repositorio.salvar(sistema)
                print("Dados salvos com sucesso.")
            elif opcao in acoes:
                acoes[opcao](sistema)
            else:
                print("Opcao invalida.")
        except (SistemaAcademicoError, ValueError) as erro:
            print("Erro:", erro)
        except (EOFError, KeyboardInterrupt):
            print("\nOperacao cancelada. Use a opcao 0 para salvar e sair.")


if __name__ == "__main__":
    menu()
