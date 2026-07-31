"""Questao 29 - Comercio eletronico com persistencia JSON.

O dominio (clientes, produtos, carrinhos e pedidos) nao conhece detalhes do
arquivo. RepositorioJSON cuida da gravacao, enquanto SistemaEcommerce coordena
as regras. Essa separacao facilita testar e evoluir cada parte isoladamente.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
import json
import os
import tempfile


class EstoqueInsuficienteError(Exception):
    pass


class CupomInvalidoError(Exception):
    pass


class PagamentoRecusadoError(Exception):
    pass


class TransicaoStatusError(Exception):
    pass


class ArquivoCorrompidoError(Exception):
    pass


class Endereco:
    def __init__(self, cidade, cep, regiao="local"):
        self.cidade = cidade
        self.cep = cep
        self.regiao = regiao


class Cliente:
    def __init__(self, nome, email, endereco):
        self.nome = nome
        self.email = email
        self.endereco = endereco
        # Cada cliente possui seu proprio carrinho e historico de pedidos.
        self.carrinho = Carrinho()
        self.pedidos = []


class Produto:
    def __init__(self, codigo, nome, preco, estoque):
        if preco < 0 or estoque < 0:
            raise ValueError("Preco e estoque nao podem ser negativos.")
        self.codigo = codigo
        self.nome = nome
        self.preco = float(preco)
        self.__estoque = int(estoque)  # encapsulamento

    @property
    def estoque(self):
        return self.__estoque

    def retirar_estoque(self, quantidade):
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser positiva.")
        if quantidade > self.__estoque:
            raise EstoqueInsuficienteError(
                f"Estoque insuficiente para {self.nome}."
            )
        self.__estoque -= quantidade


class ItemCarrinho:
    """Composicao: o item existe como parte de um carrinho ou pedido."""

    def __init__(self, produto, quantidade, preco_unitario=None):
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser positiva.")
        self.produto = produto
        self.quantidade = int(quantidade)
        # O preco e copiado para preservar o valor historico de um pedido.
        self.preco_unitario = (
            produto.preco if preco_unitario is None else float(preco_unitario)
        )

    def subtotal(self):
        return self.preco_unitario * self.quantidade


class Cupom:
    def __init__(self, codigo, percentual, valor_minimo=0, ativo=True):
        if not 0 < percentual <= 100:
            raise ValueError("O percentual deve estar entre 0 e 100.")
        self.codigo = codigo
        self.percentual = float(percentual)
        self.valor_minimo = float(valor_minimo)
        self.ativo = ativo

    def calcular_desconto(self, valor):
        if not self.ativo:
            raise CupomInvalidoError("Cupom inativo.")
        if valor < self.valor_minimo:
            raise CupomInvalidoError("Valor minimo do cupom nao atingido.")
        return valor * self.percentual / 100


class Carrinho:
    def __init__(self):
        self.itens = []
        self.cupom = None

    def adicionar(self, produto, quantidade):
        # Somamos o que ja esta no carrinho. Sem isso, duas inclusoes menores
        # poderiam ultrapassar o estoque quando consideradas em conjunto.
        item_existente = next(
            (item for item in self.itens if item.produto is produto), None
        )
        quantidade_atual = item_existente.quantidade if item_existente else 0
        if quantidade_atual + quantidade > produto.estoque:
            raise EstoqueInsuficienteError(
                f"Existem apenas {produto.estoque} unidade(s) de {produto.nome}."
            )
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser positiva.")
        if item_existente:
            item_existente.quantidade += quantidade
        else:
            self.itens.append(ItemCarrinho(produto, quantidade))

    def remover(self, codigo, quantidade=None):
        item = next(
            (item for item in self.itens if item.produto.codigo == codigo), None
        )
        if item is None:
            raise ValueError("Produto nao encontrado no carrinho.")
        # Sem quantidade, removemos o item inteiro. Com quantidade, reduzimos.
        if quantidade is None or quantidade >= item.quantidade:
            self.itens.remove(item)
        elif quantidade <= 0:
            raise ValueError("A quantidade deve ser positiva.")
        else:
            item.quantidade -= quantidade

    def aplicar_cupom(self, cupom):
        # Validamos imediatamente para dar retorno rapido ao usuario.
        cupom.calcular_desconto(self.subtotal())
        self.cupom = cupom

    def subtotal(self):
        return sum(item.subtotal() for item in self.itens)

    def desconto(self):
        return self.cupom.calcular_desconto(self.subtotal()) if self.cupom else 0

    def total(self):
        return self.subtotal() - self.desconto()

    def limpar(self):
        self.itens.clear()
        self.cupom = None


class Pagamento(ABC):
    """Estrategia abstrata: cada forma implementa pagar de modo diferente."""

    @abstractmethod
    def pagar(self, valor):
        pass


class PagamentoPix(Pagamento):
    def pagar(self, valor):
        return {"forma": "Pix", "valor": valor, "status": "Aprovado"}


class PagamentoCartao(Pagamento):
    def __init__(self, limite):
        self.limite = float(limite)

    def pagar(self, valor):
        status = "Aprovado" if valor <= self.limite else "Recusado"
        return {"forma": "Cartao", "valor": valor, "status": status}


class PagamentoBoleto(Pagamento):
    def pagar(self, valor):
        # Um boleto emitido ainda aguarda compensacao, portanto fica pendente.
        return {"forma": "Boleto", "valor": valor, "status": "Pendente"}


class Pedido:
    TRANSICOES = {
        "Pago": {"Em preparacao", "Cancelado"},
        "Aguardando pagamento": {"Pago", "Cancelado"},
        "Em preparacao": {"Enviado", "Cancelado"},
        "Enviado": {"Entregue"},
        "Entregue": set(),
        "Cancelado": set(),
    }

    def __init__(
        self, numero, cliente, itens, pagamento, frete, criado_em=None, status=None
    ):
        self.numero = numero
        self.cliente = cliente
        # Criamos novos itens para que limpar o carrinho nao apague o pedido.
        self.itens = [
            ItemCarrinho(i.produto, i.quantidade, i.preco_unitario) for i in itens
        ]
        self.frete = float(frete)
        self.pagamento = pagamento
        self.criado_em = criado_em or datetime.now()
        self.status = status or (
            "Pago" if pagamento["status"] == "Aprovado" else "Aguardando pagamento"
        )

    @property
    def valor_produtos(self):
        return sum(item.subtotal() for item in self.itens)

    @property
    def valor_total(self):
        return self.pagamento["valor"]

    def atualizar_status(self, novo_status):
        if novo_status not in self.TRANSICOES[self.status]:
            raise TransicaoStatusError(
                f"Nao e possivel passar de {self.status} para {novo_status}."
            )
        self.status = novo_status


class RepositorioJSON:
    """Isola leitura e gravacao e protege o arquivo com escrita atomica."""

    def __init__(self, arquivo):
        self.arquivo = Path(arquivo)

    def salvar(self, dados):
        self.arquivo.parent.mkdir(parents=True, exist_ok=True)
        nome_temporario = None
        try:
            # O arquivo definitivo so e substituido depois que o temporario foi
            # completamente escrito e sincronizado com o disco.
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", delete=False, dir=self.arquivo.parent
            ) as temporario:
                json.dump(dados, temporario, ensure_ascii=False, indent=2)
                temporario.flush()
                os.fsync(temporario.fileno())
                nome_temporario = temporario.name
            os.replace(nome_temporario, self.arquivo)
        except (OSError, TypeError) as erro:
            if nome_temporario:
                try:
                    Path(nome_temporario).unlink(missing_ok=True)
                except OSError:
                    pass
            raise ArquivoCorrompidoError(
                f"Nao foi possivel salvar os dados: {erro}"
            ) from erro

    def carregar(self):
        if not self.arquivo.exists():
            return {}
        try:
            return json.loads(self.arquivo.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as erro:
            # Nao sobrescrevemos o arquivo defeituoso: ele pode ser analisado ou
            # recuperado posteriormente. O sistema inicia vazio com um aviso.
            print(f"Aviso: arquivo ausente ou corrompido ({erro}).")
            return {}


class SistemaEcommerce:
    """Fachada que cadastra, vende, persiste e restaura todos os objetos."""

    def __init__(self, repositorio):
        self.repositorio = repositorio
        self.clientes = {}
        self.produtos = {}
        self.cupons = {}
        self.pedidos = {}
        self._proximo_pedido = 1
        # Requisito do PDF: os dados sao carregados automaticamente ao iniciar.
        dados = self.repositorio.carregar()
        if dados:
            self._restaurar(dados)

    def cadastrar_cliente(self, cliente):
        if cliente.email in self.clientes:
            raise ValueError("Cliente ja cadastrado.")
        self.clientes[cliente.email] = cliente

    def cadastrar_produto(self, produto):
        if produto.codigo in self.produtos:
            raise ValueError("Produto ja cadastrado.")
        self.produtos[produto.codigo] = produto

    def cadastrar_cupom(self, cupom):
        self.cupons[cupom.codigo] = cupom

    def calcular_frete(self, cliente, carrinho):
        # Exemplo de regra: compras a partir de R$ 300 possuem frete gratis.
        if carrinho.total() >= 300:
            return 0.0
        adicionais = {"local": 0, "regional": 10, "nacional": 20}
        quantidade = sum(item.quantidade for item in carrinho.itens)
        return 12 + quantidade * 2 + adicionais.get(cliente.endereco.regiao, 25)

    def gerar_pedido(self, email_cliente, forma_pagamento):
        cliente = self.clientes[email_cliente]
        carrinho = cliente.carrinho
        if not carrinho.itens:
            raise ValueError("Nao e possivel gerar um pedido vazio.")

        # Conferimos novamente no fechamento, pois o estoque pode ter mudado
        # desde o momento em que o produto entrou no carrinho.
        for item in carrinho.itens:
            if item.quantidade > item.produto.estoque:
                raise EstoqueInsuficienteError(
                    f"Estoque insuficiente para {item.produto.nome}."
                )

        frete = self.calcular_frete(cliente, carrinho)
        valor_final = carrinho.total() + frete
        resultado = forma_pagamento.pagar(valor_final)
        if resultado["status"] == "Recusado":
            raise PagamentoRecusadoError("Pagamento recusado; estoque preservado.")

        pedido = Pedido(
            self._proximo_pedido,
            cliente,
            carrinho.itens,
            resultado,
            frete,
        )
        # Apenas pagamentos aprovados baixam o estoque imediatamente. Um boleto
        # pendente pode ser aprovado depois por uma rotina de confirmacao.
        if resultado["status"] == "Aprovado":
            for item in carrinho.itens:
                item.produto.retirar_estoque(item.quantidade)

        self.pedidos[pedido.numero] = pedido
        cliente.pedidos.append(pedido)
        self._proximo_pedido += 1
        carrinho.limpar()
        return pedido

    def salvar(self):
        self.repositorio.salvar(self._para_dict())

    def _para_dict(self):
        """Converte referencias de objetos em codigos adequados ao JSON."""
        return {
            "versao": 1,
            "proximo_pedido": self._proximo_pedido,
            "clientes": [
                {
                    "nome": c.nome,
                    "email": c.email,
                    "endereco": {
                        "cidade": c.endereco.cidade,
                        "cep": c.endereco.cep,
                        "regiao": c.endereco.regiao,
                    },
                    "carrinho": [
                        {"produto": i.produto.codigo, "quantidade": i.quantidade}
                        for i in c.carrinho.itens
                    ],
                    "cupom": c.carrinho.cupom.codigo if c.carrinho.cupom else None,
                }
                for c in self.clientes.values()
            ],
            "produtos": [
                {
                    "codigo": p.codigo,
                    "nome": p.nome,
                    "preco": p.preco,
                    "estoque": p.estoque,
                }
                for p in self.produtos.values()
            ],
            "cupons": [
                {
                    "codigo": c.codigo,
                    "percentual": c.percentual,
                    "valor_minimo": c.valor_minimo,
                    "ativo": c.ativo,
                }
                for c in self.cupons.values()
            ],
            "pedidos": [
                {
                    "numero": p.numero,
                    "cliente": p.cliente.email,
                    "itens": [
                        {
                            "produto": i.produto.codigo,
                            "quantidade": i.quantidade,
                            "preco_unitario": i.preco_unitario,
                        }
                        for i in p.itens
                    ],
                    "frete": p.frete,
                    "pagamento": p.pagamento,
                    "criado_em": p.criado_em.isoformat(),
                    "status": p.status,
                }
                for p in self.pedidos.values()
            ],
        }

    def _restaurar(self, dados):
        """Refaz primeiro objetos independentes e depois seus relacionamentos."""
        if dados.get("versao") != 1:
            raise ArquivoCorrompidoError("Versao de arquivo nao suportada.")

        for item in dados.get("produtos", []):
            produto = Produto(
                item["codigo"], item["nome"], item["preco"], item["estoque"]
            )
            self.produtos[produto.codigo] = produto
        for item in dados.get("cupons", []):
            cupom = Cupom(
                item["codigo"],
                item["percentual"],
                item["valor_minimo"],
                item["ativo"],
            )
            self.cupons[cupom.codigo] = cupom
        for item in dados.get("clientes", []):
            endereco = Endereco(**item["endereco"])
            cliente = Cliente(item["nome"], item["email"], endereco)
            self.clientes[cliente.email] = cliente
            for dados_item in item.get("carrinho", []):
                cliente.carrinho.adicionar(
                    self.produtos[dados_item["produto"]], dados_item["quantidade"]
                )
            codigo_cupom = item.get("cupom")
            if codigo_cupom:
                cliente.carrinho.aplicar_cupom(self.cupons[codigo_cupom])
        for item in dados.get("pedidos", []):
            cliente = self.clientes[item["cliente"]]
            itens = [
                ItemCarrinho(
                    self.produtos[dado["produto"]],
                    dado["quantidade"],
                    dado["preco_unitario"],
                )
                for dado in item["itens"]
            ]
            pedido = Pedido(
                item["numero"],
                cliente,
                itens,
                item["pagamento"],
                item["frete"],
                datetime.fromisoformat(item["criado_em"]),
                item["status"],
            )
            self.pedidos[pedido.numero] = pedido
            cliente.pedidos.append(pedido)
        self._proximo_pedido = dados.get("proximo_pedido", 1)


if __name__ == "__main__":
    # O JSON fica ao lado deste arquivo, independentemente do diretorio atual.
    arquivo = Path(__file__).with_name("dados_ecommerce.json")
    sistema = SistemaEcommerce(RepositorioJSON(arquivo))

    if "P1" not in sistema.produtos:
        sistema.cadastrar_produto(Produto("P1", "Notebook", 3500, 3))
    if "ana@exemplo.com" not in sistema.clientes:
        sistema.cadastrar_cliente(
            Cliente(
                "Ana",
                "ana@exemplo.com",
                Endereco("Brasilia", "70000-000", "local"),
            )
        )

    cliente = sistema.clientes["ana@exemplo.com"]
    produto = sistema.produtos["P1"]
    if not cliente.carrinho.itens:
        cliente.carrinho.adicionar(produto, 1)
        pedido = sistema.gerar_pedido(cliente.email, PagamentoPix())
        print(f"Pedido {pedido.numero}. Total: R$ {pedido.valor_total:.2f}")

    sistema.salvar()
    print("Dados salvos; na proxima execucao serao carregados automaticamente.")
