from pathlib import Path
import json
import os
import tempfile


class RepositorioAcademico:
    def __init__(self, arquivo="dados_academicos.json"):
        self.arquivo = Path(arquivo)

    def salvar(self, dados):
        # A gravação atômica reduz o risco de corrupção do arquivo.
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", delete=False, dir=self.arquivo.parent or "."
        ) as temp:
            json.dump(dados, temp, ensure_ascii=False, indent=2)
            temp.flush()
            os.fsync(temp.fileno())
            nome_temp = temp.name
        os.replace(nome_temp, self.arquivo)

    def carregar(self):
        if not self.arquivo.exists():
            return {}
        try:
            return json.loads(self.arquivo.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            print("Arquivo inexistente ou corrompido. O sistema iniciará sem dados.")
            return {}
