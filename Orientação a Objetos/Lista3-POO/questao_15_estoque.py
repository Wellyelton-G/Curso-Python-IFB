"""Questao 15: encapsulamento, agregacao e excecoes de negocio."""


class EstoqueInsuficienteError(Exception):
    pass


class Produto:
    def __init__(self, codigo, nome, preco, quantidade=0):
        self.codigo = codigo
        self.nome = nome
        self.preco = preco
        self.__quantidade = quantidade

    @property
    def quantidade(self):
        # A property permite consultar sem permitir atribuicao direta comum.
        return self.__quantidade

    def adicionar(self, unidades):
        if unidades <= 0:
            raise ValueError("As unidades devem ser positivas.")
        self.__quantidade += unidades

    def retirar(self, unidades):
        if unidades <= 0:
            raise ValueError("As unidades devem ser positivas.")
        # Uma excecao especifica diferencia falta de estoque de outros erros.
        if unidades > self.__quantidade:
            raise EstoqueInsuficienteError("Quantidade solicitada maior que o estoque disponível.")
        self.__quantidade -= unidades

    def valor_em_estoque(self):
        return self.preco * self.__quantidade


class Estoque:
    def __init__(self):
        self.produtos = {}

    def cadastrar_produto(self, produto):
        if produto.codigo in self.produtos:
            raise ValueError("Código já cadastrado.")
        self.produtos[produto.codigo] = produto

    def consultar(self, codigo):
        return self.produtos.get(codigo)

    def listar_baixo_estoque(self):
        # A compreensao cria uma nova lista apenas com itens abaixo do limite.
        return [p for p in self.produtos.values() if p.quantidade < 5]

    def calcular_valor_total(self):
        return sum(p.valor_em_estoque() for p in self.produtos.values())


if __name__ == "__main__":
    estoque = Estoque()
    produto = Produto("P001", "Mouse", 80, 7)
    estoque.cadastrar_produto(produto)
    produto.retirar(3)

    for item in estoque.listar_baixo_estoque():
        print(f"Baixo estoque: {item.nome}, {item.quantidade} unidade(s).")

    print(f"Valor total: R$ {estoque.calcular_valor_total():.2f}")
