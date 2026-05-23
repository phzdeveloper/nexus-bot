import discord
from discord.ext import commands, tasks
from discord.ui import View, Button
from collections import defaultdict
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import os

# =========================
# CONFIG
# =========================

load_dotenv()

TOKEN = os.getenv("TOKEN")

CANAL_RANKING_ID = 1432155030903066675
CANAL_METAS_ID = 1499492871500337366
CARGO_STAFF_ID = 1432155075215884358

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================
# DATABASE
# =========================

mensagens = defaultdict(int)

ranking_message = None

# =========================
# EVENTOS
# =========================

@bot.event
async def on_ready():

    print(f"[NEXUS] Online como {bot.user}")

    try:
        synced = await bot.tree.sync()

        print(f"{len(synced)} slash commands sincronizados.")

    except Exception as e:
        print(e)

    atualizar_ranking.start()

# =========================
# CONTADOR DE MSGS
# =========================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if any(
        role.id == CARGO_STAFF_ID
        for role in message.author.roles
    ):

        mensagens[message.author.id] += 1

    await bot.process_commands(message)

# =========================
# RANKING
# =========================

@tasks.loop(minutes=1)
async def atualizar_ranking():

    global ranking_message

    canal = bot.get_channel(CANAL_RANKING_ID)

    if not canal:
        return

    ranking = sorted(
        mensagens.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    descricao = ""

    medalhas = [
        "🥇",
        "🥈",
        "🥉",
        "🔹",
        "🔹",
        "🔹",
        "🔹",
        "🔹",
        "🔹",
        "🔹"
    ]

    for i, (user_id, total) in enumerate(ranking):

        membro = canal.guild.get_member(user_id)

        if membro:

            descricao += (
                f"{medalhas[i]} "
                f"{membro.mention} — "
                f"**{total} mensagens**\n"
            )

    embed = discord.Embed(
        title="🏆 Ranking de Mensagens",
        description=(
            "Top 10 membros mais ativos 💬\n\n"
            "📊 **Classificação**\n\n"
            f"{descricao}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "⏱️ Atualiza automaticamente a cada 1 minuto"
        ),
        color=0x5865F2
    )

    embed.set_footer(
        text=f"Hoje às {datetime.now().strftime('%H:%M')}"
    )

    view = RankingView()

    if ranking_message:

        try:

            await ranking_message.edit(
                embed=embed,
                view=view
            )

        except:

            ranking_message = await canal.send(
                embed=embed,
                view=view
            )

    else:

        ranking_message = await canal.send(
            embed=embed,
            view=view
        )

# =========================
# BOTÕES RANKING
# =========================

class RankingView(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Resetar Ranking",
        style=discord.ButtonStyle.danger,
        emoji="🗑️"
    )
    async def reset_button(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "Sem permissão.",
                ephemeral=True
            )

        mensagens.clear()

        await interaction.response.send_message(
            "Ranking resetado.",
            ephemeral=True
        )

# =========================
# PAINEL DE METAS
# =========================

class MetaView(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Ver Meta",
        style=discord.ButtonStyle.primary,
        emoji="📊"
    )
    async def ver_meta(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        await interaction.response.send_message(
            "Sistema de metas em desenvolvimento.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Relatório",
        style=discord.ButtonStyle.secondary,
        emoji="📄"
    )
    async def relatorio(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        ranking = sorted(
            mensagens.items(),
            key=lambda x: x[1],
            reverse=True
        )

        texto = ""

        for user_id, total in ranking:

            membro = interaction.guild.get_member(user_id)

            if membro:

                texto += (
                    f"{membro.name} — "
                    f"{total} mensagens\n"
                )

        embed = discord.Embed(
            title="📄 Relatório Geral",
            description=texto if texto else "Sem dados.",
            color=0x5865F2
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    @discord.ui.button(
        label="Apagar Relatórios",
        style=discord.ButtonStyle.danger,
        emoji="🗑️"
    )
    async def apagar_relatorios(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "Sem permissão.",
                ephemeral=True
            )

        await interaction.channel.purge(limit=100)

        await interaction.response.send_message(
            "Relatórios apagados.",
            ephemeral=True
        )

# =========================
# SLASH COMMANDS
# =========================

@bot.tree.command(
    name="ranking",
    description="Atualiza o ranking"
)
async def ranking(interaction: discord.Interaction):

    await atualizar_ranking()

    await interaction.response.send_message(
        "Ranking atualizado.",
        ephemeral=True
    )


@bot.tree.command(
    name="metas",
    description="Abre o painel de metas"
)
async def metas(interaction: discord.Interaction):

    embed = discord.Embed(
        title="📌 Painel de Metas",
        description=(
            "📋 Ver Meta → veja suas horas e mensagens\n"
            "📄 Relatório → relatório geral dos staffs\n"
            "🗑️ Apagar Relatórios → limpa o canal de relatórios"
        ),
        color=0x5865F2
    )

    embed.set_footer(
        text="Nexus Meta System"
    )

    await interaction.response.send_message(
        embed=embed,
        view=MetaView()
    )

# =========================
# START
# =========================

bot.run(TOKEN)
