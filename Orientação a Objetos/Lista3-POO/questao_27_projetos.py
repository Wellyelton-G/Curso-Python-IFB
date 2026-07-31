"""Questao 27 - Sistema de gerenciamento de projetos.

Este exercicio demonstra heranca nos usuarios, composicao no projeto,
encapsulamento do status e excecoes para proteger regras de negocio.
"""

from datetime import date


class TransicaoInvalidaError(Exception):
    """Impede que uma tarefa salte etapas nao permitidas."""


class ResponsavelInvalidoError(Exception):
    """Somente integrantes da equipe podem receber tarefas do projeto."""


class CadastroDuplicadoError(Exception):
    pass


class Usuario:
    def __init__(self, nome, email):
        self.nome = nome
        self.email = email

    def exibir_papel(self):
        return "Usuario"


class Gerente(Usuario):
    def exibir_papel(self):
        return "Gerente"


class Desenvolvedor(Usuario):
    def exibir_papel(self):
        return "Desenvolvedor"


class Comentario:
    def __init__(self, autor, texto, data_criacao=None):
        self.autor = autor
        self.texto = texto
        self.data_criacao = data_criacao or date.today()


class Tarefa:
    """Mantem seu status privado para evitar mudancas sem validacao."""

    TRANSICOES = {
        "Pendente": {"Em andamento", "Cancelada"},
        "Em andamento": {"Em revisao", "Cancelada"},
        "Em revisao": {"Concluida", "Em andamento", "Cancelada"},
        "Concluida": set(),
        "Cancelada": set(),
    }
    PRIORIDADES = {"Baixa", "Media", "Alta"}

    def __init__(self, titulo, descricao, responsavel, prazo, prioridade):
        if prioridade not in self.PRIORIDADES:
            raise ValueError("Prioridade invalida.")
        self.titulo = titulo
        self.descricao = descricao
        self.responsavel = responsavel
        self.prazo = prazo
        self.prioridade = prioridade
        self.__status = "Pendente"
        # Composicao: comentarios fazem parte do historico desta tarefa.
        self.comentarios = []

    @property
    def status(self):
        return self.__status

    def alterar_status(self, novo_status):
        permitidos = self.TRANSICOES[self.__status]
        if novo_status not in permitidos:
            raise TransicaoInvalidaError(
                f"Nao e possivel passar de {self.__status} para {novo_status}."
            )
        self.__status = novo_status

    def atribuir_responsavel(self, usuario):
        self.responsavel = usuario

    def adicionar_comentario(self, autor, texto):
        comentario = Comentario(autor, texto)
        self.comentarios.append(comentario)
        return comentario

    def esta_atrasada(self, hoje=None):
        hoje = hoje or date.today()
        estados_finais = {"Concluida", "Cancelada"}
        return self.__status not in estados_finais and hoje > self.prazo


class Equipe:
    def __init__(self, nome):
        self.nome = nome
        self.membros = []

    def adicionar_membro(self, usuario):
        if usuario in self.membros:
            raise CadastroDuplicadoError("Usuario ja pertence a equipe.")
        self.membros.append(usuario)

    def contem(self, usuario):
        return usuario in self.membros


class Projeto:
    """Compoe equipe e tarefas que colaboram para o mesmo objetivo."""

    def __init__(self, nome, gerente, equipe):
        self.nome = nome
        self.gerente = gerente
        self.equipe = equipe
        self.tarefas = []

        # O gerente tambem precisa ser reconhecido como membro do projeto.
        if not equipe.contem(gerente):
            equipe.adicionar_membro(gerente)

    def criar_tarefa(self, titulo, descricao, responsavel, prazo, prioridade):
        if not self.equipe.contem(responsavel):
            raise ResponsavelInvalidoError(
                "O responsavel precisa pertencer a equipe."
            )
        tarefa = Tarefa(titulo, descricao, responsavel, prazo, prioridade)
        self.tarefas.append(tarefa)
        return tarefa

    def atribuir_responsavel(self, tarefa, usuario):
        if tarefa not in self.tarefas:
            raise ValueError("A tarefa nao pertence ao projeto.")
        if not self.equipe.contem(usuario):
            raise ResponsavelInvalidoError(
                "O responsavel precisa pertencer a equipe."
            )
        tarefa.atribuir_responsavel(usuario)

    def tarefas_atrasadas(self, hoje=None):
        return [tarefa for tarefa in self.tarefas if tarefa.esta_atrasada(hoje)]

    def percentual_conclusao(self):
        if not self.tarefas:
            return 0.0
        concluidas = sum(tarefa.status == "Concluida" for tarefa in self.tarefas)
        return concluidas / len(self.tarefas) * 100

    def gerar_relatorio(self, hoje=None):
        linhas = [
            f"Projeto: {self.nome}",
            f"Gerente: {self.gerente.nome}",
            f"Conclusao: {self.percentual_conclusao():.1f}%",
        ]
        for tarefa in self.tarefas:
            atraso = " - ATRASADA" if tarefa.esta_atrasada(hoje) else ""
            linhas.append(
                f"{tarefa.titulo}: {tarefa.status} | "
                f"Responsavel: {tarefa.responsavel.nome}{atraso} | "
                f"Comentarios: {len(tarefa.comentarios)}"
            )
        return "\n".join(linhas)


class SistemaProjetos:
    """Camada de aplicacao que centraliza usuarios, equipes e projetos."""

    def __init__(self):
        self.usuarios = {}
        self.equipes = {}
        self.projetos = {}

    def cadastrar_usuario(self, usuario):
        if usuario.email in self.usuarios:
            raise CadastroDuplicadoError("E-mail ja cadastrado.")
        self.usuarios[usuario.email] = usuario

    def formar_equipe(self, nome, membros):
        if nome in self.equipes:
            raise CadastroDuplicadoError("Equipe ja cadastrada.")
        equipe = Equipe(nome)
        for membro in membros:
            equipe.adicionar_membro(membro)
        self.equipes[nome] = equipe
        return equipe

    def cadastrar_projeto(self, nome, gerente, equipe):
        if nome in self.projetos:
            raise CadastroDuplicadoError("Projeto ja cadastrado.")
        projeto = Projeto(nome, gerente, equipe)
        self.projetos[nome] = projeto
        return projeto


if __name__ == "__main__":
    sistema = SistemaProjetos()
    gerente = Gerente("Ana", "ana@empresa.com")
    dev = Desenvolvedor("Bruno", "bruno@empresa.com")
    sistema.cadastrar_usuario(gerente)
    sistema.cadastrar_usuario(dev)

    equipe = sistema.formar_equipe("Equipe Python", [gerente, dev])
    projeto = sistema.cadastrar_projeto("Sistema Academico", gerente, equipe)
    tarefa = projeto.criar_tarefa(
        "Criar cadastro", "Implementar CRUD", dev, date(2026, 12, 1), "Alta"
    )
    tarefa.adicionar_comentario(gerente, "Validar os campos obrigatorios.")
    tarefa.alterar_status("Em andamento")
    tarefa.alterar_status("Em revisao")
    tarefa.alterar_status("Concluida")
    print(projeto.gerar_relatorio())
