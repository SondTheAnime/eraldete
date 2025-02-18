from typing import List
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do bot
TOKEN = os.getenv('DISCORD_TOKEN')  # Token do bot do Discord
COMMAND_PREFIX = "!"

# Caminhos de arquivo
FICHAS_FILE = 'data/fichas.json'
TITULOS_FILE = 'data/titulos.json'

# IDs de usuários especiais
class UserIDs:
    MESTRES: List[int] = [670255264112312322, 357209498286424064]
    LINDO: int = 357209498286424064
    FEIO: int = 670255264112312322 