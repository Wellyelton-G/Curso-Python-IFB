"""Questao 19: Strategy para trocar a forma de pagamento."""

from abc import ABC, abstractmethod


class Produto:
    def __init__(self, nome, preco):
        self.nome = nome
        self.preco = preco


class Carrinho:
    def __init__(self):
        self.produtos = []

    def adicionar(self, produto):
        self.produtos.append(produto)

    def calcular_total(self):
        return sum(produto.preco for produto in self.produtos)

    def finalizar_compra(self, forma_pagamento):
        # Carrinho depende apenas do contrato pagar(), nao de uma classe concreta.
        return forma_pagamento.pagar(self.calcular_total())


class FormaPagamento(ABC):
    @abstractmethod
    def pagar(self, valor):
        pass


class PagamentoDinheiro(FormaPagamento):
    def pagar(self, valor):
        # Multiplicar por 0,95 equivale a descontar 5%.
        return valor * 0.95


class PagamentoCartao(FormaPagamento):
    def pagar(self, valor):
        return valor * 1.02


class PagamentoPix(FormaPagamento):
    def pagar(self, valor):
        return valor * 0.97


if __name__ == "__main__":
    carrinho = Carrinho()
    carrinho.adicionar(Produto("Livro", 90))
    carrinho.adicionar(Produto("Caderno", 30))

    for forma in [PagamentoDinheiro(), PagamentoCartao(), PagamentoPix()]:
        print(f"{forma.__class__.__name__}: R$ {carrinho.finalizar_compra(forma):.2f}")
