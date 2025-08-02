# Função para adicionar uma nova tarefa
def adicionar_tarefa(tarefas):
    tarefa = input("Digite a descrição da tarefa: ")
    tarefas.append(tarefa)
    print(f"Tarefa '{tarefa}' adicionada com sucesso!")

# Função para listar todas as tarefas
def listar_tarefas(tarefas):
    if not tarefas:
        print("Nenhuma tarefa cadastrada.")
    else:
        print("\nLista de tarefas:")
        for idx, tarefa in enumerate(tarefas, 1):
            print(f"{idx}. {tarefa}")

# Função para remover uma tarefa pelo nome
def remover_tarefa(tarefas):
    listar_tarefas(tarefas)
    if tarefas:
        try:
            tarefa_id = int(input("Digite o número da tarefa a ser removida: "))
            if 1 <= tarefa_id <= len(tarefas):
                tarefa_removida = tarefas.pop(tarefa_id - 1)
                print(f"Tarefa '{tarefa_removida}' removida com sucesso!")
            else:
                print("Número inválido. Nenhuma tarefa foi removida.")
        except ValueError:
            print("Valor inválido. Por favor, insira um número válido.")

# Função principal para exibir o menu e gerenciar as tarefas
def menu():
    tarefas = []  # Lista para armazenar as tarefas
    while True:
        print("\nEscolha uma opção:")
        print("1. Adicionar uma nova tarefa")
        print("2. Listar todas as tarefas")
        print("3. Remover uma tarefa pelo nome")
        print("4. Sair do programa")

        opcao = input("Digite o número correspondente à opção desejada: ")

        if opcao == '1':
            adicionar_tarefa(tarefas)
        elif opcao == '2':
            listar_tarefas(tarefas)
        elif opcao == '3':
            remover_tarefa(tarefas)
        elif opcao == '4':
            print("Saindo do programa...")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Chama a função principal para executar o programa
menu()
