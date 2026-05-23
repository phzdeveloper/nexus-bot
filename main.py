import discord
from discord.ext import commands, tasks
from collections import defaultdict
from dotenv import load_dotenv
import os

# =========================
# CONFIG
# =========================

load_dotenv()

TOKEN = os.getenv("TOKEN")

CANAL_RANKING_ID = 1432155030903066675  # ID do canal
CARGO_STAFF_ID = 1432185441750093904    # ID do cargo staff

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

    print(f"Online como {bot.user}")

    atualizar_ranking.start()


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if any(role.id == CARGO_STAFF_ID for role in message.author.roles):

        mensagens[message.author.id] += 1

    await bot.process_commands(message)

# =========================
# RANKING
# =========================

@tasks.loop(minutes=30)
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
            "Atualiza automaticamente a cada 30 minutos"
        ),
        color=0xffd700
    )

    embed.set_footer(
        text="Nexus Ranking System"
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
# BOTÃO RESET
# =========================

class RankingView(discord.ui.View):

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
        button: discord.ui.Button
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
# COMANDO MANUAL
# =========================

@bot.command()
async def ranking(ctx):

    await atualizar_ranking()

    await ctx.send(
        "Ranking atualizado."
    )

# =========================
# START
# =========================

bot.run(TOKEN)
