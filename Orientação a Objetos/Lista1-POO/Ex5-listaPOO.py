class Documento:
    def __init__(self, titulo, conteudo):
        self.__titulo = titulo      # atributo privado
        self.__conteudo = conteudo  # atributo privado

    # ==== Getters (métodos públicos para acesso seguro) ====
    def get_titulo(self):
        return self.__titulo

    def get_conteudo(self):
        return self.__conteudo


class Impressora:
    # Aqui está a relação de DEPENDÊNCIA:
    # O método imprimir RECEBE um objeto da classe Documento como parâmetro,
    # usa seus dados (get_titulo e get_conteudo) para mostrar na tela,
    # mas NÃO guarda esse objeto permanentemente.
    def imprimir(self, documento):
        print("\n=== IMPRESSÃO ===")
        print(f"Título: {documento.get_titulo()}")     # dependência: usa método de Documento
        print(f"Conteúdo: {documento.get_conteudo()}") # dependência: usa método de Documento
        print("=================")
# Impressora depende da classe Documento porque recebe um objeto dela.

# ================= PROGRAMA PRINCIPAL =================
if __name__ == "__main__":
    documentos = []       # lista para guardar objetos Documento
    impressora = Impressora()  # objeto Impressora

    while True:
        print("\n=== MENU ===")
        print("1. Criar novo documento")
        print("2. Listar documentos")
        print("3. Imprimir documento")
        print("4. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            titulo = input("Digite o título do documento: ")
            conteudo = input("Digite o conteúdo do documento: ")
            doc = Documento(titulo, conteudo)  # cria objeto Documento
            documentos.append(doc)
            print("Documento criado com sucesso!")

        elif opcao == "2":
            if not documentos:
                print("Nenhum documento criado ainda.")
            else:
                print("\n--- Documentos Criados ---")
                for i, doc in enumerate(documentos, 1):
                    print(f"{i}. {doc.get_titulo()}")

        elif opcao == "3":
            if not documentos:
                print("Nenhum documento disponível para impressão.")
            else:
                num = int(input("Digite o número do documento para imprimir: "))
                if 1 <= num <= len(documentos):
                    # Dependência acontece AQUI: passamos o Documento para a Impressora
                    impressora.imprimir(documentos[num - 1])
                    #impressora usa um Documento só no momento da impressão.
                else:
                    print("Número inválido!")

        elif opcao == "4":
            print("Encerrando o programa... Até logo!")
            break

        else:
            print("Opção inválida, tente novamente!")
