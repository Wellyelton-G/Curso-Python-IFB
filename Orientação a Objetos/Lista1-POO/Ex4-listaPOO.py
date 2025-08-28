class Produto:
    def __init__(self, nome, preco, quantidade):
        # Atributos privados (não acessados diretamente fora da classe)
        self.__nome = nome
        self.__preco = preco
        self.__quantidade = quantidade

    # ==== Getters (métodos públicos para acessar valores) ====
    #Get sinifica obter, pegar, getters devolve o valor do atributo.
    # São usados para obter o valor dos atributos privados.
    def get_nome(self):  # método público
        return self.__nome

    def get_preco(self):  # método público
        return self.__preco

    def get_quantidade(self):  # método público
        return self.__quantidade

    # ==== Setters (métodos públicos para modificar valores) ====
    #Set significa definir, ajustar, setters alteram o valor do atributo.Normalmente, setters incluem validações.
    # São usados para alterar o valor dos atributos privados.

    def set_nome(self, novo_nome):  # método público
        self.__nome = novo_nome

    def set_preco(self, novo_preco):  # método público
        if novo_preco >= 0:  # só aceita preço positivo
            self.__preco = novo_preco

    def set_quantidade(self, nova_quantidade):  # método público
        if nova_quantidade >= 0:  # só aceita quantidade positiva
            self.__quantidade = nova_quantidade

# Getter → “pega” o valor do atributo privado.

#Setter → “define/atualiza” o valor do atributo privado, de forma controlada.

#Isso garante segurança e organização no código.

class CarrinhoDeCompras:
    def __init__(self):
        # Lista que armazena objetos Produto
        self.produtos = []

    def adicionar_produto(self, produto):  # método público
        self.produtos.append(produto)

    def remover_produto(self, nome):  # método público
        for produto in self.produtos:
            if produto.get_nome().lower() == nome.lower():
                self.produtos.remove(produto)
                print(f"Produto '{nome}' removido do carrinho.")
                return
        print(f"Produto '{nome}' não encontrado no carrinho.")

    def calcular_total(self):  # método público
        total = 0
        for produto in self.produtos:
            total += produto.get_preco() * produto.get_quantidade()
        return total

    def listar_produtos(self):  # método público
        if not self.produtos:
            print("Carrinho vazio!")
        else:
            print("\n--- Produtos no Carrinho ---")
            for produto in self.produtos:
                print(f"{produto.get_nome()} - R${produto.get_preco():.2f} x {produto.get_quantidade()}")
            print("---------------------------")
            print(f"Total: R${self.calcular_total():.2f}")


# ================= PROGRAMA PRINCIPAL =================
if __name__ == "__main__":
    carrinho = CarrinhoDeCompras()

    while True:
        print("\n=== MENU CARRINHO DE COMPRAS ===")
        print("1. Adicionar produto")
        print("2. Remover produto")
        print("3. Listar produtos")
        print("4. Ver total da compra")
        print("5. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            nome = input("Nome do produto: ")
            preco = float(input("Preço do produto: "))
            quantidade = int(input("Quantidade: "))
            produto = Produto(nome, preco, quantidade)  # cria objeto Produto
            carrinho.adicionar_produto(produto)
            print(f"Produto '{nome}' adicionado com sucesso!")

        elif opcao == "2":
            nome = input("Nome do produto a remover: ")
            carrinho.remover_produto(nome)

        elif opcao == "3":
            carrinho.listar_produtos()

        elif opcao == "4":
            print(f"Valor total da compra: R${carrinho.calcular_total():.2f}")

        elif opcao == "5":
            print("Saindo do programa... Obrigado por usar o carrinho!")
            break

        else:
            print("Opção inválida! Tente novamente.")
