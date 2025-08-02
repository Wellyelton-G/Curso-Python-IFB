def adicionar_tarefa(tarefas):
    tarefa = input("Digite a descrição da tarefa: ")
    tarefas.append(tarefa)
    print(f"Tarefa '{tarefa}' adicionada com sucesso!")

    if not tarefas:
        print("Nenhuma tarefa cadastrada.")
    else:
        print("Lista de tarefas:")
        for idx, tarefa in enumerate(tarefas, 1):
            print(f"{idx}. {tarefa}")

def remover_tarefa(tarefas):
    listar_tarefas(tarefas)
    try:
        tarefa_id = int(input("Digite o número da tarefa a ser removida: "))
        if 1 <= tarefa_id <= len(tarefas):
            tarefa_removida = tarefas.pop(tarefa_id - 1)
            print(f"Tarefa '{tarefa_removida}' removida com sucesso!")
        else:
            print("Número inválido. Nenhuma tarefa foi removida.")
    except ValueError:
        print("Valor inválido. Por favor, insira um número válido.")

def menu():
    tarefas = []
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
            listar_tarefas(tarefas) # type: ignore
        elif opcao == '3':
            remover_tarefa(tarefas)
        elif opcao == '4':
            print("Saindo do programa...")
            break
    else:
            print("Opção inválida. Tente novamente.")

# Chama a função menu para execução
menu()