from abc import ABC, abstractmethod
from pathlib import Path
import json
import os
import tempfile


class Endereco:
    def __init__(self, cidade, cep):
        self.cidade = cidade
        self.cep = cep


class Cliente:
    def __init__(self, nome, email, endereco):
        self.nome = nome
        self.email = email
        self.endereco = endereco


class Produto:
    def __init__(self, codigo, nome, preco, estoque):
        self.codigo = codigo
        self.nome = nome
        self.preco = preco
        self.estoque = estoque


class ItemCarrinho:
    def __init__(self, produto, quantidade):
        if quantidade <= 0:
            raise ValueError("Quantidade inválida.")
        self.produto = produto
        self.quantidade = quantidade

    def subtotal(self):
        return self.produto.preco * self.quantidade


class Cupom:
    def __init__(self, codigo, percentual):
        self.codigo = codigo
        self.percentual = percentual


class Carrinho:
    def __init__(self):
        self.itens = []
        self.cupom = None

    def adicionar(self, produto, quantidade):
        if quantidade > produto.estoque:
            raise ValueError("Estoque insuficiente.")
        self.itens.append(ItemCarrinho(produto, quantidade))

    def remover(self, codigo):
        self.itens = [i for i in self.itens if i.produto.codigo != codigo]

    def aplicar_cupom(self, cupom):
        self.cupom = cupom

    def total(self):
        bruto = sum(i.subtotal() for i in self.itens)
        desconto = bruto * self.cupom.percentual / 100 if self.cupom else 0
        return bruto - desconto


class Pagamento(ABC):
    @abstractmethod
    def pagar(self, valor):
        pass


class PagamentoPix(Pagamento):
    def pagar(self, valor):
        return {"forma": "Pix", "valor": valor, "status": "Aprovado"}


class PagamentoCartao(Pagamento):
    def pagar(self, valor):
        return {"forma": "Cartão", "valor": valor, "status": "Aprovado"}


class Pedido:
    def __init__(self, cliente, carrinho, pagamento):
        self.cliente = cliente
        self.itens = list(carrinho.itens)
        self.valor = carrinho.total()
        self.pagamento = pagamento.pagar(self.valor)
        self.status = "Pago"

        # O estoque é reduzido somente após a aprovação do pagamento.
        for item in self.itens:
            item.produto.estoque -= item.quantidade

    def atualizar_status(self, status):
        self.status = status


class RepositorioJSON:
    def __init__(self, arquivo):
        self.arquivo = Path(arquivo)

    def salvar(self, dados):
        self.arquivo.parent.mkdir(parents=True, exist_ok=True)

        # Gravação atômica. Primeiro gravamos em arquivo temporário e só depois substituímos o original.
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", delete=False, dir=self.arquivo.parent
        ) as temporario:
            json.dump(dados, temporario, ensure_ascii=False, indent=2)
            temporario.flush()
            os.fsync(temporario.fileno())
            nome_temporario = temporario.name

        os.replace(nome_temporario, self.arquivo)

    def carregar(self):
        if not self.arquivo.exists():
            return {}
        try:
            return json.loads(self.arquivo.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("Arquivo corrompido. Um conjunto vazio será usado.")
            return {}


if __name__ == "__main__":
    produto = Produto("P1", "Notebook", 3500, 3)
    cliente = Cliente("Ana", "ana@exemplo.com", Endereco("Brasília", "70000-000"))
    carrinho = Carrinho()
    carrinho.adicionar(produto, 1)
    carrinho.aplicar_cupom(Cupom("DESC10", 10))

    pedido = Pedido(cliente, carrinho, PagamentoPix())
    frete = 25.0
    total_com_frete = pedido.valor + frete

    repositorio = RepositorioJSON("dados/pedidos.json")
    repositorio.salvar({
        "cliente": cliente.nome,
        "valor": pedido.valor,
        "frete": frete,
        "total": total_com_frete,
        "status": pedido.status
    })
    print(f"Pedido salvo. Total com frete: R$ {total_com_frete:.2f}")
