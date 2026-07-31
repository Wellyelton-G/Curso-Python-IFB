"""Questao 17: filmes e series tratados por uma interface comum."""


class Conteudo:
    def __init__(self, titulo, genero, duracao):
        self.titulo = titulo
        self.genero = genero
        self.duracao = duracao

    def exibir_detalhes(self):
        # A classe-base define a operacao; as subclasses definem o resultado.
        raise NotImplementedError


class Filme(Conteudo):
    def __init__(self, titulo, genero, duracao, diretor):
        super().__init__(titulo, genero, duracao)
        self.diretor = diretor

    def exibir_detalhes(self):
        return f"Filme: {self.titulo} | {self.genero} | {self.duracao} min | Diretor: {self.diretor}"


class Serie(Conteudo):
    def __init__(self, titulo, genero, duracao, temporadas, episodios):
        super().__init__(titulo, genero, duracao)
        self.quantidade_temporadas = temporadas
        self.quantidade_episodios = episodios

    def exibir_detalhes(self):
        return (
            f"Série: {self.titulo} | {self.genero} | {self.quantidade_temporadas} temporada(s) | "
            f"{self.quantidade_episodios} episódio(s)"
        )


if __name__ == "__main__":
    catalogo = [
        Filme("Interestelar", "Ficção científica", 169, "Christopher Nolan"),
        Serie("Exemplo de Série", "Drama", 50, 3, 24)
    ]

    for conteudo in catalogo:
        # Polimorfismo: nao precisamos testar se e Filme ou Serie.
        print(conteudo.exibir_detalhes())
