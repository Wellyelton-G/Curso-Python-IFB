class ProgressaoAritmetica:
    def __init__(self, a1, r, n):
        self.a1 = a1  # primeiro termo
        self.r = r    # razão
        self.n = n    # número de termos

    def calcular_termo(self, k):
        """
        Retorna o k-ésimo termo da PA.
        Fórmula: an = a1 + r * (n - 1)
        """
        return self.a1 + self.r * (k - 1)

    def listar_termos(self):
        """
        Gera uma lista com todos os termos da PA.
        """
        termos = []
        for i in range(1, self.n + 1):
            termos.append(self.calcular_termo(i))
        return termos

    def soma(self):
        """
        Retorna a soma de todos os termos da PA.
        Fórmula: S = n * (a1 + an) / 2
        """
        an = self.calcular_termo(self.n)
        return self.n * (self.a1 + an) / 2


# Programa Principal
if __name__ == "__main__":
    print("=== PROGRESSÃO ARITMÉTICA ===")
    a1 = float(input("Digite o primeiro termo (a1): "))
    r = float(input("Digite a razão (r): "))
    n = int(input("Digite o número de termos (n): "))

    pa = ProgressaoAritmetica(a1, r, n)

    # Listando os termos
    termos = pa.listar_termos()
    print("\nTermos da Progressão Aritmética:")
    print(termos)

    # Mostrando a soma
    print(f"\nSoma dos {n} termos: {pa.soma()}")