import discord
from discord.ext import commands
from discord import app_commands
from config.settings import UserIDs

class FunCommands(commands.Cog):
    """Cog responsável por comandos divertidos e não relacionados ao RPG"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ola", description="Envia uma mensagem de saudação")
    async def ola(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Olá {interaction.user.name} gayzãos!')

    @app_commands.command(name="limpar", description="Limpa um número específico de mensagens")
    async def limpar(self, interaction: discord.Interaction, quantidade: int):
        if interaction.user.guild_permissions.manage_messages:
            await interaction.channel.purge(limit=quantidade)
            await interaction.response.send_message(
                f'{quantidade} mensagens foram apagadas!',
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                'Você não tem permissão para usar este comando!',
                ephemeral=True
            )

    @app_commands.command(name="lindo", description="Mostra quem é o mais lindo do servidor")
    async def lindo(self, interaction: discord.Interaction):
        if interaction.user.id == UserIDs.LINDO:
            await interaction.response.send_message("Você é o mais lindo desse servidor! 😍✨")
        else:
            await interaction.response.send_message(f"Desculpe, mas o mais lindo é o <@{UserIDs.LINDO}>! 👑")

    @app_commands.command(name="feio", description="Mostra quem é o mais feio do servidor")
    async def feio(self, interaction: discord.Interaction):
        if interaction.user.id == UserIDs.FEIO:
            await interaction.response.send_message("Sim, você é o mais feio mesmo! 🤡")
        else:
            await interaction.response.send_message(f"Com certeza o mais feio é o <@{UserIDs.FEIO}>! 🤮")

async def setup(bot):
    await bot.add_cog(FunCommands(bot)) 