import discord
from discord.ext import commands
from discord import app_commands
from typing import Dict, Any, List, Optional
import json
import os

from utils.storage import StorageManager
from config.settings import FICHAS_FILE, TITULOS_FILE, UserIDs

class TitleRepository:
    """Repositório para gerenciamento de títulos"""
    def __init__(self, file_path: str = TITULOS_FILE):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Garante que o arquivo de títulos existe"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({"titulos": []}, f, ensure_ascii=False, indent=4)

    def get_all_titles(self) -> List[str]:
        """Carrega a lista de títulos disponíveis"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("titulos", [])
        except Exception as e:
            print(f"Erro ao carregar títulos: {e}")
            return []

    def save_titles(self, titles: List[str]) -> bool:
        """Salva a lista de títulos"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({"titulos": titles}, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar títulos: {e}")
            return False

class CharacterTitleManager:
    """Gerenciador de títulos de personagens"""
    def __init__(self):
        self.storage = StorageManager(FICHAS_FILE)

    def get_character_titles(self, character_name: str) -> Optional[List[str]]:
        """Obtém os títulos de um personagem específico"""
        fichas = self.storage.load()
        for user_fichas in fichas.values():
            if character_name.lower() in user_fichas:
                personagem = user_fichas[character_name.lower()]
                return personagem.get("titulos", [])
        return None

    def add_title_to_character(self, character_name: str, title: str) -> bool:
        """Adiciona um título a um personagem"""
        fichas = self.storage.load()
        for user_fichas in fichas.values():
            if character_name.lower() in user_fichas:
                personagem = user_fichas[character_name.lower()]
                if "titulos" not in personagem:
                    personagem["titulos"] = []
                if title not in personagem["titulos"]:
                    personagem["titulos"].append(title)
                    self.storage.save(fichas)
                return True
        return False

    def remove_title_from_character(self, character_name: str, title: str) -> bool:
        """Remove um título de um personagem"""
        fichas = self.storage.load()
        for user_fichas in fichas.values():
            if character_name.lower() in user_fichas:
                personagem = user_fichas[character_name.lower()]
                if "titulos" in personagem and title in personagem["titulos"]:
                    personagem["titulos"].remove(title)
                    self.storage.save(fichas)
                    return True
        return False

class TitleManagement(commands.Cog):
    """Cog para gerenciamento de títulos"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.title_repository = TitleRepository()
        self.character_title_manager = CharacterTitleManager()

    def _get_character_choices(self, interaction: discord.Interaction) -> List[app_commands.Choice[str]]:
        """Retorna a lista de personagens disponíveis para choices"""
        fichas = self.character_title_manager.storage.load()
        choices = []
        
        # Se for mestre, mostra todos os personagens
        if interaction.user.id in UserIDs.MESTRES:
            for user_fichas in fichas.values():
                for nome_ficha, ficha_data in user_fichas.items():
                    choices.append(
                        app_commands.Choice(
                            name=f"{ficha_data['nome']} (Nível {ficha_data['nivel']} {ficha_data['classe']})",
                            value=nome_ficha
                        )
                    )
        else:
            # Se não for mestre, mostra apenas seus personagens
            user_id = str(interaction.user.id)
            if user_id in fichas:
                for nome_ficha, ficha_data in fichas[user_id].items():
                    choices.append(
                        app_commands.Choice(
                            name=f"{ficha_data['nome']} (Nível {ficha_data['nivel']} {ficha_data['classe']})",
                            value=nome_ficha
                        )
                    )
        
        return choices

    @app_commands.command(name="criartitulo", description="Cria um novo título para ser usado (apenas mestres)")
    # @app_commands.default_permissions(administrator=True)
    async def criar_titulo(self, interaction: discord.Interaction, titulo: str):
        """Cria um novo título no sistema"""
        # Verifica se é um mestre
        if interaction.user.id not in UserIDs.MESTRES:
            await interaction.response.send_message(
                "Você não tem permissão para criar títulos!",
                ephemeral=True
            )
            return
        
        # Carrega títulos existentes
        titulos = self.title_repository.get_all_titles()
        
        # Verifica se o título já existe
        if titulo in titulos:
            await interaction.response.send_message(
                f"O título '{titulo}' já existe!",
                ephemeral=True
            )
            return
        
        # Adiciona o novo título
        titulos.append(titulo)
        if self.title_repository.save_titles(titulos):
            await interaction.response.send_message(
                f"✨ Título '{titulo}' criado com sucesso!",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Erro ao criar título. Por favor, tente novamente.",
                ephemeral=True
            )

    @app_commands.command(name="removertitulocriado", description="Remove um título da lista de títulos disponíveis (apenas mestres)")
    # @app_commands.default_permissions(administrator=True)
    async def remover_titulo_criado(self, interaction: discord.Interaction, titulo: str):
        """Remove um título do sistema"""
        # Verifica se é um mestre
        if interaction.user.id not in UserIDs.MESTRES:
            await interaction.response.send_message(
                "Você não tem permissão para remover títulos!",
                ephemeral=True
            )
            return
        
        # Carrega títulos existentes
        titulos = self.title_repository.get_all_titles()
        
        # Verifica se o título existe
        if titulo not in titulos:
            await interaction.response.send_message(
                f"O título '{titulo}' não existe!",
                ephemeral=True
            )
            return
        
        # Remove o título
        titulos.remove(titulo)
        if self.title_repository.save_titles(titulos):
            await interaction.response.send_message(
                f"✨ Título '{titulo}' removido com sucesso!",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Erro ao remover título. Por favor, tente novamente.",
                ephemeral=True
            )

    @app_commands.command(name="listatitulos", description="Lista todos os títulos disponíveis")
    async def listar_titulos(self, interaction: discord.Interaction):
        """Lista todos os títulos disponíveis no sistema"""
        # Carrega títulos existentes
        titulos = self.title_repository.get_all_titles()
        
        if not titulos:
            await interaction.response.send_message(
                "Não há títulos disponíveis!",
                ephemeral=True
            )
            return
        
        # Cria embed para mostrar os títulos
        embed = discord.Embed(
            title="𝐓𝐢́𝐭𝐮𝐥𝐨𝐬 𝐃𝐢𝐬𝐩𝐨𝐧𝐢́𝐯𝐞𝐢𝐬",
            color=discord.Color.dark_purple()
        )
        
        # Adiciona os títulos ao embed
        embed.add_field(
            name="Lista de Títulos",
            value="\n".join(f"• {titulo}" for titulo in titulos),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="adicionartitulo", description="Adiciona um título a um personagem (apenas mestres)")
    async def adicionar_titulo(
        self,
        interaction: discord.Interaction,
        nome_personagem: str,
        titulo: str
    ):
        """Adiciona um título a um personagem"""
        if interaction.user.id not in UserIDs.MESTRES:
            await interaction.response.send_message(
                "Você não tem permissão para adicionar títulos!",
                ephemeral=True
            )
            return

        if self.character_title_manager.add_title_to_character(nome_personagem, titulo):
            await interaction.response.send_message(
                f"✨ Título '{titulo}' adicionado ao personagem '{nome_personagem}'!"
            )
        else:
            await interaction.response.send_message(
                f"❌ Erro ao adicionar título. Personagem '{nome_personagem}' não encontrado.",
                ephemeral=True
            )

    @app_commands.command(name="removertitulo", description="Remove um título de um personagem (apenas mestres)")
    async def remover_titulo(
        self,
        interaction: discord.Interaction,
        nome_personagem: str,
        titulo: str
    ):
        """Remove um título de um personagem"""
        if interaction.user.id not in UserIDs.MESTRES:
            await interaction.response.send_message(
                "Você não tem permissão para remover títulos!",
                ephemeral=True
            )
            return

        if self.character_title_manager.remove_title_from_character(nome_personagem, titulo):
            await interaction.response.send_message(
                f"✨ Título '{titulo}' removido do personagem '{nome_personagem}'!"
            )
        else:
            await interaction.response.send_message(
                f"❌ Erro ao remover título. Verifique se o personagem existe e possui o título.",
                ephemeral=True
            )

    # Autocomplete para os comandos
    @adicionar_titulo.autocomplete('nome_personagem')
    async def autocomplete_personagem_adicionar(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        """Autocomplete para nomes de personagens no comando de adicionar título"""
        return self._get_character_choices(interaction)

    @adicionar_titulo.autocomplete('titulo')
    async def autocomplete_titulo_adicionar(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        """Autocomplete para títulos disponíveis no comando de adicionar título"""
        titulos = self.title_repository.get_all_titles()
        return [
            app_commands.Choice(name=titulo, value=titulo)
            for titulo in titulos
            if current.lower() in titulo.lower()
        ][:25]

    @remover_titulo.autocomplete('nome_personagem')
    async def autocomplete_personagem_remover(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        """Autocomplete para nomes de personagens no comando de remover título"""
        return self._get_character_choices(interaction)

    @remover_titulo.autocomplete('titulo')
    async def autocomplete_titulo_remover(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        """Autocomplete para títulos no comando de remover título"""
        nome_personagem = interaction.namespace.nome_personagem
        if not nome_personagem:
            return []
        
        titulos = self.character_title_manager.get_character_titles(nome_personagem)
        if not titulos:
            return []
            
        return [
            app_commands.Choice(name=titulo, value=titulo)
            for titulo in titulos
            if current.lower() in titulo.lower()
        ][:25]

    @remover_titulo_criado.autocomplete('titulo')
    async def autocomplete_titulo_remover_criado(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        """Autocomplete para títulos disponíveis no comando de remover título criado"""
        titulos = self.title_repository.get_all_titles()
        return [
            app_commands.Choice(name=titulo, value=titulo)
            for titulo in titulos
            if current.lower() in titulo.lower()
        ][:25]

async def setup(bot: commands.Bot):
    await bot.add_cog(TitleManagement(bot)) 