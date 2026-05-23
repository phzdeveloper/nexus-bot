import discord
from discord.ext import commands
from discord import app_commands
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
    command_prefix="!",
    intents=intents
)

# =========================
# EVENTOS
# =========================

@bot.event
async def on_ready():

    print(f"[NEXUS SECURITY] Online como {bot.user}")

    try:
        synced = await bot.tree.sync()

        print(f"{len(synced)} slash commands sincronizados.")

    except Exception as e:
        print(e)

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Protegendo o servidor"
        )
    )


@bot.event
async def on_member_join(member):

    canal = discord.utils.get(
        member.guild.text_channels,
        name="logs"
    )

    if canal:

        embed = discord.Embed(
            title="Novo membro detectado",
            description=f"{member.mention} entrou no servidor.",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        await canal.send(embed=embed)


@bot.event
async def on_member_remove(member):

    canal = discord.utils.get(
        member.guild.text_channels,
        name="logs"
    )

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
# DASHBOARD
# =========================

class NexusPanel(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="LOCKDOWN",
        style=discord.ButtonStyle.danger,
        emoji="🔒"
    )
    async def lockdown_button(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "Sem permissão.",
                ephemeral=True
            )

        for channel in interaction.guild.channels:

            try:

                overwrite = channel.overwrites_for(
                    interaction.guild.default_role
                )

                overwrite.send_messages = False

                await channel.set_permissions(
                    interaction.guild.default_role,
                    overwrite=overwrite
                )

            except:
                pass

        await interaction.response.send_message(
            "LOCKDOWN ativado em todos os canais.",
            ephemeral=True
        )

    @discord.ui.button(
        label="UNLOCK",
        style=discord.ButtonStyle.success,
        emoji="🔓"
    )
    async def unlock_button(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "Sem permissão.",
                ephemeral=True
            )

        for channel in interaction.guild.channels:

            try:

                overwrite = channel.overwrites_for(
                    interaction.guild.default_role
                )

                overwrite.send_messages = True

                await channel.set_permissions(
                    interaction.guild.default_role,
                    overwrite=overwrite
                )

            except:
                pass

        await interaction.response.send_message(
            "Todos os canais foram desbloqueados.",
            ephemeral=True
        )

    @discord.ui.button(
        label="CLEAR 100",
        style=discord.ButtonStyle.secondary,
        emoji="🧹"
    )
    async def clear_button(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if not interaction.user.guild_permissions.manage_messages:

            return await interaction.response.send_message(
                "Sem permissão.",
                ephemeral=True
            )

        await interaction.channel.purge(limit=100)

        await interaction.response.send_message(
            "100 mensagens apagadas.",
            ephemeral=True
        )

# =========================
# SLASH COMMANDS
# =========================

@bot.tree.command(
    name="nexusdashboard",
    description="Abre o dashboard de segurança Nexus"
)
async def nexusdashboard(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:

        return await interaction.response.send_message(
            "Sem permissão.",
            ephemeral=True
        )

    embed = discord.Embed(
        title="NEXUS SECURITY DASHBOARD",
        description="""
Painel central de segurança e moderação.

━━━━━━━━━━━━━━━━━━
⚔️ COMANDOS DISPONÍVEIS
━━━━━━━━━━━━━━━━━━

🔒 /lock
Bloqueia o canal atual.

🔓 /unlock
Desbloqueia o canal atual.

🚨 /ban
Bane um membro.

👢 /kick
Expulsa um membro.

🧹 /clear
Limpa mensagens.

🛡️ /nexusdashboard
Abre o painel de segurança.

━━━━━━━━━━━━━━━━━━
⚡ SISTEMAS ATIVOS
━━━━━━━━━━━━━━━━━━

• Anti-Link
• Logs automáticos
• Lockdown global
• Painel interativo
• Proteção administrativa
""",
        color=0x0f111a
    )

    if interaction.guild.icon:
        embed.set_thumbnail(
            url=interaction.guild.icon.url
        )

    embed.set_footer(
        text="Nexus Security • Advanced Protection System"
    )

    await interaction.response.send_message(
        embed=embed,
        view=NexusPanel()
    )


@bot.tree.command(
    name="lock",
    description="Bloqueia o canal atual"
)
async def lock(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:

        return await interaction.response.send_message(
            "Sem permissão.",
            ephemeral=True
        )

    overwrite = interaction.channel.overwrites_for(
        interaction.guild.default_role
    )

    overwrite.send_messages = False

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite
    )

    await interaction.response.send_message(
        "Canal bloqueado."
    )


@bot.tree.command(
    name="unlock",
    description="Desbloqueia o canal atual"
)
async def unlock(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:

        return await interaction.response.send_message(
            "Sem permissão.",
            ephemeral=True
        )

    overwrite = interaction.channel.overwrites_for(
        interaction.guild.default_role
    )

    overwrite.send_messages = True

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite
    )

    await interaction.response.send_message(
        "Canal desbloqueado."
    )


@bot.tree.command(
    name="clear",
    description="Apaga mensagens"
)
@app_commands.describe(
    quantidade="Quantidade de mensagens"
)
async def clear(
    interaction: discord.Interaction,
    quantidade: int
):

    if not interaction.user.guild_permissions.manage_messages:

        return await interaction.response.send_message(
            "Sem permissão.",
            ephemeral=True
        )

    await interaction.channel.purge(limit=quantidade)

    await interaction.response.send_message(
        f"{quantidade} mensagens apagadas.",
        ephemeral=True
    )


@bot.tree.command(
    name="kick",
    description="Expulsa um membro"
)
@app_commands.describe(
    membro="Membro",
    motivo="Motivo da expulsão"
)
async def kick(
    interaction: discord.Interaction,
    membro: discord.Member,
    motivo: str = "Sem motivo"
):

    if not interaction.user.guild_permissions.kick_members:

        return await interaction.response.send_message(
            "Sem permissão.",
            ephemeral=True
        )

    await membro.kick(reason=motivo)

    await interaction.response.send_message(
        f"{membro.mention} foi expulso.\nMotivo: {motivo}"
    )


@bot.tree.command(
    name="ban",
    description="Bane um membro"
)
@app_commands.describe(
    membro="Membro",
    motivo="Motivo do banimento"
)
async def ban(
    interaction: discord.Interaction,
    membro: discord.Member,
    motivo: str = "Sem motivo"
):

    if not interaction.user.guild_permissions.ban_members:

        return await interaction.response.send_message(
            "Sem permissão.",
            ephemeral=True
        )

    await membro.ban(reason=motivo)

    await interaction.response.send_message(
        f"{membro.mention} foi banido.\nMotivo: {motivo}"
    )

# =========================
# INICIAR BOT
# =========================

bot.run(TOKEN)
