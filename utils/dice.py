def calcular_dado(nivel_atributo: int) -> str:
    """
    Calcula o dado baseado no nível do atributo
    
    Args:
        nivel_atributo: Nível do atributo
        
    Returns:
        String formatada com o dado e bônus (se houver)
    """
    # Calcula o dado base (nível x 4)
    dado = f"d{nivel_atributo * 4}"
    
    # Calcula o bônus (+1 a cada 10 pontos)
    bonus = nivel_atributo // 10
    
    # Retorna a string formatada
    if bonus > 0:
        return f"{dado}+{bonus}"
    return dado

import random
import re
from typing import Tuple, List, Dict

def parse_dice_notation(notation: str) -> Tuple[int, int, int]:
    """
    Analisa a notação de dados (exemplo: 2d20+5)
    
    Args:
        notation: String com a notação de dados
        
    Returns:
        Tupla com (quantidade_dados, faces, modificador)
    """
    # Padrão regex para notação de dados: XdY+Z ou XdY-Z
    pattern = r'^(\d+)?d(\d+)([+-]\d+)?$'
    match = re.match(pattern, notation.lower().replace(' ', ''))
    
    if not match:
        raise ValueError("Notação de dados inválida")
    
    quantidade = int(match.group(1)) if match.group(1) else 1
    faces = int(match.group(2))
    modificador = int(match.group(3)) if match.group(3) else 0
    
    # Limites para evitar abuso
    if quantidade > 100:
        raise ValueError("Máximo de 100 dados permitido")
    if faces > 1000:
        raise ValueError("Máximo de 1000 faces permitido")
        
    return quantidade, faces, modificador

def rolar_dados(notation: str) -> Dict:
    """
    Rola os dados conforme a notação fornecida
    
    Args:
        notation: String com a notação de dados (exemplo: 2d20+5)
        
    Returns:
        Dicionário com os resultados da rolagem
    """
    quantidade, faces, modificador = parse_dice_notation(notation)
    
    # Rola os dados
    resultados = [random.randint(1, faces) for _ in range(quantidade)]
    
    # Calcula o total
    subtotal = sum(resultados)
    total = subtotal + modificador
    
    # Verifica críticos (apenas para d20)
    criticos = []
    if faces == 20:
        criticos = [
            i + 1 for i, resultado in enumerate(resultados)
            if resultado == 20 or resultado == 1
        ]
    
    return {
        "notacao": notation,
        "dados": quantidade,
        "faces": faces,
        "modificador": modificador,
        "resultados": resultados,
        "subtotal": subtotal,
        "total": total,
        "criticos": criticos
    } 