import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Dict, Any, List
import json
import os
from datetime import datetime
from config.settings import UserIDs

# Interface para equipamentos
class IEquipment:
    def to_dict(self) -> Dict[str, Any]:
        pass

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Equipment':
        pass

# Classe concreta de equipamento
class Equipment(IEquipment):
    def __init__(
        self,
        name: str,
        type: str,
        description: str,
        damage: Optional[str] = None,
        armor: Optional[int] = None,
        weight: Optional[float] = None,
        value: Optional[int] = None,
        properties: Optional[list[str]] = None,
        requirements: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
        created_at: Optional[str] = None
    ):
        self.name = name
        self.type = type
        self.description = description
        self.damage = damage
        self.armor = armor
        self.weight = weight
        self.value = value
        self.properties = properties or []
        self.requirements = requirements or {}
        self.created_by = created_by
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "damage": self.damage,
            "armor": self.armor,
            "weight": self.weight,
            "value": self.value,
            "properties": self.properties,
            "requirements": self.requirements,
            "created_by": self.created_by,
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Equipment':
        return Equipment(**data)

# Gerenciador de persistência de equipamentos
class EquipmentRepository:
    def __init__(self, file_path: str = "data/equipment.json"):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)

    def save_equipment(self, equipment: Equipment) -> bool:
        try:
            equipments = self.get_all_equipment()
            equipments.append(equipment.to_dict())
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(equipments, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar equipamento: {e}")
            return False

    def get_all_equipment(self) -> list[Dict[str, Any]]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao ler equipamentos: {e}")
            return []

    def get_equipment_by_name(self, name: str) -> Optional[Equipment]:
        """Busca um equipamento pelo nome"""
        equipments = self.get_all_equipment()
        for eq in equipments:
            if eq["name"].lower() == name.lower():
                return Equipment.from_dict(eq)
        return None

    def update_equipment(self, name: str, updated_equipment: Equipment) -> bool:
        """Atualiza um equipamento existente"""
        try:
            equipments = self.get_all_equipment()
            for i, eq in enumerate(equipments):
                if eq["name"].lower() == name.lower():
                    equipments[i] = updated_equipment.to_dict()
                    with open(self.file_path, 'w', encoding='utf-8') as f:
                        json.dump(equipments, f, ensure_ascii=False, indent=4)
                    return True
            return False
        except Exception as e:
            print(f"Erro ao atualizar equipamento: {e}")
            return False

    def delete_equipment(self, name: str) -> bool:
        """Exclui um equipamento pelo nome"""
        try:
            equipments = self.get_all_equipment()
            initial_length = len(equipments)
            equipments = [eq for eq in equipments if eq["name"].lower() != name.lower()]
            
            if len(equipments) == initial_length:
                return False
                
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(equipments, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao excluir equipamento: {e}")
            return False

# Cog para gerenciamento de equipamentos
class EquipmentManagement(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.repository = EquipmentRepository()

    # Grupo de comandos de equipamento
    equipment_group = app_commands.Group(
        name="equipamento",
        description="Comandos relacionados a equipamentos"
    )

    @equipment_group.command(
        name="criar",
        description="Cria um novo equipamento no sistema"
    )
    async def create_equipment(
        self,
        interaction: discord.Interaction,
        nome: str,
        tipo: str,
        descricao: str,
        dano: Optional[str] = None,
        armadura: Optional[int] = None,
        peso: Optional[float] = None,
        valor: Optional[int] = None,
        propriedades: Optional[str] = None
    ):
        """
        Cria um novo equipamento com detalhes específicos
        """
        # Criação do embed inicial para feedback visual
        embed = discord.Embed(
            title="🛠️ Criando Novo Equipamento",
            description="Processando informações...",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

        # Processamento das propriedades
        properties_list = (
            [prop.strip() for prop in propriedades.split(',')]
            if propriedades else []
        )

        # Criação do equipamento
        equipment = Equipment(
            name=nome,
            type=tipo,
            description=descricao,
            damage=dano,
            armor=armadura,
            weight=peso,
            value=valor,
            properties=properties_list,
            created_by=str(interaction.user),
        )

        # Salvamento do equipamento
        if self.repository.save_equipment(equipment):
            # Criação do embed de sucesso
            success_embed = discord.Embed(
                title="✨ Equipamento Criado com Sucesso!",
                color=discord.Color.green()
            )
            
            # Campos do equipamento
            success_embed.add_field(
                name="📝 Nome",
                value=equipment.name,
                inline=True
            )
            success_embed.add_field(
                name="🏷️ Tipo",
                value=equipment.type,
                inline=True
            )
            success_embed.add_field(
                name="📖 Descrição",
                value=equipment.description,
                inline=False
            )

            # Campos opcionais
            if equipment.damage:
                success_embed.add_field(
                    name="⚔️ Dano",
                    value=equipment.damage,
                    inline=True
                )
            if equipment.armor:
                success_embed.add_field(
                    name="🛡️ Armadura",
                    value=str(equipment.armor),
                    inline=True
                )
            if equipment.weight:
                success_embed.add_field(
                    name="⚖️ Peso",
                    value=f"{equipment.weight} kg",
                    inline=True
                )
            if equipment.value:
                success_embed.add_field(
                    name="💰 Valor",
                    value=f"{equipment.value} moedas",
                    inline=True
                )
            if equipment.properties:
                success_embed.add_field(
                    name="🔮 Propriedades",
                    value="\n".join(f"• {prop}" for prop in equipment.properties),
                    inline=False
                )

            # Informações adicionais
            success_embed.set_footer(
                text=f"Criado por {equipment.created_by} • {datetime.fromisoformat(equipment.created_at).strftime('%d/%m/%Y %H:%M')}"
            )

            await interaction.edit_original_response(embed=success_embed)
        else:
            error_embed = discord.Embed(
                title="❌ Erro ao Criar Equipamento",
                description="Não foi possível salvar o equipamento. Por favor, tente novamente.",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=error_embed)

    @equipment_group.command(
        name="editar",
        description="Edita um equipamento existente"
    )
    async def edit_equipment(
        self,
        interaction: discord.Interaction,
        nome_atual: str,
        novo_nome: Optional[str] = None,
        tipo: Optional[str] = None,
        descricao: Optional[str] = None,
        dano: Optional[str] = None,
        armadura: Optional[int] = None,
        peso: Optional[float] = None,
        valor: Optional[int] = None,
        propriedades: Optional[str] = None
    ):
        """
        Edita um equipamento existente no sistema
        """
        # Feedback inicial
        embed = discord.Embed(
            title="🔄 Editando Equipamento",
            description="Buscando equipamento...",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

        # Busca o equipamento
        equipment = self.repository.get_equipment_by_name(nome_atual)
        if not equipment:
            error_embed = discord.Embed(
                title="❌ Equipamento Não Encontrado",
                description=f"Não foi encontrado nenhum equipamento com o nome '{nome_atual}'.",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=error_embed)
            return

        # Atualiza apenas os campos fornecidos
        updated_equipment = Equipment(
            name=novo_nome or equipment.name,
            type=tipo or equipment.type,
            description=descricao or equipment.description,
            damage=dano if dano is not None else equipment.damage,
            armor=armadura if armadura is not None else equipment.armor,
            weight=peso if peso is not None else equipment.weight,
            value=valor if valor is not None else equipment.value,
            properties=[prop.strip() for prop in propriedades.split(',')] if propriedades else equipment.properties,
            created_by=equipment.created_by,
            created_at=equipment.created_at
        )

        # Tenta atualizar o equipamento
        if self.repository.update_equipment(nome_atual, updated_equipment):
            # Criação do embed de sucesso
            success_embed = discord.Embed(
                title="✨ Equipamento Atualizado com Sucesso!",
                color=discord.Color.green()
            )
            
            # Campos do equipamento
            success_embed.add_field(
                name="📝 Nome",
                value=updated_equipment.name,
                inline=True
            )
            success_embed.add_field(
                name="🏷️ Tipo",
                value=updated_equipment.type,
                inline=True
            )
            success_embed.add_field(
                name="📖 Descrição",
                value=updated_equipment.description,
                inline=False
            )

            # Campos opcionais
            if updated_equipment.damage:
                success_embed.add_field(
                    name="⚔️ Dano",
                    value=updated_equipment.damage,
                    inline=True
                )
            if updated_equipment.armor:
                success_embed.add_field(
                    name="🛡️ Armadura",
                    value=str(updated_equipment.armor),
                    inline=True
                )
            if updated_equipment.weight:
                success_embed.add_field(
                    name="⚖️ Peso",
                    value=f"{updated_equipment.weight} kg",
                    inline=True
                )
            if updated_equipment.value:
                success_embed.add_field(
                    name="💰 Valor",
                    value=f"{updated_equipment.value} moedas",
                    inline=True
                )
            if updated_equipment.properties:
                success_embed.add_field(
                    name="🔮 Propriedades",
                    value="\n".join(f"• {prop}" for prop in updated_equipment.properties),
                    inline=False
                )

            # Informações adicionais
            success_embed.set_footer(
                text=f"Criado por {updated_equipment.created_by} • Editado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            )

            await interaction.edit_original_response(embed=success_embed)
        else:
            error_embed = discord.Embed(
                title="❌ Erro ao Atualizar Equipamento",
                description="Não foi possível atualizar o equipamento. Por favor, tente novamente.",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=error_embed)

    @equipment_group.command(
        name="excluir",
        description="Exclui um equipamento do sistema"
    )
    async def delete_equipment(
        self,
        interaction: discord.Interaction,
        nome: str
    ):
        """
        Exclui um equipamento do sistema
        """
        # Feedback inicial
        embed = discord.Embed(
            title="🗑️ Excluindo Equipamento",
            description="Processando exclusão...",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

        # Busca o equipamento antes de excluir para mostrar os detalhes
        equipment = self.repository.get_equipment_by_name(nome)
        if not equipment:
            error_embed = discord.Embed(
                title="❌ Equipamento Não Encontrado",
                description=f"Não foi encontrado nenhum equipamento com o nome '{nome}'.",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=error_embed)
            return

        # Tenta excluir o equipamento
        if self.repository.delete_equipment(nome):
            # Criação do embed de sucesso
            success_embed = discord.Embed(
                title="✅ Equipamento Excluído com Sucesso!",
                description=f"O equipamento '{nome}' foi excluído permanentemente.",
                color=discord.Color.green()
            )
            
            # Adiciona os detalhes do equipamento excluído
            success_embed.add_field(
                name="📝 Nome",
                value=equipment.name,
                inline=True
            )
            success_embed.add_field(
                name="🏷️ Tipo",
                value=equipment.type,
                inline=True
            )
            
            success_embed.set_footer(
                text=f"Excluído em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            )

            await interaction.edit_original_response(embed=success_embed)
        else:
            error_embed = discord.Embed(
                title="❌ Erro ao Excluir Equipamento",
                description="Não foi possível excluir o equipamento. Por favor, tente novamente.",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=error_embed)

    @equipment_group.command(
        name="equipar",
        description="Equipa um item em um personagem"
    )
    async def equip_item(
        self,
        interaction: discord.Interaction,
        nome_personagem: str,
        nome_equipamento: str
    ):
        """
        Equipa um item em um personagem específico
        """
        # Feedback inicial
        embed = discord.Embed(
            title="⚔️ Equipando Item",
            description="Processando...",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

        # Carrega os dados das fichas
        with open('data/fichas.json', 'r', encoding='utf-8') as f:
            fichas = json.load(f)

        # Verifica se o usuário é mestre
        is_mestre = interaction.user.id in UserIDs.MESTRES
        user_id = str(interaction.user.id)
        personagem = None
        owner_id = None

        # Busca o personagem
        if is_mestre:
            # Mestres podem equipar em qualquer personagem
            for uid, user_fichas in fichas.items():
                if nome_personagem in user_fichas:
                    personagem = user_fichas[nome_personagem]
                    owner_id = uid
                    break
        else:
            # Usuários normais só podem equipar em seus próprios personagens
            if user_id in fichas and nome_personagem in fichas[user_id]:
                personagem = fichas[user_id][nome_personagem]
                owner_id = user_id

        if not personagem:
            error_embed = discord.Embed(
                title="❌ Personagem Não Encontrado",
                description=f"Personagem '{nome_personagem}' não encontrado.",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=error_embed)
            return

        # Busca o equipamento
        equipment = self.repository.get_equipment_by_name(nome_equipamento)
        if not equipment:
            error_embed = discord.Embed(
                title="❌ Equipamento Não Encontrado",
                description=f"Não foi encontrado nenhum equipamento com o nome '{nome_equipamento}'.",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=error_embed)
            return

        # Adiciona o equipamento ao personagem
        if nome_equipamento not in personagem["equipamentos"]:
            personagem["equipamentos"].append(nome_equipamento)
            
            # Salva as alterações
            with open('data/fichas.json', 'w', encoding='utf-8') as f:
                json.dump(fichas, f, ensure_ascii=False, indent=4)

            # Cria embed de sucesso
            success_embed = discord.Embed(
                title="✅ Equipamento Adicionado",
                description=f"O item '{nome_equipamento}' foi equipado em '{nome_personagem}' com sucesso!",
                color=discord.Color.green()
            )

            # Adiciona detalhes do equipamento
            success_embed.add_field(
                name="🏷️ Tipo",
                value=equipment.type,
                inline=True
            )
            
            if equipment.damage:
                success_embed.add_field(
                    name="⚔️ Dano",
                    value=equipment.damage,
                    inline=True
                )
            if equipment.armor:
                success_embed.add_field(
                    name="🛡️ Armadura",
                    value=str(equipment.armor),
                    inline=True
                )

            # Adiciona informação de quem equipou
            if is_mestre:
                success_embed.add_field(
                    name="👤 Equipado por",
                    value=f"Mestre {interaction.user.name}",
                    inline=False
                )

            success_embed.set_footer(
                text=f"Equipado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            )

            await interaction.edit_original_response(embed=success_embed)
        else:
            warning_embed = discord.Embed(
                title="⚠️ Equipamento Já Equipado",
                description=f"O personagem '{nome_personagem}' já possui o item '{nome_equipamento}' equipado.",
                color=discord.Color.yellow()
            )
            await interaction.edit_original_response(embed=warning_embed)

    @equip_item.autocomplete('nome_personagem')
    async def autocomplete_personagem_equipar(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        """Autocomplete para nomes de personagens no comando de equipar"""
        # Carrega as fichas
        with open('data/fichas.json', 'r', encoding='utf-8') as f:
            fichas = json.load(f)
        
        choices = []
        user_id = str(interaction.user.id)
        
        # Verifica se o usuário é mestre
        is_mestre = interaction.user.id in UserIDs.MESTRES
        
        if is_mestre:
            # Para mestres, mostra todos os personagens
            for user_fichas in fichas.values():
                for nome_ficha, ficha_data in user_fichas.items():
                    if current.lower() in nome_ficha.lower():
                        choices.append(
                            app_commands.Choice(
                                name=f"{ficha_data['nome']} (Nível {ficha_data['nivel']} {ficha_data['classe']})",
                                value=nome_ficha
                            )
                        )
        else:
            # Para usuários normais, mostra apenas seus personagens
            if user_id in fichas:
                for nome_ficha, ficha_data in fichas[user_id].items():
                    if current.lower() in nome_ficha.lower():
                        choices.append(
                            app_commands.Choice(
                                name=f"{ficha_data['nome']} (Nível {ficha_data['nivel']} {ficha_data['classe']})",
                                value=nome_ficha
                            )
                        )
        
        return choices[:25]  # Limite de 25 opções

    @equip_item.autocomplete('nome_equipamento')
    async def autocomplete_equipamento_equipar(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        """Autocomplete para equipamentos disponíveis"""
        equipments = self.repository.get_all_equipment()
        
        return [
            app_commands.Choice(
                name=f"{eq['name']} ({eq['type']})",
                value=eq['name']
            )
            for eq in equipments
            if current.lower() in eq['name'].lower()
        ][:25]  # Limite de 25 opções

async def setup(bot: commands.Bot):
    await bot.add_cog(EquipmentManagement(bot)) 