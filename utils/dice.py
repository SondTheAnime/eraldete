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