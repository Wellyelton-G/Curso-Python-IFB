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
class RecursoInativoError(Exception):
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

class ServicoEmprestimo(ABC):  # Herda de ABC
    @abstractmethod  # Indica que o método é abstrato
    def validar(self, usuario, recurso): pass
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
# Aqui temos duas implementações concretas do contrato Notificador.
# Elas mostram o uso de polimorfismo: ambas têm o método 'enviar', mas fazem coisas diferentes.

class NotificadorEmail(Notificador):
    def enviar(self, mensagem: str):
        print("[EMAIL]", mensagem)  # 'print' exibe algo na tela

class NotificadorConsole(Notificador):
    def enviar(self, mensagem: str):
        print("[CONSOLE]", mensagem)

# ===================== CLASSES DE APOIO =====================
# Classe Autor demonstra agregação: Livro tem um Autor, mas o Autor existe independente do Livro.

class Autor:
    def __init__(self, nome, nacionalidade):  # '__init__' é o construtor, chamado ao criar o objeto
        self.nome = nome  # 'self' representa o próprio objeto
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

    @property  # Permite acessar como atributo (ex: obj.id)
    def id(self): return self.__id
    @property
    def titulo(self): return self.__titulo
    @property
    def ativo(self): return self.__ativo

    def ativar(self): self.__ativo = True  # Ativa o recurso
    def desativar(self): self.__ativo = False  # Desativa o resurso
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
        if not self._historico_emprestimos:
            print("Nenhum empréstimo registrado para este recurso.")
        else:
            for emp in self._historico_emprestimos:
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
        super().__init__(id_, titulo)  # 'super()' chama o construtor da classe mãe
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
    #.Join é um étodo de string que junta todos os elementos da lista, separando-os por vírgula e espaço.

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
# Classe base Usuario e subclasses para diferentes perfis (Aluno, Servidor, Visitante).
# Demonstra herança, encapsulamento e métodos de classe.

class Usuario:
    _limite_padrao = 3  # Atributo de classe (protegido)
    def __init__(self, nome, matricula):
        self.nome = nome
        self.__matricula = matricula  # Privado
        self._historico_emprestimos = []  # Protegido
        self._historico_reservas = []  # Protegido

    @property
    def matricula(self): return self.__matricula
    @classmethod
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
class Aluno(Usuario): _limite_padrao = 3
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
        self.data_devolucao = datetime.now() #datetime é um módulo que fornece classes para manipulação de datas e horas atual do sistema.

    def em_atraso(self):
        # Calcula se o empréstimo está em atraso
        limite = self.data_emprestimo + timedelta(days=self.prazo)
        if self.devolvido:
            return self.data_devolucao > limite
        return datetime.now() > limite

    def resumo(self):
        # Retorna uma string com o resumo do empréstimo para histórico
        data_ini = self.data_emprestimo.strftime("%d/%m/%Y") #strftime é usado para formatar objetos de datas e hora.
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
# Implementação dos serviços de empréstimo e reserva.
# Mostram uso de polimorfismo, exceções e validações.

class EmprestimoService(ServicoEmprestimo):
    def __init__(self, notificador):
        self.notificador = notificador

    def validar(self, usuario, recurso):
        # Valida regras de negócio antes do empréstimo
        if not recurso.ativo: raise RecursoInativoError("Recurso inativo.")
        if not recurso.esta_disponivel(): raise Exception("Recurso já emprestado.")
        if not usuario.pode_emprestar(): raise LimiteEmprestimoExcedidoError("Limite de empréstimos.")
        if isinstance(recurso, Notebook) and not recurso.termo_assinado:
            raise PoliticaNaoAtendidaError("Notebook exige termo assinado.")

    def executar(self, usuario, recurso):
        # Realiza o empréstimo após validação
        self.validar(usuario, recurso)
        # Define o prazo conforme o tipo de usuário
        prazo = 7 if isinstance(usuario, Aluno) else 14 if isinstance(usuario, Servidor) else 3
        emprestimo = Emprestimo(usuario, recurso, datetime.now(), prazo)
        recurso._emprestado = True
        usuario.registrar_emprestimo(emprestimo)
        self.notificador.enviar(f"Empréstimo: {recurso.descricao()} para {usuario.nome}")
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
        self.notificador.enviar(f"Reserva: {recurso.descricao()} para {usuario.nome}")
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

def menu():
    # Exibe o menu principal de opções
    print("\nPlataforma de Empréstimos Acadêmicos (PEA)")
    print("Escolha uma opção:")
    print("1 - Listar recursos")
    print("2 - Cadastrar usuário")
    print("3 - Realizar empréstimo")
    print("4 - Devolver recurso")
    print("5 - Reservar recurso")
    print("6 - Consultar histórico de empréstimos de um recurso")
    print("7 - Consultar histórico de reservas de um recurso")
    print("8 - Consultar histórico de empréstimos de um usuário")
    print("9 - Consultar histórico de reservas de um usuário")
    print("10 - Sair")

def escolher_usuario(biblioteca):
    # Permite ao usuário escolher um usuário cadastrado
    print("Usuários cadastrados:")
    biblioteca.listar_usuarios()
    escolha = int(input("Escolha o usuário pelo número: ")) - 1
    return biblioteca._usuarios[escolha]

def escolher_recurso(biblioteca):
    # Permite ao usuário escolher um recurso cadastrado
    print("Recursos disponíveis:")
    for idx, r in enumerate(biblioteca._catalogo):
        print(f"{idx+1} - {r.descricao()}")
    escolha = int(input("Escolha o recurso pelo número: ")) - 1
    return biblioteca._catalogo[escolha]

# ===================== PROGRAMA PRINCIPAL =====================
# Aqui começa a execução do programa.
# Mostra uso de laço while, if/elif/else, try/except, input, print e manipulação de objetos.

if __name__ == "__main__":
    # Instancia o notificador e a biblioteca
    notificador = NotificadorConsole()
    biblioteca = Biblioteca(notificador)

    # Cadastro inicial de autores e recursos
    autor1 = Autor("Ana Silva", "Brasileira")
    livro = Livro(1, "POO em Python", autor1, 2022)
    kit = KitRobotica(2, "Kit Arduino", ["Arduino Uno", "Jumpers", "Protoboard"])
    notebook = Notebook(3, "Dell Inspiron", "i5", 8, 256)
    biblioteca.adicionar_recurso(livro)
    biblioteca.adicionar_recurso(kit)
    biblioteca.adicionar_recurso(notebook)

    # Cadastro inicial de usuários
    aluno = Aluno("Carlos", "A123")
    servidor = Servidor("Prof. João", "S456")
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
            tipo = input("Tipo (aluno/servidor/visitante): ").strip().lower()
            if tipo == "aluno":
                usuario = Aluno(nome, matricula)
            elif tipo == "servidor":
                usuario = Servidor(nome, matricula)
            else:
                usuario = Visitante(nome, matricula)
            biblioteca.cadastrar_usuario(usuario)
            print(f"Usuário {nome} cadastrado com sucesso!")
        elif opcao == "3":
            # Realiza um empréstimo de recurso
            try:
                usuario = escolher_usuario(biblioteca)
                recurso = escolher_recurso(biblioteca)
                # Para notebook, exige termo assinado
                if isinstance(recurso, Notebook) and not recurso.termo_assinado:
                    termo = input("Assinar termo de responsabilidade para notebook? (s/n): ")
                    if termo.lower() == "s":
                        recurso.assinar_termo()
                emprestimo = biblioteca.emprestimo_service.executar(usuario, recurso)
                # Registra o empréstimo no histórico do recurso também
                recurso.registrar_emprestimo(emprestimo)
                print("Empréstimo realizado com sucesso!")
            except Exception as e:
                print("Erro:", e)
        elif opcao == "4":
            # Permite devolver um recurso emprestado
            usuario = escolher_usuario(biblioteca)
            # Lista empréstimos ativos do usuário
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
                # Registra a reserva no histórico do recurso também
                recurso.registrar_reserva(reserva)
                print("Reserva realizada com sucesso!")
            except Exception as e:
                print("Erro:", e)
        elif opcao == "6":
            # Consulta histórico de empréstimos de um recurso
            recurso = escolher_recurso(biblioteca)
            recurso.mostrar_historico_emprestimos()
        elif opcao == "7":
            # Consulta histórico de reservas de um recurso
            recurso = escolher_recurso(biblioteca)
            recurso.mostrar_historico_reservas()
        elif opcao == "8":
            # Consulta histórico de empréstimos de um usuário
            usuario = escolher_usuario(biblioteca)
            usuario.mostrar_historico_emprestimos()
        elif opcao == "9":
            # Consulta histórico de reservas de um usuário
            usuario = escolher_usuario(biblioteca)
            usuario.mostrar_historico_reservas()
        elif opcao == "10":
            # Sai do sistema
            print("Saindo do sistema. Até logo!")
            break
        else:
            # Opção inválida
            print("Opção inválida. Tente novamente.")

# Fim do código. Todos os blocos estão comentados para explicar o que está acontecendo e como as palavras reservadas do Python
