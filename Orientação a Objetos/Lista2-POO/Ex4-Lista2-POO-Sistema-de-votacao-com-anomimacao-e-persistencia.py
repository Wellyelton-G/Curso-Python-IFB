import hashlib           # import: importa um módulo externo para uso no código
import json              # import: importa o módulo json para ler/salvar arquivos JSON
import os                # import: importa o módulo os para interagir com o sistema operacional
from pathlib import Path  # from/import: importa apenas Path do módulo pathlib (é um módulo para manipulação de caminhos de arquivos e pastas de forma orientada a objetos e multiplataforma).

# Caminho seguro para o arquivo de votos (pasta Downloads do usuário)
CAMINHO_VOTOS = Path.home() / "Downloads" / "votos.json"  # /: operador de caminho do pathlib

# class: define uma nova classe em Python (conceito de classe/objeto da POO)
class Candidato:
    # def: define um método ou função
    def __init__(self, nome):  # self: referência ao próprio objeto (conceito de encapsulamento)
        self.nome = nome       # self: usado para acessar atributos do objeto
        self.votos = 0         # Atributo que armazena a quantidade de votos (atributo de instância)

# class: define uma nova classe para representar o eleitor (abstração)
class Eleitor:
    def __init__(self, cpf):
        # hashlib.sha256: cria um hash seguro do CPF (encapsulamento dos dados sensíveis)
        # encode(): converte string para bytes
        # hexdigest(): retorna o hash como string hexadecimal
        self.cpf_hash = hashlib.sha256(cpf.encode()).hexdigest()

# class: define a classe principal que gerencia a eleição (abstração e composição)
class Eleicao:
    def __init__(self, candidatos, arquivo_votos=CAMINHO_VOTOS):
        # dict comprehension: cria um dicionário {nome: objeto_candidato}
        # composição: Eleicao possui candidatos (objetos Candidato)
        self.candidatos = {c.nome: c for c in candidatos}
        self.votos_anonimizados = set()   # set: conjunto para armazenar hashes dos CPFs (encapsulamento)
        self.arquivo_votos = arquivo_votos
        self._carregar_votos()            # Chama método para carregar votos do arquivo

    # Método privado (por convenção, começa com _) para carregar votos do arquivo (encapsulamento)
    def _carregar_votos(self):
        # if: estrutura condicional
        if os.path.exists(self.arquivo_votos):  # os.path.exists: verifica se o arquivo existe
            try:                                # try: tenta executar o bloco, except: captura erros
                with open(self.arquivo_votos, "r", encoding="utf-8") as f:  # with: gerencia contexto de arquivo
                    data = json.load(f)  # json.load: carrega dados do arquivo JSON
                    # set(): converte lista para conjunto
                    self.votos_anonimizados = set(data.get("votos", []))
                    # for: laço de repetição
                    for nome, votos in data.get("apuracao", {}).items():
                        if nome in self.candidatos:
                            self.candidatos[nome].votos = votos
            except Exception as e:  # except: captura exceções, Exception: classe base de erros, as: atribui erro à variável e
                print(f"Aviso: Não foi possível carregar votos anteriores ({e}). O sistema começará zerado.")

    # Método privado para salvar votos no arquivo (persistência e encapsulamento)
    def _salvar_votos(self):
        # Cria um dicionário com os dados a serem salvos
        data = {
            "votos": list(self.votos_anonimizados),  # list(): converte conjunto para lista
            "apuracao": {nome: c.votos for nome, c in self.candidatos.items()}  # dict comprehension
        }
        temp_file = str(self.arquivo_votos) + ".tmp"  # Cria nome de arquivo temporário
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)  # json.dump: salva dados em JSON
            os.replace(temp_file, self.arquivo_votos)  # os.replace: substitui arquivo antigo pelo novo
        except Exception as e:
            print(f"Erro ao salvar votos: {e}")

    # Método público para registrar um voto (polimorfismo: aceita qualquer objeto do tipo Eleitor)
    def votar(self, eleitor: 'Eleitor', nome_candidato: str):  # : indica tipagem opcional
        nome_candidato = nome_candidato.strip().title()  # strip: remove espaços, title: capitaliza

        # in: verifica se elemento está no conjunto (controle de duplicidade)
        if eleitor.cpf_hash in self.votos_anonimizados:
            print("Este eleitor já votou.")
            return False  # return: encerra a função e retorna valor

        # not in: verifica se elemento NÃO está no dicionário
        if nome_candidato not in self.candidatos:
            print("Candidato não encontrado.")
            return False

        self.candidatos[nome_candidato].votos += 1  # +=: incrementa valor
        self.votos_anonimizados.add(eleitor.cpf_hash)  # add: adiciona elemento ao conjunto
        print("Voto registrado com sucesso!")
        return True

    # Método público para mostrar o resultado da eleição (abstração)
    def resultado(self):
        total_votos = sum(c.votos for c in self.candidatos.values())  # sum: soma valores, for: laço de repetição
        if total_votos == 0:
            print("Nenhum voto registrado.")
            return

        print("\nResultado da Eleição:")
        maior = max(c.votos for c in self.candidatos.values())  # max: retorna maior valor
        vencedores = [c.nome for c in self.candidatos.values() if c.votos == maior]  # list comprehension, if: filtro

        for c in self.candidatos.values():
            percentual = (c.votos / total_votos) * 100  # /: divisão, *: multiplicação
            print(f"{c.nome}: {c.votos} voto(s) ({percentual:.2f}%)")  # f-string: interpolação de variáveis

        if len(vencedores) == 1:  # len: retorna tamanho da lista
            print(f"\n Vencedor: {vencedores[0]}")
        else:
            print(f"\n Empate entre: {', '.join(vencedores)}")  # ', '.join: junta elementos da lista em string

# Função principal que exibe o menu e controla o fluxo do programa (abstração e encapsulamento)
def menu():
    candidatos = [Candidato("Alice"), Candidato("Bob"), Candidato("Carol")]  # lista de objetos (instâncias de Candidato)
    eleicao = Eleicao(candidatos)  # instancia a eleição (composição: Eleicao possui candidatos)

    try:  # try: tenta executar o bloco, except: captura interrupção
        while True:  # while: laço de repetição infinito até break
            print("\n=== MENU ===")
            print("1 - Votar")
            print("2 - Resultado da Eleição")
            print("3 - Sair")
            opcao = input("Escolha uma opção: ").strip()  # input: lê entrada do usuário, strip: remove espaços

            if opcao == "1":  # if: estrutura condicional
                cpf = input("Digite seu CPF: ").strip()
                if not cpf:  # not: negação lógica
                    print("CPF não pode ser vazio.")
                    continue  # continue: volta ao início do laço
                eleitor = Eleitor(cpf)  # Cria um objeto Eleitor (instanciação)

                print("Candidatos:")
                for nome in sorted(eleicao.candidatos):  # sorted: ordena nomes
                    print("-", nome)

                voto = input("Digite o nome do candidato: ").strip()
                if not voto:
                    print("Nome do candidato não pode ser vazio.")
                    continue

                eleicao.votar(eleitor, voto)  # Chama método da classe Eleicao (encapsulamento)

            elif opcao == "2":
                eleicao.resultado()  # Chama método da classe Eleicao

            elif opcao == "3":
                print(" Salvando votos e encerrando...")
                eleicao._salvar_votos()
                break  # break: encerra o laço while

            else:
                print(" Opção inválida. Tente novamente.")

    except KeyboardInterrupt:  # except: captura interrupção por Ctrl+C
        print("\n Encerrado com Ctrl+C. Salvando votos...")
        eleicao._salvar_votos()

# if: estrutura condicional especial para executar o código principal apenas se o arquivo for executado diretamente
if __name__ == "__main__":  # __name__: variável especial, __main__: valor quando executado diretamente
    menu()  # Chama a função principal do programa

# -----------------------------------------------------------
# CONCEITOS DE ORIENTAÇÃO A OBJETOS UTILIZADOS NESTE CÓDIGO:
# - Classe: estrutura que define um tipo de objeto (Candidato, Eleitor, Eleicao)
# - Objeto/Instância: cada candidato, eleitor ou eleição criado é um objeto
# - Encapsulamento: atributos e métodos ficam "dentro" das classes, protegendo dados sensíveis (ex: hash do CPF)
# - Abstração: cada classe representa um conceito do mundo real (candidato, eleitor, eleição)
# - Composição: a classe Eleicao é composta por vários objetos Candidato
# - Instanciação: criar objetos a partir das classes (ex: Eleitor(cpf))
# - Métodos: funções que pertencem a uma classe e manipulam seus dados (ex: votar, resultado)
# - Polimorfismo: métodos podem receber diferentes objetos do tipo esperado (ex: votar aceita qualquer Eleitor)
