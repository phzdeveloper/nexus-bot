import discord
from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="/", intents=intents)

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
bot.run(TOKEN)
