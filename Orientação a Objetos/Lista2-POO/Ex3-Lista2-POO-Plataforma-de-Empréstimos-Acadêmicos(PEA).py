"""
Plataforma de Empréstimos Acadêmicos (PEA)
Este programa é um exemplo didático de como usar Programação Orientada a Objetos (POO) em Python
para modelar um sistema de empréstimos e reservas de recursos em uma instituição.
Aqui você verá conceitos como: abstração, herança, polimorfismo, encapsulamento, exceções personalizadas,
composição, agregação e uso de interfaces (ABC).

Cada parte do código está comentada para explicar o que está acontecendo e como as palavras reservadas
do Python são usadas.
"""

# Importando recursos da linguagem Python:
from abc import ABC, abstractmethod  # 'from' e 'import' trazem funcionalidades de outros módulos
from datetime import datetime, timedelta  # Para trabalhar com datas e horários

# ===================== EXCEÇÕES PERSONALIZADAS =====================
# Aqui criei novas exceções (erros) específicas para o sistema.
# 'class' define uma nova classe. Todas herdam de Exception (classe base de erros em Python).
class RecursoInativoError(Exception):  # class: define uma classe nova
    pass  # 'pass' indica que não há código extra aqui, só herdamos de Exception

class LimiteEmprestimoExcedidoError(Exception):
    pass

class ConflitoDeReservaError(Exception):
    pass

class PrazoAtrasadoError(Exception):
    pass

class PoliticaNaoAtendidaError(Exception):
    pass

# ===================== CONTRATOS/INTERFACES (ABC) =================
# Usamos classes abstratas (ABC) para definir contratos que outras classes devem seguir.
# 'ABC' significa Abstract Base Class. '@abstractmethod' obriga as subclasses a implementarem o método.

class ServicoEmprestimo(ABC):  # class: define uma classe abstrata, herda de ABC
    @abstractmethod  # @abstractmethod: obriga a implementação nas subclasses
    def validar(self, usuario, recurso): pass  # def: define um método
    @abstractmethod
    def executar(self, usuario, recurso): pass
    @abstractmethod
    def cancelar(self, usuario, recurso): pass

class ServicoReserva(ABC):
    @abstractmethod
    def validar(self, usuario, recurso, inicio, fim): pass
    @abstractmethod
    def reservar(self, usuario, recurso, inicio, fim): pass
    @abstractmethod
    def liberar(self, reserva): pass

class Notificador(ABC):
    @abstractmethod
    def enviar(self, mensagem: str): pass

# ===================== NOTIFICADORES =====================
# Agora, vamos permitir que o sistema armazene a última mensagem enviada por e-mail,
# para que o usuário possa consultar depois pelo menu.
# Aqui temos implementações concretas do contrato notificador, com armazenamento da última mensagem.
# Elas mostram o uso de polimorfismo: ambas têm o método 'enviar' com a mesma assinatura, mas implementações diferentes.

class NotificadorEmail(Notificador):  # class: define uma classe que herda de Notificador
    def __init__(self):  # def: define o construtor, self: referência ao objeto
        self.ultima_mensagem = ""  # self: atributo do objeto

    def enviar(self, mensagem: str):  # def: define um método
        # Salva a mensagem enviada para consulta posterior
        self.ultima_mensagem = mensagem
        print("\n========== NOTIFICAÇÃO POR E-MAIL ==========")  # print: exibe mensagem no console
        print(mensagem)
        print("=============================================\n")

class NotificadorConsole(Notificador):
    def enviar(self, mensagem: str):
        print("\n========== NOTIFICAÇÃO NO CONSOLE ==========")
        print(mensagem)
        print("=============================================\n")

class NotificadorDuplo(Notificador):
    def __init__(self):
        # Instancia os dois notificadores
        self.notificador_email = NotificadorEmail()
        self.notificador_console = NotificadorConsole()

    def enviar(self, mensagem: str):
        # Envia a mensagem para ambos
        self.notificador_email.enviar(mensagem)
        self.notificador_console.enviar(mensagem)

    def consultar_ultima_mensagem_email(self):
        # Retorna a última mensagem enviada por e-mail
        return self.notificador_email.ultima_mensagem

# ===================== CLASSES DE APOIO =====================
# Classe Autor demonstra agregação: Livro tem um Autor, mas o Autor existe independente do Livro.

class Autor:
    def __init__(self, nome, nacionalidade):  # __init__: método construtor
        self.nome = nome  # self: atributo do objeto
        self.nacionalidade = nacionalidade

# ===================== RECURSOS =====================
# Classe abstrata Recurso e suas especializações (Livro, KitRobotica, Notebook).
# Mostra herança, encapsulamento (atributos privados/protegidos) e polimorfismo.

class Recurso(ABC):
    def __init__(self, id_, titulo):
        self.__id = id_  # '__' torna o atributo privado (name mangling)
        self.__titulo = titulo
        self.__ativo = True
        self._emprestado = False  # '_' indica protegido (acessível só na classe e subclasses)
        self._historico_emprestimos = []  # Lista para guardar histórico de empréstimos
        self._historico_reservas = []     # Lista para guardar histórico de reservas

    @property  # @property: permite acessar método como atributo
    def id(self): return self.__id
    @property
    def titulo(self): return self.__titulo
    @property
    def ativo(self): return self.__ativo

    def ativar(self): self.__ativo = True  # Ativa o recurso
    def desativar(self): self.__ativo = False  # Desativa o recurso
    def esta_disponivel(self): return self.__ativo and not self._emprestado  # Disponível se ativo e não emprestado

    @abstractmethod
    def descricao(self): pass  # Método abstrato, cada recurso terá sua própria descrição

    # Métodos para adicionar ao histórico
    def registrar_emprestimo(self, emprestimo):
        self._historico_emprestimos.append(emprestimo)

    def registrar_reserva(self, reserva):
        self._historico_reservas.append(reserva)

    # Método para exibir histórico de empréstimos do recurso
    def mostrar_historico_emprestimos(self):
        print(f"\nHistórico de empréstimos do recurso: {self.descricao()}")
        if not self._historico_emprestimos:  # if: estrutura de decisão
            print("Nenhum empréstimo registrado para este recurso.")
        else:  # else: caso contrário
            for emp in self._historico_emprestimos:  # for: laço de repetição
                print(emp.resumo())

    # Método para exibir histórico de reservas do recurso
    def mostrar_historico_reservas(self):
        print(f"\nHistórico de reservas do recurso: {self.descricao()}")
        if not self._historico_reservas:
            print("Nenhuma reserva registrada para este recurso.")
        else:
            for res in self._historico_reservas:
                print(res.resumo())

# Livro herda de Recurso e adiciona autor (agregação) e ano.
class Livro(Recurso):
    def __init__(self, id_, titulo, autor, ano):
        super().__init__(id_, titulo)  # super(): chama o construtor da classe mãe
        self.autor = autor  # Agregação: autor é um objeto externo
        self.ano = ano

    def descricao(self):
        return f"Livro: {self.titulo} ({self.ano}) - Autor: {self.autor.nome}"

# KitRobotica herda de Recurso e adiciona lista de componentes.
class KitRobotica(Recurso):
    def __init__(self, id_, titulo, componentes):
        super().__init__(id_, titulo)
        self.componentes = componentes  # Lista de strings

    def descricao(self):
        return f"Kit Robótica: {self.titulo} - Componentes: {', '.join(self.componentes)}" 
    # .join: método de string que junta todos os elementos da lista, separando-os por vírgula e espaço.

# Notebook herda de Recurso e adiciona atributos específicos.
class Notebook(Recurso):
    def __init__(self, id_, titulo, cpu, ram, ssd):
        super().__init__(id_, titulo)
        self.cpu = cpu
        self.ram = ram
        self.ssd = ssd
        self.termo_assinado = False  # Política especial: só pode emprestar se termo for assinado

    def descricao(self):
        return f"Notebook: {self.titulo} ({self.cpu}, {self.ram}GB RAM, {self.ssd}GB SSD)"
    def assinar_termo(self):
        self.termo_assinado = True

# ===================== USUÁRIOS =====================
# Agora vamos adicionar o campo de e-mail ao usuário.
# O e-mail será solicitado no cadastro e exibido na consulta de usuários.

class Usuario:
    _limite_padrao = 3  # Atributo de classe (protegido)
    def __init__(self, nome, matricula, email):  # def: define o construtor
        self.nome = nome
        self.__matricula = matricula  # Privado
        self.email = email            # Novo atributo para armazenar o e-mail do usuário
        self._historico_emprestimos = []  # Protegido
        self._historico_reservas = []     # Protegido

    @property
    def matricula(self): return self.__matricula
    @classmethod  # @classmethod: método de classe, recebe cls como primeiro parâmetro
    def atualizar_limite_padrao(cls, novo_limite): cls._limite_padrao = novo_limite
    def pode_emprestar(self):
        # Conta quantos empréstimos não devolvidos o usuário possui
        return len([e for e in self._historico_emprestimos if not e.devolvido]) < self._limite_padrao
    def registrar_emprestimo(self, emprestimo): self._historico_emprestimos.append(emprestimo)
    def registrar_reserva(self, reserva): self._historico_reservas.append(reserva)

    # Método para exibir histórico de empréstimos do usuário
    def mostrar_historico_emprestimos(self):
        print(f"\nHistórico de empréstimos do usuário: {self.nome}")
        if not self._historico_emprestimos:
            print("Nenhum empréstimo registrado para este usuário.")
        else:
            for emp in self._historico_emprestimos:
                print(emp.resumo_usuario())

    # Método para exibir histórico de reservas do usuário
    def mostrar_historico_reservas(self):
        print(f"\nHistórico de reservas do usuário: {self.nome}")
        if not self._historico_reservas:
            print("Nenhuma reserva registrada para este usuário.")
        else:
            for res in self._historico_reservas:
                print(res.resumo_usuario())

# Subclasses de Usuario para diferentes perfis e limites.
class Aluno(Usuario): _limite_padrao = 3  # class: define uma subclasse, _limite_padrao: atributo de classe
class Servidor(Usuario): _limite_padrao = 5
class Visitante(Usuario): _limite_padrao = 1

# ===================== EMPRÉSTIMOS E RESERVAS =====================
# Classes para registrar empréstimos e reservas.
# Mostram associação entre objetos (um empréstimo associa usuário e recurso).
# Agora, cada recurso e cada usuário terá um histórico detalhado.

class Emprestimo:
    def __init__(self, usuario, recurso, data_emprestimo, prazo_dias):
        self.usuario = usuario
        self.recurso = recurso
        self.data_emprestimo = data_emprestimo
        self.prazo = prazo_dias
        self.devolvido = False
        self.data_devolucao = None

    def devolver(self):
        self.devolvido = True
        self.data_devolucao = datetime.now() # datetime.now(): retorna data/hora atual

    def em_atraso(self):
        # Calcula se o empréstimo está em atraso
        limite = self.data_emprestimo + timedelta(days=self.prazo)
        if self.devolvido:
            return self.data_devolucao > limite
        return datetime.now() > limite

    def resumo(self):
        # Retorna uma string com o resumo do empréstimo para histórico
        data_ini = self.data_emprestimo.strftime("%d/%m/%Y") # strftime: formata data
        if self.devolvido:
            data_fim = self.data_devolucao.strftime("%d/%m/%Y")
            status = f"Devolvido em {data_fim}"
        else:
            status = "Em aberto"
        return f"Usuário: {self.usuario.nome} | Início: {data_ini} | Prazo: {self.prazo} dias | {status}"

    def resumo_usuario(self):
        # Resumo para histórico do usuário
        data_ini = self.data_emprestimo.strftime("%d/%m/%Y")
        if self.devolvido:
            data_fim = self.data_devolucao.strftime("%d/%m/%Y")
            status = f"Devolvido em {data_fim}"
        else:
            status = "Em aberto"
        return f"Recurso: {self.recurso.descricao()} | Início: {data_ini} | Prazo: {self.prazo} dias | {status}"

class Reserva:
    def __init__(self, usuario, recurso, inicio, fim):
        self.usuario = usuario
        self.recurso = recurso
        self.inicio = inicio
        self.fim = fim
        self.liberada = False

    def liberar(self):
        self.liberada = True

    def resumo(self):
        # Retorna uma string com o resumo da reserva para histórico
        data_ini = self.inicio.strftime("%d/%m/%Y %H:%M")
        data_fim = self.fim.strftime("%d/%m/%Y %H:%M")
        status = "Liberada" if self.liberada else "Ativa"
        return f"Usuário: {self.usuario.nome} | Início: {data_ini} | Fim: {data_fim} | {status}"

    def resumo_usuario(self):
        # Resumo para histórico do usuário
        data_ini = self.inicio.strftime("%d/%m/%Y %H:%M")
        data_fim = self.fim.strftime("%d/%m/%Y %H:%M")
        status = "Liberada" if self.liberada else "Ativa"
        return f"Recurso: {self.recurso.descricao()} | Início: {data_ini} | Fim: {data_fim} | {status}"

# ===================== SERVIÇOS =====================
# Aqui vamos melhorar as mensagens de notificação para incluir a duração do empréstimo e da reserva.

class EmprestimoService(ServicoEmprestimo):
    def __init__(self, notificador):
        self.notificador = notificador

    def validar(self, usuario, recurso):
        # Valida regras de negócio antes do empréstimo
        if not recurso.ativo: raise RecursoInativoError("Recurso inativo.")  # if: estrutura de decisão, raise: lança exceção
        if not recurso.esta_disponivel(): raise Exception("Recurso já emprestado.")
        if not usuario.pode_emprestar(): raise LimiteEmprestimoExcedidoError("Limite de empréstimos.")
        if isinstance(recurso, Notebook) and not recurso.termo_assinado:  # isinstance: verifica tipo do objeto
            raise PoliticaNaoAtendidaError("Notebook exige termo assinado.")

    def executar(self, usuario, recurso):
        # Realiza o empréstimo após validação
        self.validar(usuario, recurso)
        # Define o prazo conforme o tipo de usuário
        prazo = 7 if isinstance(usuario, Aluno) else 14 if isinstance(usuario, Servidor) else 3  # if/else: decisão
        emprestimo = Emprestimo(usuario, recurso, datetime.now(), prazo)
        recurso._emprestado = True
        usuario.registrar_emprestimo(emprestimo)
        # Monta uma mensagem detalhada com a duração do empréstimo
        mensagem = (
            f"Empréstimo realizado!\n"
            f"Recurso: {recurso.descricao()}\n"
            f"Usuário: {usuario.nome}\n"
            f"Duração do empréstimo: {prazo} dia(s), de {emprestimo.data_emprestimo.strftime('%d/%m/%Y')} até "
            f"{(emprestimo.data_emprestimo + timedelta(days=prazo)).strftime('%d/%m/%Y')}."
        )
        # Envia a mensagem para ambos os tipos de notificação
        self.notificador.enviar(mensagem)
        return emprestimo

    def cancelar(self, usuario, recurso):
        # Cancela um empréstimo ativo
        for e in usuario._historico_emprestimos:
            if e.recurso == recurso and not e.devolvido:
                e.devolver()
                recurso._emprestado = False
                self.notificador.enviar(f"Cancelado: {recurso.descricao()} para {usuario.nome}")
                return
        raise Exception("Empréstimo não encontrado.")

class ReservaService(ServicoReserva):
    def __init__(self, notificador):
        self.notificador = notificador
        self._agenda = []

    def validar(self, usuario, recurso, inicio, fim):
        # Valida conflitos de reserva
        if not recurso.ativo:
            raise RecursoInativoError("Recurso inativo.")
        for r in self._agenda:
            if r.recurso == recurso and not r.liberada:
                if not (fim <= r.inicio or inicio >= r.fim):
                    raise ConflitoDeReservaError("Conflito de reserva.")

    def reservar(self, usuario, recurso, inicio, fim):
        # Realiza a reserva após validação
        self.validar(usuario, recurso, inicio, fim)
        reserva = Reserva(usuario, recurso, inicio, fim)
        self._agenda.append(reserva)
        usuario.registrar_reserva(reserva)
        # Calcula a duração da reserva em horas
        duracao_horas = int((fim - inicio).total_seconds() // 3600)
        # Monta uma mensagem detalhada para o usuário, informando o recurso, o usuário, a duração e o período da reserva
        mensagem = (
            f"Reserva realizada!\n"
            f"Recurso: {recurso.descricao()}\n"
            f"Usuário: {usuario.nome}\n"
            f"Duração da reserva: {duracao_horas} hora(s), de {inicio.strftime('%d/%m/%Y %H:%M')} até {fim.strftime('%d/%m/%Y %H:%M')}."
        )
        # Envia a mensagem detalhada para ambos os tipos de notificação
        self.notificador.enviar(mensagem)
        return reserva

    def liberar(self, reserva):
        reserva.liberar()
        self.notificador.enviar(f"Reserva liberada: {reserva.recurso.descricao()}")

# ===================== BIBLIOTECA =====================
# Biblioteca faz composição dos recursos e usuários.
# Demonstra composição: Biblioteca "possui" recursos e usuários.

class Biblioteca:
    def __init__(self, notificador):
        self._catalogo = []  # Lista de recursos (composição)
        self._usuarios = []  # Lista de usuários (composição)
        self.emprestimo_service = EmprestimoService(notificador)
        self.reserva_service = ReservaService(notificador)

    def adicionar_recurso(self, recurso): self._catalogo.append(recurso)
    def cadastrar_usuario(self, usuario): self._usuarios.append(usuario)
    def listar_recursos(self):
        for r in self._catalogo:
            print(r.descricao())

    def buscar_recurso(self, id_):
        for r in self._catalogo:
            if r.id == id_:
                return r
        return None

    def buscar_usuario(self, matricula):
        for u in self._usuarios:
            if u.matricula == matricula:
                return u
        return None

    def listar_usuarios(self):
        for idx, u in enumerate(self._usuarios):
            print(f"{idx+1} - {u.nome} (Matrícula: {u.matricula})")

# ===================== INTERFACE DE USUÁRIO (CLI) =====================
# Funções para interação com o usuário via terminal.
# Mostram uso de laços, input, print e manipulação de listas.

def escolher_recurso(biblioteca):
    print("\nRecursos disponíveis:")
    for idx, recurso in enumerate(biblioteca._catalogo):  # enumerate: retorna índice e valor
        print(f"{idx+1} - {recurso.descricao()}")
    escolha = int(input("Escolha o recurso pelo número: ")) - 1  # input: recebe valor do usuário
    return biblioteca._catalogo[escolha]

def escolher_usuario(biblioteca):
    print("\nUsuários cadastrados:")
    for idx, usuario in enumerate(biblioteca._usuarios):
        print(f"{idx+1} - {usuario.nome} (Matrícula: {usuario.matricula})")
    escolha = int(input("Escolha o usuário pelo número: ")) - 1
    return biblioteca._usuarios[escolha]

def consultar_usuarios(biblioteca):
    print("\nUsuários cadastrados:")
    for idx, usuario in enumerate(biblioteca._usuarios):
        print(f"{idx+1} - {usuario.nome} (Matrícula: {usuario.matricula}, E-mail: {usuario.email})")

def alterar_informacoes_usuario(biblioteca):
    print("\nUsuários cadastrados:")
    for idx, usuario in enumerate(biblioteca._usuarios):
        print(f"{idx+1} - {usuario.nome} (Matrícula: {usuario.matricula}, E-mail: {usuario.email})")
    escolha = int(input("Escolha o usuário para alterar pelo número: ")) - 1
    usuario = biblioteca._usuarios[escolha]
    print(f"Alterando informações de {usuario.nome}:")
    novo_nome = input("Novo nome (deixe em branco para manter): ")
    novo_email = input("Novo e-mail (deixe em branco para manter): ")
    if novo_nome:  # if: estrutura de decisão
        usuario.nome = novo_nome
    if novo_email:
        usuario.email = novo_email
    print("Informações atualizadas com sucesso!")

def renovar_emprestimo(biblioteca):
    """
    Permite ao usuário renovar um empréstimo ativo, aumentando o prazo.
    Demonstra uso de listas, laços, input, manipulação de objetos e atributos.
    """
    usuario = escolher_usuario(biblioteca)  # Seleciona o usuário
    emprestimos_ativos = [e for e in usuario._historico_emprestimos if not e.devolvido]  # Lista empréstimos não devolvidos
    if not emprestimos_ativos:
        print("Nenhum empréstimo ativo para este usuário.")
        return
    for idx, e in enumerate(emprestimos_ativos):
        print(f"{idx+1} - {e.recurso.descricao()} (Início: {e.data_emprestimo.strftime('%d/%m/%Y')}, Prazo: {e.prazo} dias)")
    escolha = int(input("Escolha o empréstimo para renovar: ")) - 1
    emprestimo = emprestimos_ativos[escolha]
    # Exemplo: renova por mais 7 dias (ajuste conforme política)
    emprestimo.prazo += 7
    print("Empréstimo renovado com sucesso! Novo prazo:", emprestimo.prazo, "dias.")

def menu():
    # Exibe o menu principal de opções
    print("\nPlataforma de Empréstimos Acadêmicos (PEA)")
    print("Escolha uma opção:")
    print("1 - Listar recursos")
    print("2 - Cadastrar usuário")
    print("3 - Realizar empréstimo")
    print("4 - Devolver recurso")
    print("5 - Reservar recurso")
    print("6 - Consultas")  # Nova opção para submenu de consultas
    print("7 - Alterar informações dos usuários")
    print("8 - Renovar empréstimo")  # NOVA OPÇÃO
    print("9 - Sair")

def submenu_consultas(biblioteca, notificador):
    # Submenu para centralizar todas as opções de consulta do sistema
    while True:  # while: laço de repetição
        print("\n=== CONSULTAS ===")
        print("1 - Histórico de empréstimos de um recurso")
        print("2 - Histórico de reservas de um recurso")
        print("3 - Histórico de empréstimos de um usuário")
        print("4 - Histórico de reservas de um usuário")
        print("5 - Consultar última mensagem enviada por e-mail ao realizar empréstimo")
        print("6 - Consultar usuários cadastrados")
        print("7 - Voltar ao menu principal")
        opcao = input("Escolha uma opção de consulta: ")

        if opcao == "1":
            recurso = escolher_recurso(biblioteca)
            recurso.mostrar_historico_emprestimos()
        elif opcao == "2":
            recurso = escolher_recurso(biblioteca)
            recurso.mostrar_historico_reservas()
        elif opcao == "3":
            usuario = escolher_usuario(biblioteca)
            usuario.mostrar_historico_emprestimos()
        elif opcao == "4":
            usuario = escolher_usuario(biblioteca)
            usuario.mostrar_historico_reservas()
        elif opcao == "5":
            # Consulta a última mensagem enviada por e-mail ao realizar empréstimo
            ultima_mensagem = notificador.consultar_ultima_mensagem_email()
            if ultima_mensagem:
                print("\n=== Última mensagem enviada por e-mail ao realizar empréstimo ===")
                print(ultima_mensagem)
                print("=================================================================\n")
            else:
                print("Nenhuma mensagem de empréstimo enviada por e-mail ainda.")
        elif opcao == "6":
            consultar_usuarios(biblioteca)
        elif opcao == "7":
            break  # break: sai do laço while
        else:
            print("Opção inválida. Tente novamente.")

# ...restante do código permanece igual...

if __name__ == "__main__":  # if: estrutura de decisão, __name__: variável especial, __main__: executa se for principal
    # Instancia o notificador duplo e a biblioteca
    notificador = NotificadorDuplo()
    biblioteca = Biblioteca(notificador)

    # Cadastro inicial de autores e recursos
    autor1 = Autor("Ana Silva", "Brasileira")
    livro = Livro(1, "POO em Python", autor1, 2022)
    kit = KitRobotica(2, "Kit Arduino", ["Arduino Uno", "Jumpers", "Protoboard"])
    notebook = Notebook(3, "Dell Inspiron", "i5", 8, 256)
    biblioteca.adicionar_recurso(livro)
    biblioteca.adicionar_recurso(kit)
    biblioteca.adicionar_recurso(notebook)

    # Cadastro inicial de usuários (agora com e-mail)
    aluno = Aluno("Carlos", "A123", "carlos@email.com")
    servidor = Servidor("Prof. João", "S456", "joao@email.com")
    biblioteca.cadastrar_usuario(aluno)
    biblioteca.cadastrar_usuario(servidor)

    # Loop principal do menu
    while True:
        menu()  # Mostra o menu de opções
        opcao = input("Digite sua opção: ")  # Recebe a escolha do usuário
        if opcao == "1":
            # Lista todos os recursos cadastrados
            print("\nRecursos cadastrados:")
            biblioteca.listar_recursos()
        elif opcao == "2":
            # Permite cadastrar um novo usuário
            nome = input("Nome do usuário: ")
            matricula = input("Matrícula: ")
            email = input("E-mail: ")  # Solicita o e-mail do usuário
            tipo = input("Tipo (aluno/servidor/visitante): ").strip().lower()
            if tipo == "aluno":
                usuario = Aluno(nome, matricula, email)
            elif tipo == "servidor":
                usuario = Servidor(nome, matricula, email)
            else:
                usuario = Visitante(nome, matricula, email)
            biblioteca.cadastrar_usuario(usuario)
            print(f"Usuário {nome} cadastrado com sucesso!")
        elif opcao == "3":
            # Realiza um empréstimo de recurso
            try:  # try: tenta executar o bloco, except: captura erro
                usuario = escolher_usuario(biblioteca)
                recurso = escolher_recurso(biblioteca)
                # Para notebook, exige termo assinado
                if isinstance(recurso, Notebook) and not recurso.termo_assinado:
                    termo = input("Assinar termo de responsabilidade para notebook? (s/n): ")
                    if termo.lower() == "s":
                        recurso.assinar_termo()
                emprestimo = biblioteca.emprestimo_service.executar(usuario, recurso)
                recurso.registrar_emprestimo(emprestimo)
                print("Empréstimo realizado com sucesso!")
            except Exception as e:
                print("Erro:", e)
        elif opcao == "4":
            # Permite devolver um recurso emprestado
            usuario = escolher_usuario(biblioteca)
            emprestimos_ativos = [e for e in usuario._historico_emprestimos if not e.devolvido]
            if not emprestimos_ativos:
                print("Nenhum empréstimo ativo para este usuário.")
            else:
                for idx, e in enumerate(emprestimos_ativos):
                    print(f"{idx+1} - {e.recurso.descricao()}")
                escolha = int(input("Escolha o empréstimo para devolver: ")) - 1
                emprestimo = emprestimos_ativos[escolha]
                emprestimo.devolver()
                emprestimo.recurso._emprestado = False
                print("Recurso devolvido com sucesso!")
        elif opcao == "5":
            # Permite reservar um recurso
            try:
                usuario = escolher_usuario(biblioteca)
                recurso = escolher_recurso(biblioteca)
                inicio = datetime.now()
                duracao = int(input("Duração da reserva em horas: "))
                fim = inicio + timedelta(hours=duracao)
                reserva = biblioteca.reserva_service.reservar(usuario, recurso, inicio, fim)
                recurso.registrar_reserva(reserva)
                print("Reserva realizada com sucesso!")
            except Exception as e:
                print("Erro:", e)
        elif opcao == "6":
            # Chama o submenu de consultas
            submenu_consultas(biblioteca, notificador)
        elif opcao == "7":
            # Nova opção: alterar informações dos usuários
            alterar_informacoes_usuario(biblioteca)
        elif opcao == "8":
            # Nova opção: renovar empréstimo
            renovar_emprestimo(biblioteca)
        elif opcao == "9":
            print("Saindo do sistema. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Comentários didáticos:
# - O menu principal agora tem uma opção "Consultas" que leva a um submenu com todas as opções de consulta do sistema.
# - O submenu de consultas centraliza o acesso ao histórico de empréstimos e reservas, consulta de usuários e consulta da última mensagem de e-mail.
# - Isso deixa o menu principal mais limpo e organizado, facilitando a navegação para o usuário.
# - A opção de alterar informações dos usuários foi movida para o menu principal, facilitando o acesso.
# - A nova opção "Renovar empréstimo" foi adicionada ao menu principal, permitindo renovar prazos de empréstimos ativos.
# - O código foi reorganizado para refletir essas mudanças, mas a lógica permanece a mesma.
# - Todas as palavras-chave importantes do Python estão comentadas no código, explicando sua função e uso.
