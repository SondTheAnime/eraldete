import discord
from discord.ext import commands
from discord import app_commands
from config.settings import UserIDs
from utils.dice import rolar_dados
import re

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

    @app_commands.command(name="rolar", description="Rola dados usando notação padrão (exemplo: 2d20+5,1d6)")
    @app_commands.describe(
        notacao="Notação dos dados (exemplo: 2d20+5,1d6, 1d20,2d8)",
        motivo="Motivo da rolagem (opcional)"
    )
    async def rolar(
        self,
        interaction: discord.Interaction,
        notacao: str,
        motivo: str = None
    ):
        """
        Rola dados usando notação padrão e exibe um resultado estilizado
        """
        try:
            # Remove espaços extras e converte para minúsculas
            notacao = notacao.strip().lower()
            
            # Realiza a rolagem
            resultado = rolar_dados(notacao)
            
            # Cria o embed
            embed = discord.Embed(
                title="🎲 Rolagem de Dados",
                color=discord.Color.blue()
            )
            
            # Adiciona o autor
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url
            )
            
            # Adiciona o motivo se fornecido
            if motivo:
                embed.description = f"**Motivo:** {motivo}"
            
            # Campo com a notação e resultado total
            embed.add_field(
                name="📝 Rolagem",
                value=f"`{resultado['notacao']}` = **{resultado['total']}**",
                inline=False
            )
            
            # Mostra os resultados individuais de cada dado
            resultados_str = []
            notacoes = [n.strip() for n in resultado['notacao'].split(',')]
            
            for grupo_idx, (resultados, notacao) in enumerate(zip(resultado['resultados_grupos'], notacoes)):
                tipo_dado = re.search(r'd\d+', notacao).group()  # Extrai o tipo do dado (d20, d6, etc)
                for valor in resultados:
                    # Adiciona emoji baseado no tipo do dado
                    emoji = "🎯" if tipo_dado == "d20" else "🎲"
                    resultados_str.append(f"{emoji} {tipo_dado}: **{valor}**")
            
            # Adiciona o modificador total no final se houver
            if resultado['modificador']:
                sinal = "+" if resultado['modificador'] > 0 else ""
                resultados_str.append(f"💫 Modificador: {sinal}{resultado['modificador']}")
            
            # Divide em múltiplos campos se necessário (limite de 1024 caracteres por campo)
            resultados_chunks = []
            current_chunk = []
            current_length = 0
            
            for resultado_str in resultados_str:
                if current_length + len(resultado_str) + 1 > 1024:  # +1 para a quebra de linha
                    resultados_chunks.append("\n".join(current_chunk))
                    current_chunk = [resultado_str]
                    current_length = len(resultado_str)
                else:
                    current_chunk.append(resultado_str)
                    current_length += len(resultado_str) + 1
            
            if current_chunk:
                resultados_chunks.append("\n".join(current_chunk))
            
            # Adiciona os campos de resultados
            for i, chunk in enumerate(resultados_chunks, 1):
                embed.add_field(
                    name=f"🎲 Resultados {f'(Parte {i})' if len(resultados_chunks) > 1 else ''}",
                    value=chunk,
                    inline=False
                )
            
            # Adiciona críticos se houver (apenas para d20)
            criticos = []
            if resultado['criticos']:
                for grupo, idx in resultado['criticos']:
                    valor = resultado['resultados_grupos'][grupo][idx - 1]
                    if valor == 20:
                        criticos.append(f"🌟 Sucesso Crítico! (d20: {valor})")
                    elif valor == 1:
                        criticos.append(f"💥 Falha Crítica! (d20: {valor})")
            
            if criticos:
                embed.add_field(
                    name="⚡ Críticos",
                    value="\n".join(criticos),
                    inline=False
                )
            
            # Envia o resultado
            await interaction.response.send_message(embed=embed)
            
        except ValueError as e:
            await interaction.response.send_message(
                f"❌ Erro: {str(e)}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                "❌ Ocorreu um erro ao processar sua rolagem. Verifique a notação e tente novamente.",
                ephemeral=True
            )
            print(f"Erro ao processar rolagem: {e}")

async def setup(bot):
    await bot.add_cog(FunCommands(bot)) 