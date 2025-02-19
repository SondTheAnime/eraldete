from typing import List, Tuple, Dict
import random
import re

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

def parse_dice_notation(notation: str) -> Tuple[int, int, int]:
    """
    Analisa a notação de dados (exemplo: 2d20+5)
    
    Args:
        notation: String com a notação de dados
        
    Returns:
        Tupla com (quantidade_dados, faces, modificador)
    """
    pattern = r'^(\d+)?d(\d+)([+-]\d+)?$'
    match = re.match(pattern, notation.lower().replace(' ', ''))
    
    if not match:
        raise ValueError("Notação de dados inválida")
    
    quantidade = int(match.group(1)) if match.group(1) else 1
    faces = int(match.group(2))
    modificador = int(match.group(3)) if match.group(3) else 0
    
    if quantidade > 100:
        raise ValueError("Máximo de 100 dados permitido")
    if faces > 1000:
        raise ValueError("Máximo de 1000 faces permitido")
        
    return quantidade, faces, modificador

def parse_multiple_dice_notation(notation: str) -> List[Tuple[int, int, int]]:
    """
    Analisa múltiplas notações de dados separadas por vírgula ou mais
    
    Args:
        notation: String com as notações de dados (exemplo: 2d20+5,1d6 ou 1d20+1d6)
        
    Returns:
        Lista de tuplas com (quantidade_dados, faces, modificador)
    """
    # Primeiro, procura por dados (padrão XdY)
    dice_pattern = r'\d*d\d+'
    dice_matches = re.finditer(dice_pattern, notation)
    
    # Extrai as posições dos dados encontrados
    dados = []
    last_end = 0
    modificador_total = 0
    
    for match in dice_matches:
        start, end = match.span()
        
        # Verifica se há um modificador numérico entre o último dado e este
        if last_end > 0:
            mod_str = notation[last_end:start].strip('+ ,')
            if mod_str and mod_str.isdigit():
                modificador_total += int(mod_str)
        
        dados.append(match.group())
        last_end = end
    
    # Verifica se há um modificador final
    if last_end < len(notation):
        mod_str = notation[last_end:].strip('+ ,')
        if mod_str and mod_str.replace('-', '').isdigit():
            modificador_total += int(mod_str)
    
    if not dados:
        raise ValueError("Notação de dados inválida")
    
    if len(dados) > 2:
        raise ValueError("Máximo de 2 tipos de dados permitidos")
    
    # Processa cada dado encontrado
    resultados = []
    for dado in dados:
        quantidade, faces = map(lambda x: int(x) if x else 1, re.match(r'(\d*)d(\d+)', dado).groups())
        resultados.append((quantidade, faces, 0))  # Modificador individual zerado
    
    # Adiciona o modificador total ao último dado
    if modificador_total != 0:
        last_qtd, last_faces, _ = resultados[-1]
        resultados[-1] = (last_qtd, last_faces, modificador_total)
    
    return resultados

def rolar_dados(notation: str) -> Dict:
    """
    Rola os dados conforme a notação fornecida
    
    Args:
        notation: String com a notação de dados (exemplo: 2d20+5,1d6 ou 1d20+1d6)
        
    Returns:
        Dicionário com os resultados da rolagem
    """
    try:
        notacoes = parse_multiple_dice_notation(notation)
        resultados_totais = []
        criticos_totais = []
        modificador_total = 0
        
        for i, (quantidade, faces, modificador) in enumerate(notacoes):
            # Rola os dados
            resultados = [random.randint(1, faces) for _ in range(quantidade)]
            resultados_totais.append(resultados)
            modificador_total += modificador
            
            # Verifica críticos (apenas para d20)
            if faces == 20:
                criticos = [
                    (i, j + 1) for j, resultado in enumerate(resultados)
                    if resultado == 20 or resultado == 1
                ]
                criticos_totais.extend(criticos)
        
        return {
            "notacao": notation,
            "resultados_grupos": resultados_totais,
            "modificador": modificador_total,
            "total": sum(sum(grupo) for grupo in resultados_totais) + modificador_total,
            "criticos": criticos_totais
        }
    except Exception as e:
        # Adiciona mais contexto ao erro
        raise ValueError(f"Erro ao processar rolagem '{notation}': {str(e)}") 