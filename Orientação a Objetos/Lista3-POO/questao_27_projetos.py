from datetime import date


class TransicaoInvalidaError(Exception):
    pass


class Usuario:
    def __init__(self, nome):
        self.nome = nome


class Gerente(Usuario):
    pass


class Desenvolvedor(Usuario):
    pass


class Comentario:
    def __init__(self, autor, texto):
        self.autor = autor
        self.texto = texto


class Tarefa:
    TRANSICOES = {
        "Pendente": {"Em andamento", "Cancelada"},
        "Em andamento": {"Em revisão", "Cancelada"},
        "Em revisão": {"Concluída", "Em andamento", "Cancelada"},
        "Concluída": set(),
        "Cancelada": set()
    }

    def __init__(self, titulo, descricao, responsavel, prazo, prioridade):
        self.titulo = titulo
        self.descricao = descricao
        self.responsavel = responsavel
        self.prazo = prazo
        self.prioridade = prioridade
        self.__status = "Pendente"
        self.comentarios = []

    @property
    def status(self):
        return self.__status

    def alterar_status(self, novo_status):
        if novo_status not in self.TRANSICOES[self.__status]:
            raise TransicaoInvalidaError(f"Não é possível passar de {self.__status} para {novo_status}.")
        self.__status = novo_status

    def adicionar_comentario(self, comentario):
        self.comentarios.append(comentario)

    def esta_atrasada(self):
        return self.__status not in {"Concluída", "Cancelada"} and date.today() > self.prazo


class Equipe:
    def __init__(self, nome):
        self.nome = nome
        self.membros = []

    def adicionar_membro(self, usuario):
        self.membros.append(usuario)


class Projeto:
    def __init__(self, nome, gerente, equipe):
        self.nome = nome
        self.gerente = gerente
        self.equipe = equipe
        self.tarefas = []

    def criar_tarefa(self, tarefa):
        self.tarefas.append(tarefa)

    def percentual_conclusao(self):
        if not self.tarefas:
            return 0
        concluidas = sum(t.status == "Concluída" for t in self.tarefas)
        return concluidas / len(self.tarefas) * 100

    def gerar_relatorio(self):
        linhas = [f"Projeto: {self.nome}", f"Conclusão: {self.percentual_conclusao():.1f}%"]
        for tarefa in self.tarefas:
            linhas.append(f"{tarefa.titulo}: {tarefa.status}")
        return "\n".join(linhas)


if __name__ == "__main__":
    gerente = Gerente("Ana")
    dev = Desenvolvedor("Bruno")
    equipe = Equipe("Equipe Python")
    equipe.adicionar_membro(dev)
    projeto = Projeto("Sistema Acadêmico", gerente, equipe)

    tarefa = Tarefa("Criar cadastro", "Implementar CRUD", dev, date(2026, 12, 1), "Alta")
    projeto.criar_tarefa(tarefa)
    tarefa.alterar_status("Em andamento")
    tarefa.alterar_status("Em revisão")
    tarefa.alterar_status("Concluída")
    print(projeto.gerar_relatorio())
