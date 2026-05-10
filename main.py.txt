# main.py
# Nexus Dev Bot - Discord.py / Pycord

import discord
from discord.ext import commands
from discord.ui import View, Button
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# =========================
# EVENTOS
# =========================

@bot.event
async def on_ready():
    print(f"{bot.user} está online.")

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Estou jogando free fire 🔥"
        )
    )

@bot.event
async def on_member_join(member):
    canal = discord.utils.get(member.guild.text_channels, name="welcome")

    if canal:
        embed = discord.Embed(
            title="Bem-vindo à Nexus Dev",
            description=f"{member.mention}, aproveite a comunidade.",
            color=discord.Color.blurple()
        )

        await canal.send(embed=embed)

# =========================
# MODERAÇÃO
# =========================

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)

    msg = await ctx.send(f"{amount} mensagens apagadas.")
    await msg.delete(delay=3)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Sem motivo"):
    await member.kick(reason=reason)

    embed = discord.Embed(
        title="Usuário Kickado",
        description=f"{member.mention} foi kickado.",
        color=discord.Color.orange()
    )

    embed.add_field(name="Motivo", value=reason)

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Sem motivo"):
    await member.ban(reason=reason)

    embed = discord.Embed(
        title="Usuário Banido",
        description=f"{member.mention} foi banido.",
        color=discord.Color.red()
    )

    embed.add_field(name="Motivo", value=reason)

    await ctx.send(embed=embed)

# =========================
# UTILIDADE
# =========================

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong: {round(bot.latency * 1000)}ms")

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild

    embed = discord.Embed(
        title=guild.name,
        color=discord.Color.green()
    )

    embed.add_field(name="Membros", value=guild.member_count)
    embed.add_field(name="Dono", value=guild.owner)

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author

    embed = discord.Embed(
        title=f"{member}",
        color=discord.Color.blurple()
    )

    embed.add_field(name="ID", value=member.id)
    embed.add_field(
        name="Conta criada",
        value=member.created_at.strftime("%d/%m/%Y")
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    await ctx.send(embed=embed)

# =========================
# PARCERIA
# =========================

@bot.command()
async def parceria(ctx):
    texto = """
**Parceria Nexus Dev**

• Divulgação mútua
• Staff ativa
• Sem spam
• Comunidade organizada
• Respeito entre servidores
"""

    await ctx.send(texto)

# =========================
# TICKETS
# =========================

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Abrir Ticket",
        style=discord.ButtonStyle.green
    )
    async def ticket_button(self, button, interaction):

        guild = interaction.guild

        categoria = discord.utils.get(
            guild.categories,
            name="Tickets"
        )

        canal = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=categoria
        )

        await canal.set_permissions(
            guild.default_role,
            read_messages=False
        )

        await canal.set_permissions(
            interaction.user,
            read_messages=True,
            send_messages=True
        )

        await canal.send(
            f"{interaction.user.mention} suporte iniciado."
        )

        await interaction.response.send_message(
            f"Ticket criado: {canal.mention}",
            ephemeral=True
        )

@bot.command()
async def ticketpanel(ctx):

    embed = discord.Embed(
        title="Sistema de Tickets",
        description="Clique no botão abaixo para abrir um ticket.",
        color=discord.Color.blurple()
    )

    await ctx.send(
        embed=embed,
        view=TicketView()
    )

# =========================
# HELP
# =========================

@bot.command()
async def help(ctx):

    embed = discord.Embed(
        title="Nexus Dev Commands",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="Moderação",
        value="!clear\n!kick\n!ban",
        inline=False
    )

    embed.add_field(
        name="Utilidade",
        value="!ping\n!serverinfo\n!userinfo",
        inline=False
    )

    embed.add_field(
        name="Comunidade",
        value="!parceria\n!ticketpanel",
        inline=False
    )

    await ctx.send(embed=embed)

# =========================
# START
# =========================

bot.run(TOKEN)