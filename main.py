import discord
from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime

# =========================
# CONFIG
# =========================

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="/",
    intents=intents
)

# =========================
# EVENTOS
# =========================

@bot.event
async def on_ready():
    print(f"[NEXUS SECURITY] Online como {bot.user}")

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Protegendo o servidor"
        )
    )

    print("Sistema iniciado com sucesso.")


@bot.event
async def on_member_join(member):
    canal = discord.utils.get(member.guild.text_channels, name="logs")

    if canal:
        embed = discord.Embed(
            title="Novo membro detectado",
            description=f"{member.mention} entrou no servidor.",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        await canal.send(embed=embed)


@bot.event
async def on_member_remove(member):
    canal = discord.utils.get(member.guild.text_channels, name="logs")

    if canal:
        embed = discord.Embed(
            title="Membro saiu",
            description=f"{member.name} saiu do servidor.",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )

        await canal.send(embed=embed)

# =========================
# ANTI LINK
# =========================

LINKS_BLOQUEADOS = [
    "discord.gg/",
    "https://",
    "http://"
]

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if not message.author.guild_permissions.administrator:
        for link in LINKS_BLOQUEADOS:
            if link in message.content.lower():

                await message.delete()

                aviso = await message.channel.send(
                    f"{message.author.mention} links não são permitidos."
                )

                await asyncio.sleep(5)

                await aviso.delete()

                return

    await bot.process_commands(message)

# =========================
# COMANDOS
# =========================

@bot.command()
@commands.has_permissions(administrator=True)
async def lock(ctx):

    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        overwrite=overwrite
    )

    embed = discord.Embed(
        title="Canal bloqueado",
        description="O canal foi bloqueado pela staff.",
        color=0xff0000
    )

    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(administrator=True)
async def unlock(ctx):

    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        overwrite=overwrite
    )

    embed = discord.Embed(
        title="Canal desbloqueado",
        description="O canal foi desbloqueado.",
        color=0x00ff00
    )

    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, motivo="Sem motivo"):

    await member.kick(reason=motivo)

    embed = discord.Embed(
        title="Membro expulso",
        description=f"{member.mention} foi expulso.",
        color=0xff0000
    )

    embed.add_field(name="Motivo", value=motivo)

    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, motivo="Sem motivo"):

    await member.ban(reason=motivo)

    embed = discord.Embed(
        title="Membro banido",
        description=f"{member.mention} foi banido.",
        color=0xff0000
    )

    embed.add_field(name="Motivo", value=motivo)

    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, quantidade: int):

    await ctx.channel.purge(limit=quantidade + 1)

    msg = await ctx.send(f"{quantidade} mensagens apagadas.")

    await asyncio.sleep(3)

    await msg.delete()

# =========================
# PAINEL NEXUS DEFENSE
# =========================

class NexusPanel(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Lock",
        style=discord.ButtonStyle.danger
    )
    async def lock_button(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        overwrite = interaction.channel.overwrites_for(
            interaction.guild.default_role
        )

        overwrite.send_messages = False

        await interaction.channel.set_permissions(
            interaction.guild.default_role,
            overwrite=overwrite
        )

        await interaction.response.send_message(
            "Canal bloqueado.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Unlock",
        style=discord.ButtonStyle.success
    )
    async def unlock_button(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        overwrite = interaction.channel.overwrites_for(
            interaction.guild.default_role
        )

        overwrite.send_messages = True

        await interaction.channel.set_permissions(
            interaction.guild.default_role,
            overwrite=overwrite
        )

        await interaction.response.send_message(
            "Canal desbloqueado.",
            ephemeral=True
        )

@bot.command(name="nexusdefense")
@commands.has_permissions(administrator=True)
async def nexus_defense(ctx):

    embed = discord.Embed(
        title="Nexus Defense Dashboard",
        description=(
            "Sistema de segurança do servidor.\n\n"
            "Funções:\n"
            "• Lock de canais\n"
            "• Unlock de canais\n"
            "• Anti-Link\n"
            "• Logs automáticos\n"
            "• Moderação avançada"
        ),
        color=0x2b2d31
    )

    embed.set_footer(text="Nexus Security System")

    await ctx.send(
        embed=embed,
        view=NexusPanel()
    )

# =========================
# ERROS
# =========================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):

        await ctx.send(
            "Você não tem permissão para isso."
        )

    elif isinstance(error, commands.MissingRequiredArgument):

        await ctx.send(
            "Argumentos inválidos."
        )

# =========================
# INICIAR BOT
# =========================

bot.run(TOKEN)
