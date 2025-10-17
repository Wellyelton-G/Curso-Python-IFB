# ===== Model =====
class Tarefa:
    # Classe que representa uma tarefa da lista
    def __init__(self, descricao):
        # Construtor: recebe a descrição da tarefa
        self.descricao = descricao
        self.concluida = False  # Por padrão, a tarefa começa como não concluída

    def marcar_concluida(self):
        # Método para marcar a tarefa como concluída
        self.concluida = True

    def __str__(self):
        # Método especial para mostrar a tarefa de forma amigável
        status = "Concluída" if self.concluida else "Não concluída"
        return f"{status} {self.descricao}"

# Singleton para gerenciar tarefas
class BancoDeDadosTarefas:
    # Esta classe garante que só existe uma instância (objeto) dela em todo o programa
    _instancia = None  # Variável de classe para guardar a instância única

    def __new__(cls):
        
        """
        Cria e retorna uma instância singleton da classe.
        Este método especial é chamado ao criar um novo objeto. Se uma instância da classe ainda não existir,
        ele cria uma e inicializa seus atributos (`tarefas` como uma lista vazia e `observers` como uma lista vazia).
        Chamadas subsequentes sempre retornarão a mesma instância, garantindo o padrão singleton.
        Retorna:
            cls._instancia: A instância singleton da classe.
        """
        
        # Método especial chamado ao criar um novo objeto
        if cls._instancia is None:
            # Se ainda não existe, cria e inicializa atributos
            cls._instancia = super().__new__(cls)
            cls._instancia.tarefas = []    # Lista de tarefas
            cls._instancia.observers = []  # Lista de observadores (Views)
        return cls._instancia  # Sempre retorna a mesma instância

    def adicionar_tarefa(self, tarefa):
        # Adiciona uma nova tarefa à lista
        self.tarefas.append(tarefa)
        self.notificar_observers()  # Notifica a View que houve mudança

    def marcar_concluida(self, indice):
        # Marca uma tarefa como concluída pelo índice
        if 0 <= indice < len(self.tarefas):
            self.tarefas[indice].marcar_concluida()
            self.notificar_observers()  # Notifica a View que houve mudança
            return True
        return False

    def listar_tarefas(self):
        # Retorna a lista de tarefas
        return self.tarefas

    # Observer: registro e notificação
    def registrar_observer(self, observer):
        # Adiciona uma View à lista de observadores
        self.observers.append(observer)

    def notificar_observers(self):
        # Chama o método atualizar de cada View registrada
        for obs in self.observers:
            obs.atualizar(self.tarefas)

# ===== View =====
class TarefaView:
    # Classe responsável por mostrar informações no terminal

    def atualizar(self, tarefas):
        # Método chamado automaticamente quando o modelo muda (Observer)
        print("\nLista de Tarefas Atualizada:")
        if not tarefas:
            print("Nenhuma tarefa cadastrada.")
        else:
            for idx, tarefa in enumerate(tarefas, 1):
                print(f"{idx}. {tarefa}")

    @staticmethod
    def mostrar_mensagem(msg):
        # Método para mostrar mensagens simples
        print(msg)

# ===== Controller =====
class TarefaController:
    # Classe que recebe comandos do usuário e coordena ações entre Model e View
    def __init__(self, modelo, view):
        self.modelo = modelo  # Referência ao Model (BancoDeDadosTarefas)
        self.view = view      # Referência à View (TarefaView)
        self.modelo.registrar_observer(self.view)  # Registra a View como observadora

    def adicionar_tarefa(self, descricao):
        # Adiciona uma nova tarefa
        tarefa = Tarefa(descricao)
        self.modelo.adicionar_tarefa(tarefa)
        self.view.mostrar_mensagem("Tarefa adicionada com sucesso!")

    def marcar_concluida(self, indice):
        # Marca uma tarefa como concluída
        if self.modelo.marcar_concluida(indice):
            self.view.mostrar_mensagem("Tarefa marcada como concluída!")
        else:
            self.view.mostrar_mensagem("Índice inválido.")

    def listar_tarefas(self):
        # Mostra a lista de tarefas
        tarefas = self.modelo.listar_tarefas()
        self.view.atualizar(tarefas)

# ===== Menu Principal =====
def menu():
    # Função principal que exibe o menu e controla o fluxo do programa
    modelo = BancoDeDadosTarefas()  # Cria (ou recupera) a instância única do banco de tarefas
    view = TarefaView()             # Cria a View
    controller = TarefaController(modelo, view)  # Cria o Controller e conecta tudo

    while True:
        print("\n=== Sistema de Lista de Tarefas ===")
        print("1 - Adicionar nova tarefa")
        print("2 - Listar todas as tarefas")
        print("3 - Marcar tarefa como concluída")
        print("4 - Sair")
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "1":
            desc = input("Digite a descrição da tarefa: ").strip()
            controller.adicionar_tarefa(desc)
        elif opcao == "2":
            controller.listar_tarefas()
        elif opcao == "3":
            controller.listar_tarefas()
            try:
                idx = int(input("Digite o número da tarefa a marcar como concluída: ")) - 1
                controller.marcar_concluida(idx)
            except ValueError:
                view.mostrar_mensagem("Entrada inválida.")
        elif opcao == "4":
            print("Saindo do sistema. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Este bloco garante que o menu só será executado se o arquivo for rodado diretamente
if __name__ == "__main__":
    menu()