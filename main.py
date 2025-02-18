import discord
from discord.ext import commands
from config.settings import TOKEN, COMMAND_PREFIX, UserIDs

# Configuração do bot com todos os intents necessários
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Comando para sincronizar os comandos slash
@bot.tree.command(name="sync", description="Sincroniza os comandos do bot (apenas mestres)")
async def sync(interaction: discord.Interaction):
    # Verifica se é um mestre
    if interaction.user.id not in UserIDs.MESTRES:
        await interaction.response.send_message(
            "Você não tem permissão para sincronizar os comandos!",
            ephemeral=True
        )
        return
    
    # Tenta sincronizar os comandos
    try:
        # Sincroniza globalmente
        synced = await bot.tree.sync()
        
        # Envia mensagem de sucesso
        await interaction.response.send_message(
            f"✅ Sincronizados {len(synced)} comandos globalmente!",
            ephemeral=True
        )
        print(f'Comandos sincronizados por {interaction.user.name} (ID: {interaction.user.id})')
        
    except Exception as e:
        # Em caso de erro
        await interaction.response.send_message(
            f"❌ Erro ao sincronizar comandos: {str(e)}",
            ephemeral=True
        )
        print(f'Erro ao sincronizar comandos: {e}')

# Evento executado quando o bot está pronto
@bot.event
async def on_ready():
    print('='*50)
    print(f'Iniciando {bot.user.name}...')
    print('='*50)
    
    # Carrega as extensões do bot
    print('\n📂 Carregando extensões...')
    try:
        await bot.load_extension('cogs.character_management')
        print('✅ Extensão character_management carregada')
        await bot.load_extension('cogs.fun_commands')
        print('✅ Extensão fun_commands carregada')
        await bot.load_extension('cogs.equipment_management')
        print('✅ Extensão equipment_management carregada')
        await bot.load_extension('cogs.title_management')
        print('✅ Extensão title_management carregada')
    except Exception as e:
        print(f'❌ Erro ao carregar extensões: {e}')
    
    # Sincroniza os comandos com o Discord
    print('\n🔄 Sincronizando comandos...')
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} comandos sincronizados:')
        for cmd in synced:
            print(f'  • /{cmd.name}: {cmd.description}')
    except Exception as e:
        print(f'❌ Erro ao sincronizar comandos: {e}')
    
    # Lista todos os servidores conectados
    print('\n🌐 Servidores conectados:')
    for guild in bot.guilds:
        print(f'  • {guild.name}')
        print(f'    - ID: {guild.id}')
        print(f'    - Membros: {guild.member_count}')
        print(f'    - Dono: {guild.owner.name} (ID: {guild.owner.id})')
    
    print('\n'+'='*50)
    print(f'✨ {bot.user.name} está online e pronto!')
    print('='*50)

# Evento executado quando o bot entra em um novo servidor
@bot.event
async def on_guild_join(guild):
    print('\n'+'='*50)
    print(f'🎉 Bot entrou em um novo servidor!')
    print(f'  • Nome: {guild.name}')
    print(f'  • ID: {guild.id}')
    print(f'  • Membros: {guild.member_count}')
    print(f'  • Dono: {guild.owner.name} (ID: {guild.owner.id})')
    
    # Sincroniza os comandos com o novo servidor
    print('\n🔄 Sincronizando comandos com o novo servidor...')
    try:
        await bot.tree.sync(guild=guild)
        print('✅ Comandos sincronizados com sucesso!')
    except Exception as e:
        print(f'❌ Erro ao sincronizar comandos: {e}')
    print('='*50)

# Inicia o bot
bot.run(TOKEN)
