import discord
from discord.ext import commands
from discord import app_commands
import json
import os


INFRACTIONS_FILE = "infractions.json"


def load_infractions():
    if not os.path.exists(INFRACTIONS_FILE):
        return {}
    with open(INFRACTIONS_FILE, "r") as f:
        return json.load(f)


def save_infractions(data):
    with open(INFRACTIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setchannel", description="Define o canal de logs de moderação")
    @app_commands.describe(canal="Canal onde os logs serão enviados")
    @app_commands.default_permissions(administrator=True)
    async def setchannel(self, interaction: discord.Interaction, canal: discord.TextChannel):
        data = load_infractions()
        if "config" not in data:
            data["config"] = {}
        gid = str(interaction.guild_id)
        if gid not in data["config"]:
            data["config"][gid] = {}
        data["config"][gid]["log_channel"] = str(canal.id)
        save_infractions(data)
        await interaction.response.send_message(
            f"✅ Canal de logs definido para {canal.mention}.\nTodas as ações de moderação serão registradas ali.",
            ephemeral=True,
        )

    @app_commands.command(name="setrole", description="Define o cargo de moderador do bot")
    @app_commands.describe(cargo="Cargo que terá acesso aos comandos de moderação")
    @app_commands.default_permissions(administrator=True)
    async def setrole(self, interaction: discord.Interaction, cargo: discord.Role):
        data = load_infractions()
        if "config" not in data:
            data["config"] = {}
        gid = str(interaction.guild_id)
        if gid not in data["config"]:
            data["config"][gid] = {}
        data["config"][gid]["mod_role"] = str(cargo.id)
        save_infractions(data)
        await interaction.response.send_message(
            f"✅ Cargo de moderador definido como {cargo.mention}.\nMembros com esse cargo agora podem usar os comandos de moderação.",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(Config(bot))
