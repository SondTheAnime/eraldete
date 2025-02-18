# Classe que representa a estrutura de dados de um personagem
class Character:
    def __init__(self, nome: str, nivel: int, classe: str, atributos: dict):
        self.nome = nome
        self.nivel = nivel
        self.classe = classe
        self.atributos = atributos
        self.vida_total = self._calcular_vida()
        self.vida_atual = self.vida_total
        self.pericias = []
        self.capacidades = []
        self.equipamentos = []
        self.titulos = []

    def _calcular_vida(self) -> int:
        """Calcula a vida total do personagem baseado nos atributos"""
        vida_base = self.atributos['forca'] * (self.atributos['vigor'] * 2)
        bonus_nivel = int((vida_base * 0.25) * self.nivel)
        return vida_base + bonus_nivel

    def to_dict(self) -> dict:
        """Converte o personagem para um dicionário para salvar no JSON"""
        return {
            "nome": self.nome,
            "nivel": self.nivel,
            "classe": self.classe,
            "atributos": self.atributos,
            "vida_total": self.vida_total,
            "vida_atual": self.vida_atual,
            "pericias": self.pericias,
            "capacidades": self.capacidades,
            "equipamentos": self.equipamentos,
            "titulos": self.titulos
        }

    @staticmethod
    def from_dict(data: dict) -> 'Character':
        """Cria um personagem a partir de um dicionário"""
        char = Character(
            data["nome"],
            data["nivel"],
            data["classe"],
            data["atributos"]
        )
        char.vida_atual = data["vida_atual"]
        char.pericias = data["pericias"]
        char.capacidades = data["capacidades"]
        char.equipamentos = data["equipamentos"]
        char.titulos = data.get("titulos", [])  # Usa get para compatibilidade com fichas antigas
        return char 