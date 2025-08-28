class Criptografo:
    def __init__(self, frase):
        self.frase = frase

    def criptografar(self):
        # Dicionário com as trocas: vogal -> número
        mapa = {
            "a": "4",
            "e": "3",
            "i": "1",
            "o": "0",
            "u": "8"
        }

        texto_final = ""
        for letra in self.frase:
            if letra.lower() in mapa:   # Se for vogal
                texto_final += mapa[letra.lower()]
            else:
                texto_final += letra    # Se não for vogal, mantém igual
        return texto_final


# Programa principal
if __name__ == "__main__":
    frase = input("Digite uma frase: ")
    cript = Criptografo(frase)

    print("\n=== RESULTADO ===")
    print("Frase original:   ", frase)
    print("Frase criptografada:", cript.criptografar())
