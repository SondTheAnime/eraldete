import json
import os
from typing import Dict, Any

class StorageManager:
    """Gerenciador de armazenamento para salvar e carregar dados do JSON"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.directory = os.path.dirname(file_path)

    def _ensure_directory_exists(self):
        """Garante que o diretório do arquivo existe"""
        os.makedirs(self.directory, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        """Carrega os dados do arquivo JSON"""
        self._ensure_directory_exists()
        
        if not os.path.exists(self.file_path):
            return {}
            
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def save(self, data: Dict[str, Any]):
        """Salva os dados no arquivo JSON"""
        self._ensure_directory_exists()
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4) 