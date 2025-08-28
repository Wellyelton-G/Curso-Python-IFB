class AnalisadorDeString:
    def __init__(self, texto):
        self.texto = texto
    #len(...) → é uma função pronta do Python que retorna o comprimento (tamanho) de algo. 
    #No caso, len(self.texto) retorna o número de caracteres na string armazenada em self.texto.
    #Se for uma string, ela retorna o número de caracteres (incluindo espaços, letras, números, pontuação, etc.)
    def contar_caracteres(self):
        return len(self.texto)
   
    # .uper é um método de string que converte todos os caracteres para maiúsculas
    def maiusculas(self):
        return self.texto.upper()
    # .lower é um método de string que converte todos os caracteres para minúsculas.
    def minusculas(self):
        return self.texto.lower()

    def contar_vogais(self):
        vogais = "aeiou"
        contador = 0
        for letra in self.texto.lower():  # converte para minúsculo
            if letra in vogais:
                contador += 1
        return contador

    def contem_ifb(self):
        return "ifb" in self.texto.lower()


# Programa Principal
if __name__ == "__main__":
    texto = input("Digite uma string: ")

    analisador = AnalisadorDeString(texto)

    print("\n=== RESULTADOS ===")
    print(f"Número de caracteres: {analisador.contar_caracteres()}")
    print(f"Texto em maiúsculas: {analisador.maiusculas()}")
    print(f"Texto em minúsculas: {analisador.minusculas()}")
    print(f"Número de vogais: {analisador.contar_vogais()}")

    if analisador.contem_ifb():
        print("A substring 'IFB' aparece no texto.")
    else:
        print("A substring 'IFB' NÃO aparece no texto.")
