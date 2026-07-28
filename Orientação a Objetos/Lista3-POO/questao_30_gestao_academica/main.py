from modelos import Aluno, Professor, Coordenador, HistoricoEscolar
from persistencia import RepositorioAcademico


def demonstracao():
    coordenador = Coordenador("Carla")
    professor = Professor("Paulo")
    aluno = Aluno("Ana", "2026001")

    curso = coordenador.criar_curso("Tecnologia em Sistemas")
    disciplina = coordenador.criar_disciplina("POO101", "Programação Orientada a Objetos")
    curso.adicionar_disciplina(disciplina)

    turma = coordenador.criar_turma("T1", disciplina, professor)
    turma.matricular_aluno(aluno)

    professor.registrar_nota(turma, aluno, 8.0)
    professor.registrar_nota(turma, aluno, 7.0)
    professor.registrar_frequencia(turma, aluno, 82)

    historico = HistoricoEscolar(aluno)
    print(historico.gerar())

    repositorio = RepositorioAcademico()
    repositorio.salvar({
        "aluno": {
            "nome": aluno.nome,
            "matricula": aluno.matricula,
            "historico": historico.gerar()
        }
    })


def menu():
    while True:
        print("\n1. Executar demonstração")
        print("2. Sair")
        opcao = input("Escolha: ")

        if opcao == "1":
            demonstracao()
        elif opcao == "2":
            print("Programa encerrado.")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()
