import discord
from discord.ext import commands
from discord import app_commands
from typing import Dict, Any, List

from models.character import Character
from utils.storage import StorageManager
from utils.dice import calcular_dado
from config.settings import FICHAS_FILE, UserIDs

class CharacterManagement(commands.Cog):
    """Cog responsável por gerenciar os comandos relacionados a personagens"""

    def __init__(self, bot):
        self.bot = bot
        self.storage = StorageManager(FICHAS_FILE)

    async def autocomplete_character_names(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        """Função de autocompletar para nomes de personagens"""
        # Carrega as fichas
        fichas = self.storage.load()
        user_id = str(interaction.user.id)
        
        # Se o usuário não tem fichas, retorna lista vazia
        if user_id not in fichas:
            return []
        
        # Filtra os nomes que começam com o texto atual
        matches = []
        for nome in fichas[user_id].keys():
            if nome.startswith(current.lower()):
                matches.append(app_commands.Choice(name=nome, value=nome))
        
        return matches[:25]  # Limite de 25 opções

    @app_commands.command(name="criarficha", description="Cria uma ficha de personagem personalizada")
    async def criar_ficha(
        self,
        interaction: discord.Interaction,
        nome: str,
        nivel: int,
        classe: str,
        forca: int,
        agilidade: int,
        sapiencia: int,
        intelecto: int,
        vigor: int,
        coragem: int
    ):
        # Cria o personagem usando o modelo
        character = Character(
            nome=nome,
            nivel=nivel,
            classe=classe,
            atributos={
                "forca": forca,
                "agilidade": agilidade,
                "sapiencia": sapiencia,
                "intelecto": intelecto,
                "vigor": vigor,
                "coragem": coragem
            }
        )

        # Carrega fichas existentes
        fichas = self.storage.load()
        
        # Salva a ficha do usuário
        user_id = str(interaction.user.id)
        if user_id not in fichas:
            fichas[user_id] = {}
        fichas[user_id][nome.lower()] = character.to_dict()
        
        # Salva as fichas atualizadas
        self.storage.save(fichas)

        # Cria o embed para exibir a ficha
        await self._send_character_embed(interaction, character)

    @app_commands.command(name="verficha", description="Mostra uma ficha de personagem salva")
    async def ver_ficha(self, interaction: discord.Interaction):
        # Verifica se é um mestre
        is_mestre = interaction.user.id in UserIDs.MESTRES
        
        # Carrega as fichas
        fichas = self.storage.load()
        
        # Prepara as opções do menu
        options = await self._prepare_character_options(interaction, fichas, is_mestre)
        
        if not options:
            await interaction.response.send_message(
                "Não há fichas disponíveis!" if is_mestre else "Você não tem nenhuma ficha criada!",
                ephemeral=True
            )
            return

        # Cria o menu de seleção
        view = await self._create_character_select_view(interaction, options, fichas, is_mestre)
        await interaction.response.send_message("Selecione um personagem:", view=view)

    async def _prepare_character_options(
        self,
        interaction: discord.Interaction,
        fichas: Dict[str, Any],
        is_mestre: bool
    ) -> list:
        """Prepara as opções do menu de seleção de personagem"""
        options = []
        
        if is_mestre:
            for user_id, user_fichas in fichas.items():
                for nome_ficha, ficha_data in user_fichas.items():
                    try:
                        user = await self.bot.fetch_user(int(user_id))
                        user_name = user.name
                    except:
                        user_name = f"ID: {user_id}"
                    
                    options.append(
                        discord.SelectOption(
                            label=ficha_data["nome"],
                            value=f"{user_id}:{nome_ficha}",
                            description=f"Nível {ficha_data['nivel']} - {ficha_data['classe']} (Dono: {user_name})"
                        )
                    )
        else:
            user_id = str(interaction.user.id)
            if user_id in fichas:
                options = [
                    discord.SelectOption(
                        label=ficha_data["nome"],
                        value=f"{user_id}:{nome_ficha}",
                        description=f"Nível {ficha_data['nivel']} - {ficha_data['classe']}"
                    )
                    for nome_ficha, ficha_data in fichas[user_id].items()
                ]
        
        return options

    async def _create_character_select_view(
        self,
        interaction: discord.Interaction,
        options: list,
        fichas: Dict[str, Any],
        is_mestre: bool
    ) -> discord.ui.View:
        """Cria a view com o menu de seleção de personagem"""
        select = discord.ui.Select(
            placeholder="Escolha um personagem para ver a ficha",
            options=options,
            min_values=1,
            max_values=1
        )

        view = discord.ui.View()
        view.add_item(select)

        async def select_callback(interaction: discord.Interaction):
            user_id, nome_ficha = select.values[0].split(":")
            ficha_data = fichas[user_id][nome_ficha]
            character = Character.from_dict(ficha_data)
            
            embed = await self._create_character_embed(character, is_mestre, user_id)
            await interaction.response.send_message(embed=embed)

        select.callback = select_callback
        return view

    async def _create_character_embed(
        self,
        character: Character,
        is_mestre: bool,
        user_id: str = None
    ) -> discord.Embed:
        """Cria o embed para exibir a ficha do personagem"""
        embed = discord.Embed(
            title="𝐅𝐢𝐜𝐡𝐚 𝐝𝐞 𝐏𝐞𝐫𝐬𝐨𝐧𝐚𝐠𝐞𝐦",
            color=discord.Color.dark_purple()
        )

        # Se for mestre, adiciona informação do dono da ficha
        if is_mestre and user_id:
            try:
                user = await self.bot.fetch_user(int(user_id))
                dono_ficha = f"Dono da ficha: {user.name} (ID: {user_id})"
            except:
                dono_ficha = f"Dono da ficha: ID {user_id}"
            embed.set_footer(text=dono_ficha)

        # Informações básicas
        embed.add_field(
            name="𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐜̧𝐨̃𝐞𝐬 𝐁𝐚́𝐬𝐢𝐜𝐚𝐬",
            value=(
                f"**𝐍𝐨𝐦𝐞:** {character.nome}\n"
                f"**𝐧𝐢́𝐯𝐞𝐥:** {character.nivel}\n"
                f"**𝐂𝐥𝐚𝐬𝐬𝐞:** {character.classe}"
            ),
            inline=False
        )

        # Títulos
        if character.titulos:
            embed.add_field(
                name="𝐓𝐢́𝐭𝐮𝐥𝐨𝐬",
                value="\n".join(f"• {titulo}" for titulo in character.titulos),
                inline=False
            )

        # Status
        embed.add_field(
            name="𝐒𝐭𝐚𝐭𝐮𝐬",
            value=(
                f"**𝐕𝐢𝐝𝐚:** {character.vida_atual}/{character.vida_total}\n"
                f"**𝐈𝐧𝐢𝐜𝐢𝐚𝐭𝐢𝐯𝐚:** d20+{character.atributos['agilidade']}"
            ),
            inline=False
        )

        # Atributos
        atrib_text = []
        for nome, valor in character.atributos.items():
            dado = calcular_dado(valor)
            atrib_text.append(f"**{nome.capitalize()}:** ({valor}) {dado}")
        
        embed.add_field(
            name="𝐀𝐭𝐫𝐢𝐛𝐮𝐭𝐨𝐬",
            value="\n".join(atrib_text),
            inline=False
        )

        # Outros campos
        for campo, lista in [
            ("𝐏𝐞𝐫𝐢́𝐜𝐢𝐚𝐬 𝐍𝐨𝐭𝐚́𝐯𝐞𝐢𝐬", character.pericias),
            ("𝐂𝐚𝐩𝐚𝐜𝐢𝐝𝐚𝐝𝐞𝐬", character.capacidades),
            ("𝐄𝐪𝐮𝐢𝐩𝐚𝐦𝐞𝐧𝐭𝐨𝐬 𝐍𝐨𝐭𝐚́𝐯𝐞𝐢𝐬", character.equipamentos)
        ]:
            valor = "\n".join(f"• {item}" for item in lista) if lista else "• Nenhum registro"
            embed.add_field(name=campo, value=valor, inline=False)

        return embed

    async def _send_character_embed(self, interaction: discord.Interaction, character: Character):
        """Envia o embed do personagem como resposta à interação"""
        embed = await self._create_character_embed(character, False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CharacterManagement(bot)) 