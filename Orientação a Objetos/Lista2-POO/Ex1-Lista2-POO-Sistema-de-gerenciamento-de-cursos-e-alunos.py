# Classe que representa um aluno
# A palavra-chave 'class' é usada para definir uma nova classe em Python.
# Classes são estruturas que agrupam dados e comportamentos (funções) relacionados a um objeto.
class Aluno:
    
    # Método especial __init__ é o construtor da classe. Ele é executado sempre que criamos um novo objeto do tipo Aluno.
    # O parâmetro 'self' representa o próprio objeto que está sendo criado.
    def __init__(self, nome):
        self.nome = nome              # Armazena o nome do aluno. 'self.nome' é um atributo do objeto.
        self.cursos = []              # Cria uma lista vazia que guardará os cursos em que esse aluno está matriculado.
        # [] cria uma lista em Python. Uma lista é uma estrutura que pode armazenar vários elementos.

    # Método que permite matricular o aluno em um curso
    def matricular(self, curso):
        # Verifica se o curso ainda não está na lista de cursos do aluno usando o operador 'not in'
        if curso not in self.cursos:
            self.cursos.append(curso)         # Adiciona o curso à lista do aluno. append() insere um elemento no final da lista.
            curso.adicionar_aluno(self)       # Também adiciona o aluno na lista de alunos do curso (relação bidirecional).

    # Método que define como o aluno será exibido ao ser impresso com print()
    def __str__(self):
        # Cria uma string com os nomes dos cursos usando list comprehension e o método join()
        # [curso.nome for curso in self.cursos] → cria uma lista com os nomes dos cursos
        # ', '.join(lista) → junta os elementos da lista em uma única string, separados por vírgula
        cursos_nomes = ', '.join([curso.nome for curso in self.cursos]) if self.cursos else "Nenhum"
        return f"Aluno: {self.nome} | Cursos: {cursos_nomes}"
        # f-string → permite incorporar variáveis dentro de uma string com {variavel}
        # Exemplo: f"Olá {nome}" vira "Olá Ana" se nome = "Ana"

# Classe que representa um curso
class Curso:
    def __init__(self, nome):
        self.nome = nome              # Atributo que armazena o nome do curso
        self.alunos = []              # Lista que vai guardar os objetos do tipo Aluno matriculados neste curso

    def adicionar_aluno(self, aluno):
        if aluno not in self.alunos:              # Só adiciona se o aluno ainda não estiver matriculado
            self.alunos.append(aluno)             # append() adiciona o aluno na lista de alunos

    def __str__(self):
        alunos_nomes = ', '.join([aluno.nome for aluno in self.alunos]) if self.alunos else "Nenhum"
        return f"Curso: {self.nome} | Alunos: {alunos_nomes}"


# Função que mostra o menu na tela
# A palavra-chave 'def' é usada para definir uma função em Python.
def menu():
    print("\nMenu:")                              # \n cria uma quebra de linha
    print("1 - Listar alunos")
    print("2 - Listar cursos")
    print("3 - Matricular aluno em curso")
    print("4 - Ver cursos de um aluno")
    print("5 - Cadastrar novo aluno")
    print("6 - Cadastrar novo curso")
    print("7 - Sair")


# Bloco principal do programa. Esse código só será executado se o arquivo for rodado diretamente.
# '__name__ == "__main__"' é uma forma de dizer "execute o que está aqui apenas se o script for o principal"
if __name__ == "__main__":
    
    # Criando uma lista de objetos da classe Curso
    cursos = [
        Curso("Python"),
        Curso("Java"),
        Curso("HTML")
    ]

    # Criando uma lista de objetos da classe Aluno
    alunos = [
        Aluno("Ana"),
        Aluno("Bruno"),
        Aluno("Carla")
    ]

    # Loop infinito para manter o programa funcionando até o usuário escolher sair
    while True:
        menu()  # Mostra o menu
        opcao = input("Escolha uma opção: ")  # input() recebe o valor digitado como string

        if opcao == "1":
            # Lista todos os alunos
            print("\nAlunos:")
            for idx, aluno in enumerate(alunos):
                # enumerate() retorna o índice (posição) e o valor de cada item da lista
                # idx começa do 0, por isso usamos idx+1 para mostrar a numeração a partir do 1
                print(f"{idx+1} - {aluno.nome}")  # Mostra o nome do aluno com numeração

        elif opcao == "2":
            # Lista todos os cursos
            print("\nCursos:")
            for idx, curso in enumerate(cursos):
                print(f"{idx+1} - {curso.nome}")

        elif opcao == "3":
            # Matricular aluno em curso
            print("\nAlunos:")
            for idx, aluno in enumerate(alunos):
                print(f"{idx+1} - {aluno.nome}")
            aluno_idx = int(input("Escolha o número do aluno: ")) - 1
            # int() converte o que foi digitado (string) para inteiro

            print("\nCursos:")
            for idx, curso in enumerate(cursos):
                print(f"{idx+1} - {curso.nome}")
            curso_idx = int(input("Escolha o número do curso: ")) - 1

            # Verifica se os índices digitados estão dentro dos limites da lista
            if 0 <= aluno_idx < len(alunos) and 0 <= curso_idx < len(cursos):
                alunos[aluno_idx].matricular(cursos[curso_idx])
                print(f"{alunos[aluno_idx].nome} matriculado em {cursos[curso_idx].nome}!")
            else:
                print("Opção inválida.")

        elif opcao == "4":
            # Ver cursos em que um aluno está matriculado
            print("\nAlunos:")
            for idx, aluno in enumerate(alunos):
                print(f"{idx+1} - {aluno.nome}")
            aluno_idx = int(input("Escolha o número do aluno: ")) - 1

            if 0 <= aluno_idx < len(alunos):
                print(alunos[aluno_idx])  # Imprime a representação completa do aluno
            else:
                print("Opção inválida.")

        elif opcao == "5":
            # Cadastro de novo aluno
            nome = input("Digite o nome do novo aluno: ")  # input() lê o nome digitado
            alunos.append(Aluno(nome))                     # Cria novo objeto Aluno e adiciona à lista
            print(f"Aluno '{nome}' cadastrado com sucesso!")

        elif opcao == "6":
            # Cadastro de novo curso
            nome = input("Digite o nome do novo curso: ")
            cursos.append(Curso(nome))                     # Cria novo objeto Curso e adiciona à lista
            print(f"Curso '{nome}' cadastrado com sucesso!")

        elif opcao == "7":
            # Encerra o programa com break
            print("Saindo...")
            break

        else:
            # Caso o usuário digite uma opção que não existe
            print("Opção inválida.")
