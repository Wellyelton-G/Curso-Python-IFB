# SISTEMA BANCÁRIO ORIENTADO A OBJETOS EM PYTHON
# Este sistema simula operações bancárias como criação de contas, depósitos, saques,
# transferências, histórico de titularidade e gerenciamento de chave Pix, usando os conceitos de Programação Orientada a Objetos.

from datetime import datetime  # Importa a classe datetime do módulo datetime para trabalhar com datas e horas
import re  # Importa o módulo de expressões regulares para validação da chave Pix

# ===================== CLASSE CLIENTE ===================== #
# class: Define uma classe (molde para criar objetos).
class Cliente:
    def __init__(self, nome, cpf):
        # def: Define uma função ou método.
        # __init__: Método construtor, chamado ao criar um novo objeto.
        # self: Referência ao próprio objeto (usado dentro de métodos de classe).
        self.nome = nome  # Nome do cliente (string)
        self.cpf = cpf    # CPF ou CNPJ do cliente (string)
        self.historico_titularidade = []  # Lista que guarda tuplas com alterações de titularidade (data, antigo, novo)

    def alterar_nome(self, novo_nome):
        # if: Estrutura de decisão (condicional).
        if novo_nome != self.nome:
            agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # Pega data e hora atual formatada
            # append(): Adiciona um item ao final de uma lista.
            self.historico_titularidade.append((agora, self.nome, novo_nome))  # Adiciona alteração ao histórico
            self.nome = novo_nome  # Atualiza o nome

    def ver_historico_titularidade(self):
        # if, else: Estruturas de decisão (condicionais).
        if not self.historico_titularidade:  # Verifica se a lista está vazia
            print("Titularidade nunca foi alterada.")  # print: Exibe informações na tela.
        else:
            print("Histórico de titularidade:")
            # for: Estrutura de repetição (laço).
            for data, antigo, novo in self.historico_titularidade:
                # format/string f"{}": Formata strings de maneira prática.
                print(f"- Em {data}, alterado de '{antigo}' para '{novo}'")

    def __str__(self):
        # __str__: Método especial que define como o objeto será exibido ao usar print(cliente)
        return f"{self.nome} (CPF: {self.cpf})"

# ===================== CLASSE CONTA (BASE) ===================== #
# class: Define uma classe base para diferentes tipos de conta bancária
class Conta:
    # Atributos de classe: são compartilhados por todas as instâncias da classe
    TAXA_JUROS_VIGENTE = 0.0  # Taxa de juros padrão ao mês (%)
    TAXA_JUROS_ANUAL = 0.0    # Taxa de juros padrão ao ano (%)
    IOF_BASICO = 0.0          # IOF alíquota básica (%)
    IOF_ADICIONAL = 0.0       # IOF alíquota adicional (%)
    CET_MENSAL = 0.0          # Custo Efetivo Total ao mês (%)
    CET_ANUAL = 0.0           # Custo Efetivo Total ao ano (%)

    def __init__(self, numero, cliente):
        # def: Define uma função ou método.
        # __init__: Método construtor, chamado ao criar um novo objeto.
        # self: Referência ao próprio objeto (usado dentro de métodos de classe).
        self.numero = numero          # Número da conta (string)
        self.cliente = cliente        # Objeto do tipo Cliente (composição)
        self._saldo = 0.0             # Saldo protegido (inicia com 0). O _ indica que é um atributo "protegido"
        self._transacoes = []         # Lista de objetos Transacao
        self.pix = None               # Atributo para armazenar a chave Pix da conta

    @property
    # @property: Permite acessar um método como se fosse um atributo (ex: conta.saldo)
    def saldo(self):
        # return: Retorna um valor de uma função/método.
        return self._saldo

    def registrar_transacao(self, transacao):
        # append(): Adiciona um item ao final de uma lista.
        self._transacoes.append(transacao)

    def depositar(self, valor):
        # if, raise: Estruturas de decisão e lançamento de exceção (erro).
        if valor <= 0:
            # raise: Lança uma exceção (erro).
            raise ValueError("O valor do depósito deve ser positivo.")
        self._saldo += valor
        self.registrar_transacao(Transacao('depósito', valor, self))

    def sacar(self, valor):
        # Realiza um saque na conta
        if valor <= 0:
            raise ValueError("O valor do saque deve ser positivo.")
        if self._saldo < valor:
            raise ValueError("Saldo insuficiente.")
        self._saldo -= valor
        self.registrar_transacao(Transacao('saque', valor, self))

    def transferir(self, valor, conta_destino):
        # Realiza uma transferência para outra conta
        if valor <= 0:
            raise ValueError("O valor da transferência deve ser positivo.")
        if self._saldo < valor:
            raise ValueError("Saldo insuficiente para transferência.")
        self._saldo -= valor
        conta_destino._saldo += valor
        transacao = Transacao('transferência', valor, self, conta_destino)
        self.registrar_transacao(transacao)
        conta_destino.registrar_transacao(transacao)

    def validar_chave_pix(self, chave):
        """
        Valida a chave Pix conforme as regras do Banco Central.
        # Trechos de regex para UUID/Pix baseados em:
        # https://github.com/project-fifo/pyfi/tree/1e19c31af9d838809a8568e6e16ec7dab4f63573/fifo/helper.py
        # https://github.com/Chrisser884/socioboard/tree/ad5b7c5148d93b081c7a1a5b127eab5596c03531/Socioboard%20V2.0/SocioboardDataServices/Web%20References/Api.Linkedin/Linkedin.wsdl
        # https://github.com/marvin-heiden/sendungsverfolgung/tree/5f737b5bb4684cf332e6db6fc755d5c9e7fd3050/MessageFilterService/helm/messageFilterService/templates/json-schema.yaml
        # https://github.com/basgroot/api-explorer/tree/bd4463f2751711dade7ff083e00193c70125f762/oas/cm.yaml
        # Licença: desconhecida
        """
        # strip(): Remove espaços em branco do início e fim de uma string.
        chave = chave.strip()
        cpf_pattern = r'^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$'
        cnpj_pattern = r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$|^\d{14}$'
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        telefone_pattern = r'^(\+55)?\d{10,11}$'
        # Referência das regex abaixo conforme citado acima
        uuid_pattern = r'^[0-9a-fA-F]{32}$|^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
        # re.match(): Verifica se uma string corresponde a um padrão (expressão regular).
        if (re.match(cpf_pattern, chave) or
            re.match(cnpj_pattern, chave) or
            re.match(email_pattern, chave) or
            re.match(telefone_pattern, chave) or
            re.match(uuid_pattern, chave)):
            return True
        else:
            return False

    def cadastrar_pix(self, chave):
        if self.pix:
            print(f"Já existe uma chave Pix cadastrada: {self.pix}")
        else:
            if self.validar_chave_pix(chave):
                self.pix = chave
                print(f"Chave Pix '{self.pix}' cadastrada com sucesso para a conta {self.numero}.")
            else:
                print("Chave Pix inválida! Siga o padrão do Banco Central (CPF, CNPJ, e-mail, telefone ou chave aleatória UUID).")

    def alterar_pix(self, nova_chave):
        if not self.pix:
            print("Nenhuma chave Pix cadastrada ainda. Use a opção de cadastro.")
        else:
            if self.validar_chave_pix(nova_chave):
                print(f"Chave Pix alterada de '{self.pix}' para '{nova_chave}'.")
                self.pix = nova_chave
            else:
                print("Nova chave Pix inválida! Siga o padrão do Banco Central (CPF, CNPJ, e-mail, telefone ou chave aleatória UUID).")

    def exibir_pix(self):
        if self.pix:
            return f"Chave Pix: {self.pix}"
        else:
            return "Chave Pix: Não cadastrada"

    def extrato(self):
        print(f"\nExtrato da conta {self.numero} - Titular: {self.cliente}")
        print(self.exibir_pix())
        for t in self._transacoes:
            print(t)
        print(f"Saldo atual: R${self._saldo:.2f}\n")
        print("=== Informações de taxas e custos bancários ===")
        print(f"Taxa de juros vigente (ao mês): {self.TAXA_JUROS_VIGENTE:.2f}%")
        print(f"Taxa de juros cobrada ao ano: {self.TAXA_JUROS_ANUAL:.2f}%")
        print(f"IOF alíquota básica: {self.IOF_BASICO:.2f}%")
        print(f"IOF alíquota adicional: {self.IOF_ADICIONAL:.4f}%")
        print(f"Custo Efetivo Total (CET) ao mês: {self.CET_MENSAL:.2f}%")
        print(f"Custo Efetivo Total (CET) ao ano: {self.CET_ANUAL:.2f}%")
        print("=============================================\n")

    def alterar_titular(self, novo_nome):
        self.cliente.alterar_nome(novo_nome)
        print(f"Titular da conta {self.numero} alterado para {novo_nome}.")

    def tem_limite(self):
        return False

    def mostrar_limite(self):
        return "Não possui limite para operação."

# ===================== CLASSE TRANSACAO ===================== #
class Transacao:
    def __init__(self, tipo, valor, conta_origem, conta_destino=None):
        self.tipo = tipo  # Tipo da transação: 'depósito', 'saque' ou 'transferência'
        self.valor = valor  # Valor da transação (float)
        self.data = datetime.now()  # Armazena o horário atual da transação
        self.conta_origem = conta_origem  # Conta de onde saiu o dinheiro
        self.conta_destino = conta_destino  # Conta que recebeu o dinheiro (apenas para transferências)

    def __str__(self):
        data_formatada = self.data.strftime('%d/%m/%Y %H:%M:%S')
        if self.tipo == 'transferência':
            return f"{data_formatada} - {self.tipo.title()} de R${self.valor:.2f} para conta {self.conta_destino.numero}"
        return f"{data_formatada} - {self.tipo.title()} de R${self.valor:.2f}"

# ===================== CONTA CORRENTE ===================== #
# class: Define uma classe filha que herda de Conta (herança).
class ContaCorrente(Conta):
    # Sobrescreve atributos de classe (polimorfismo).
    TAXA_JUROS_VIGENTE = 1.99  # Exemplo: 1,99% ao mês
    TAXA_JUROS_ANUAL = 26.82   # Exemplo: 26,82% ao ano
    IOF_BASICO = 0.38          # Exemplo: 0,38%
    IOF_ADICIONAL = 0.0082     # Exemplo: 0,0082% ao dia
    CET_MENSAL = 2.5           # Exemplo: 2,5% ao mês
    CET_ANUAL = 34.49          # Exemplo: 34,49% ao ano

    def __init__(self, numero, cliente, limite=500.0):
        # super(): Chama métodos da classe base (superclasse).
        super().__init__(numero, cliente)
        self.limite = limite  # Limite adicional para saque

    def sacar(self, valor):
        # Sobrescreve o método sacar para considerar o limite
        if valor <= 0:
            raise ValueError("O valor do saque deve ser positivo.")
        if self._saldo + self.limite < valor:
            raise ValueError("Saldo e limite insuficientes.")
        self._saldo -= valor
        self.registrar_transacao(Transacao('saque', valor, self))

    def tem_limite(self):
        # Indica que esta conta possui limite
        return True

    def mostrar_limite(self):
        # Exibe o limite disponível
        return f"Limite disponível para operação: R${self.limite:.2f}"

    def alterar_limite(self, novo_limite):
        # Permite alterar o limite da conta corrente
        if novo_limite < 0:
            print("O limite não pode ser negativo.")
        else:
            self.limite = novo_limite
            print(f"Novo limite definido: R${self.limite:.2f}")

# ===================== CONTA POUPANÇA ===================== #
class ContaPoupanca(Conta):
    TAXA_JUROS_VIGENTE = 0.5   # Exemplo: 0,5% ao mês
    TAXA_JUROS_ANUAL = 6.17    # Exemplo: 6,17% ao ano
    IOF_BASICO = 0.0           # Poupança geralmente isenta de IOF
    IOF_ADICIONAL = 0.0
    CET_MENSAL = 0.5           # Exemplo: 0,5% ao mês
    CET_ANUAL = 6.17           # Exemplo: 6,17% ao ano

    def transferir(self, valor, conta_destino):
        # raise: Lança uma exceção (erro).
        raise NotImplementedError("Transferências não são permitidas em contas poupança.")

# ===================== CLASSE BANCO ===================== #
class Banco:
    def __init__(self):
        self.contas = {}  # Dicionário que armazena as contas no formato {numero: Conta}

    def criar_conta_corrente(self, numero, nome, cpf, limite):
        cliente = Cliente(nome, cpf)
        conta = ContaCorrente(numero, cliente, limite)
        self.contas[numero] = conta
        print(f"Conta Corrente {numero} criada com sucesso.")

    def criar_conta_poupanca(self, numero, nome, cpf):
        cliente = Cliente(nome, cpf)
        conta = ContaPoupanca(numero, cliente)
        self.contas[numero] = conta
        print(f"Conta Poupança {numero} criada com sucesso.")

    def listar_contas(self):
        print("\nContas cadastradas e suas funcionalidades:")
        for conta in self.contas.values():
            tipo_conta = conta.__class__.__name__
            is_pj = '/' in conta.cliente.cpf
            tipo_pessoa = "Pessoa Jurídica" if is_pj else "Pessoa Física"
            print(f"{tipo_conta} ({tipo_pessoa}) | Número: {conta.numero} | Titular: {conta.cliente.nome} | Saldo: R${conta.saldo:.2f}")
            print(f"  - {conta.mostrar_limite()}")
            print(f"  - {conta.exibir_pix()}")
            if tipo_conta == "ContaCorrente":
                print("  - Permite: Saque, Depósito, Transferência")
                print("  - Pode operar no negativo até o valor do limite")
            elif tipo_conta == "ContaPoupanca":
                print("  - Permite: Saque, Depósito")
                print("  - Não permite transferências")
            alteracao = "Já teve alteração de titularidade" if conta.cliente.historico_titularidade else "Titularidade nunca foi alterada"
            print(f"  - {alteracao}")

    def buscar_conta(self, numero):
        # return: Retorna um valor de uma função/método.
        return self.contas.get(numero)

    def buscar_contas_por_nome_ou_cpf(self, termo):
        resultado = []
        for conta in self.contas.values():
            # in: Usado para percorrer elementos de uma lista ou verificar se um valor está em uma coleção.
            if conta.cliente.nome.lower() == termo.lower() or conta.cliente.cpf == termo:
                resultado.append(conta)
        return resultado

# ===================== INTERFACE DE USUÁRIO ===================== #
def menu():
    print("\nMenu:")
    print("1 - Listar contas")
    print("2 - Depositar")
    print("3 - Sacar")
    print("4 - Transferir")
    print("5 - Extrato")
    print("6 - Criar nova conta")
    print("7 - Alterar titular da conta (por número, nome ou CPF/CNPJ)")
    print("8 - Ver histórico de titularidade")
    print("9 - Alterar limite da conta corrente")
    print("10 - Cadastrar chave Pix")
    print("11 - Alterar chave Pix")
    print("12 - Sair")

# ===================== PROGRAMA PRINCIPAL ===================== #
# if __name__ == "__main__": é o ponto de entrada do programa.
if __name__ == "__main__":
    banco = Banco()  # Cria o banco

    # Criação de contas iniciais para simulação
    banco.criar_conta_poupanca("1010", "Maria Silva", "123.456.789-00")
    banco.criar_conta_corrente("2020", "João Oliveira", "987.654.321-00", limite=1000.0)
    banco.criar_conta_corrente("3030", "Tech Solutions LTDA", "12.345.678/0001-99", limite=5000.0)

    while True:
        menu()
        # input: Recebe dados do usuário.
        opcao = input("Escolha uma opção: ")

        # try, except: Bloco de tratamento de erros.
        try:
            if opcao == "1":
                banco.listar_contas()

            elif opcao == "2":
                numero = input("Conta: ")
                valor = float(input("Valor do depósito: "))
                conta = banco.buscar_conta(numero)
                if conta:
                    conta.depositar(valor)
                    print("Depósito realizado com sucesso!")
                else:
                    print("Conta não encontrada.")

            elif opcao == "3":
                numero = input("Conta: ")
                valor = float(input("Valor do saque: "))
                conta = banco.buscar_conta(numero)
                if conta:
                    conta.sacar(valor)
                    print("Saque realizado com sucesso!")
                else:
                    print("Conta não encontrada.")

            elif opcao == "4":
                origem = input("Conta de origem: ")
                destino = input("Conta de destino: ")
                valor = float(input("Valor da transferência: "))
                conta_origem = banco.buscar_conta(origem)
                conta_destino = banco.buscar_conta(destino)
                if conta_origem and conta_destino:
                    conta_origem.transferir(valor, conta_destino)
                    print("Transferência realizada com sucesso!")
                else:
                    print("Conta de origem ou destino não encontrada.")

            elif opcao == "5":
                numero = input("Conta: ")
                conta = banco.buscar_conta(numero)
                if conta:
                    conta.extrato()
                else:
                    print("Conta não encontrada.")

            elif opcao == "6":
                tipo = input("Tipo (1 - Corrente, 2 - Poupança): ")
                numero = input("Número da conta: ")
                nome = input("Nome do titular: ")
                cpf = input("CPF ou CNPJ do titular: ")
                if tipo == "1":
                    limite = float(input("Limite da conta: "))
                    banco.criar_conta_corrente(numero, nome, cpf, limite)
                elif tipo == "2":
                    banco.criar_conta_poupanca(numero, nome, cpf)
                else:
                    print("Tipo inválido.")

            elif opcao == "7":
                print("\nVocê pode buscar a conta pelo número, nome do titular ou CPF/CNPJ.")
                termo = input("Digite o número da conta, nome do titular ou CPF/CNPJ: ")
                contas_encontradas = []
                conta = banco.buscar_conta(termo)
                if conta:
                    contas_encontradas = [conta]
                else:
                    contas_encontradas = banco.buscar_contas_por_nome_ou_cpf(termo)
                if not contas_encontradas:
                    print("Nenhuma conta encontrada para o termo informado.")
                elif len(contas_encontradas) == 1:
                    nova_titularidade = input("Novo nome do titular: ")
                    contas_encontradas[0].alterar_titular(nova_titularidade)
                else:
                    print("Foram encontradas várias contas para este titular/CPF/CNPJ:")
                    for idx, c in enumerate(contas_encontradas):
                        print(f"{idx+1} - Conta: {c.numero} | Titular: {c.cliente.nome} | Tipo: {c.__class__.__name__}")
                    escolha = int(input("Digite o número da conta que deseja alterar (escolha pelo índice): ")) - 1
                    if 0 <= escolha < len(contas_encontradas):
                        nova_titularidade = input("Novo nome do titular: ")
                        contas_encontradas[escolha].alterar_titular(nova_titularidade)
                    else:
                        print("Opção inválida.")

            elif opcao == "8":
                numero = input("Número da conta: ")
                conta = banco.buscar_conta(numero)
                if conta:
                    print(f"\nConta: {conta.numero}")
                    print(f"Titular atual: {conta.cliente.nome}")
                    print(f"CPF/CNPJ: {conta.cliente.cpf}")
                    print(conta.exibir_pix())
                    conta.cliente.ver_historico_titularidade()
                else:
                    print("Conta não encontrada.")

            elif opcao == "9":
                print("\nVocê pode buscar a conta pelo número, nome do titular ou CPF/CNPJ.")
                termo = input("Digite o número da conta, nome do titular ou CPF/CNPJ: ")
                contas_encontradas = []
                conta = banco.buscar_conta(termo)
                # isinstance(): Verifica se um objeto é de um determinado tipo/classe.
                if conta and isinstance(conta, ContaCorrente):
                    contas_encontradas = [conta]
                else:
                    contas_encontradas = [c for c in banco.buscar_contas_por_nome_ou_cpf(termo) if isinstance(c, ContaCorrente)]
                if not contas_encontradas:
                    print("Nenhuma conta corrente encontrada para o termo informado.")
                elif len(contas_encontradas) == 1:
                    print(f"Limite atual: R${contas_encontradas[0].limite:.2f}")
                    novo_limite = float(input("Digite o novo limite: "))
                    contas_encontradas[0].alterar_limite(novo_limite)
                else:
                    print("Foram encontradas várias contas correntes para este titular/CPF/CNPJ:")
                    for idx, c in enumerate(contas_encontradas):
                        print(f"{idx+1} - Conta: {c.numero} | Titular: {c.cliente.nome} | Limite atual: R${c.limite:.2f}")
                    escolha = int(input("Digite o número da conta que deseja alterar o limite (escolha pelo índice): ")) - 1
                    if 0 <= escolha < len(contas_encontradas):
                        print(f"Limite atual: R${contas_encontradas[escolha].limite:.2f}")
                        novo_limite = float(input("Digite o novo limite: "))
                        contas_encontradas[escolha].alterar_limite(novo_limite)
                    else:
                        print("Opção inválida.")

            elif opcao == "10":
                numero = input("Número da conta: ")
                conta = banco.buscar_conta(numero)
                if conta:
                    chave = input("Digite a chave Pix para cadastrar: ")
                    conta.cadastrar_pix(chave)
                else:
                    print("Conta não encontrada.")

            elif opcao == "11":
                numero = input("Número da conta: ")
                conta = banco.buscar_conta(numero)
                if conta:
                    nova_chave = input("Digite a nova chave Pix: ")
                    conta.alterar_pix(nova_chave)
                else:
                    print("Conta não encontrada.")

            elif opcao == "12":
                print("Saindo...")
                break

            else:
                print("Opção inválida.")

        except Exception as e:
            print(f"Ocorreu um erro: {e}")

# ----------------------------------------------------------
# Palavras-chave importantes do Python usadas neste código:
# class: Define uma classe (molde para criar objetos).
# def: Define uma função ou método.
# self: Referência ao próprio objeto (usado dentro de métodos de classe).
# __init__: Método construtor, chamado ao criar um novo objeto.
# return: Retorna um valor de uma função/método.
# if, elif, else: Estruturas de decisão (condicionais).
# for: Estrutura de repetição (laço).
# in: Usado para percorrer elementos de uma lista ou verificar se um valor está em uma coleção.
# raise: Lança uma exceção (erro).
# try, except: Bloco de tratamento de erros.
# print: Exibe informações na tela.
# input: Recebe dados do usuário.
# True, False: Valores booleanos (verdadeiro/falso).
# None: Representa a ausência de valor.
# @property: Permite acessar um método como se fosse um atributo.
# super(): Chama métodos da classe base (superclasse).
# isinstance(): Verifica se um objeto é de um determinado tipo/classe.
# strip(): Remove espaços em branco do início e fim de uma string.
# re.match(): Verifica se uma string corresponde a um padrão (expressão regular).
# append(): Adiciona um item ao final de uma lista.
# format/string f"{}": Formata strings de maneira prática.

# ----------------------------------------------------------
# CONCEITOS DE PROGRAMAÇÃO ORIENTADA A OBJETOS NO CÓDIGO:
# - Classe: Molde para criar objetos (ex: Cliente, Conta, Banco).
# - Objeto: Instância de uma classe (ex: uma conta específica).
# - Herança: ContaCorrente e ContaPoupanca herdam de Conta.
# - Encapsulamento: Uso de atributos protegidos (ex: _saldo).
# - Composição: Uma Conta possui um Cliente.
# - Polimorfismo: Métodos sobrescritos em subclasses (ex: sacar, transferir).
# - Métodos de instância: Funções que atuam sobre o objeto (ex: depositar, sacar).
# - Métodos especiais: __init__, __str__.