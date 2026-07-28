class Livro:
    def __init__(self, titulo, autor):
        self.titulo = titulo
        self.autor = autor
        self.disponivel = True

    def emprestar(self):
        if not self.disponivel:
            print("O livro já está emprestado.")
            return
        self.disponivel = False
        print("Empréstimo realizado.")

    def devolver(self):
        if self.disponivel:
            print("O livro já está disponível.")
            return
        self.disponivel = True
        print("Devolução realizada.")

    def exibir_status(self):
        status = "disponível" if self.disponivel else "emprestado"
        print(f"{self.titulo}, de {self.autor}: {status}.")


if __name__ == "__main__":
    livro = Livro("Dom Casmurro", "Machado de Assis")
    livro.exibir_status()
    livro.emprestar()
    livro.emprestar()
    livro.devolver()
