class Produto:
    def __init__(self, nome, preco):
        self.nome = nome
        self.preco = preco


class ItemPedido:
    def __init__(self, produto, quantidade):
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser positiva.")
        self.produto = produto
        self.quantidade = quantidade

    def subtotal(self):
        return self.produto.preco * self.quantidade


class Pedido:
    def __init__(self):
        self.itens = []
        self.finalizado = False

    def adicionar_item(self, item):
        if self.finalizado:
            raise RuntimeError("O pedido já foi finalizado.")
        self.itens.append(item)

    def remover_item(self, nome_produto):
        if self.finalizado:
            raise RuntimeError("O pedido já foi finalizado.")
        for item in self.itens:
            if item.produto.nome.lower() == nome_produto.lower():
                self.itens.remove(item)
                return True
        return False

    def listar_itens(self):
        for item in self.itens:
            print(f"{item.produto.nome} x {item.quantidade}: R$ {item.subtotal():.2f}")

    def calcular_total(self):
        return sum(item.subtotal() for item in self.itens)

    def finalizar(self):
        if not self.itens:
            raise RuntimeError("Não é possível finalizar um pedido vazio.")
        self.finalizado = True
        print(f"Pedido finalizado. Total: R$ {self.calcular_total():.2f}")


if __name__ == "__main__":
    pedido = Pedido()
    pedido.adicionar_item(ItemPedido(Produto("Prato executivo", 22), 2))
    pedido.adicionar_item(ItemPedido(Produto("Suco", 6), 1))
    pedido.listar_itens()
    pedido.finalizar()
